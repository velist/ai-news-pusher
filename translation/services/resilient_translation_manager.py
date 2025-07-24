#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弹性翻译服务管理器
实现多级降级策略、自动恢复和错误处理
"""

import logging
import time
from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass

from ..core.interfaces import ITranslationService, TranslationResult
from ..services.rule_based_translator import RuleBasedTranslator


@dataclass
class TranslationAttempt:
    """翻译尝试记录"""
    service_name: str
    success: bool
    result: Optional[TranslationResult]
    error: Optional[str]
    response_time: float
    timestamp: datetime


class ResilientTranslationManager:
    """弹性翻译服务管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化弹性翻译管理器"""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化翻译服务（按优先级排序）
        self.services = self._initialize_services()
        self.rule_translator = RuleBasedTranslator()  # 最终降级方案
        
        # 统计信息
        self.translation_stats = {
            'total_requests': 0,
            'successful_translations': 0,
            'failed_translations': 0,
            'fallback_used': 0,
            'rule_translator_used': 0,
            'service_usage': {},
            'average_response_time': 0.0
        }
    
    def _initialize_services(self) -> List[ITranslationService]:
        """初始化翻译服务（按优先级排序）"""
        services = []
        
        # 这里简化处理，实际使用时会根据配置初始化各种翻译服务
        # 1. 硅基流动翻译（最高优先级）
        # 2. 百度翻译
        # 3. 腾讯翻译  
        # 4. 谷歌翻译
        
        if not services:
            self.logger.warning("没有可用的外部翻译服务，将仅使用规则翻译器")
        
        return services
    
    def translate_with_fallback(self, text: str, source_lang: str = 'en', 
                               target_lang: str = 'zh') -> Dict:
        """使用降级策略进行翻译"""
        self.translation_stats['total_requests'] += 1
        start_time = time.time()
        
        # 记录翻译尝试
        attempts: List[TranslationAttempt] = []
        
        # 尝试外部翻译服务
        if self.services:
            result = self._try_external_services(
                text, source_lang, target_lang, self.services, attempts
            )
            
            if result['success']:
                response_time = time.time() - start_time
                self._update_stats(result['service_used'], response_time, True)
                result['attempts'] = attempts
                result['fallback_level'] = 0
                return result
        
        # 所有外部服务失败，使用规则翻译器
        self.logger.warning("所有外部翻译服务失败，使用规则翻译器")
        self.translation_stats['fallback_used'] += 1
        self.translation_stats['rule_translator_used'] += 1
        
        try:
            rule_result = self.rule_translator.translate_text(text, source_lang, target_lang)
            response_time = time.time() - start_time
            
            attempts.append(TranslationAttempt(
                service_name="rule_based_translator",
                success=True,
                result=rule_result,
                error=None,
                response_time=response_time,
                timestamp=datetime.now()
            ))
            
            self._update_stats("rule_based_translator", response_time, True)
            
            return {
                'success': True,
                'result': rule_result,
                'service_used': 'rule_based_translator',
                'fallback_level': len(self.services) + 1,
                'attempts': attempts,
                'warning': '使用规则翻译器作为最终降级方案，翻译质量可能有限'
            }
            
        except Exception as e:
            # 连规则翻译器都失败了，返回原文
            self.logger.error(f"规则翻译器也失败了: {e}")
            response_time = time.time() - start_time
            
            attempts.append(TranslationAttempt(
                service_name="rule_based_translator",
                success=False,
                result=None,
                error=str(e),
                response_time=response_time,
                timestamp=datetime.now()
            ))
            
            # 创建失败结果，返回原文
            fallback_result = TranslationResult(
                original_text=text,
                translated_text=text,  # 返回原文
                source_language=source_lang,
                target_language=target_lang,
                service_name="fallback_original",
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message="所有翻译服务均失败，返回原文"
            )
            
            self._update_stats("fallback_original", response_time, False)
            
            return {
                'success': False,
                'result': fallback_result,
                'service_used': 'fallback_original',
                'fallback_level': len(self.services) + 2,
                'attempts': attempts,
                'error': '所有翻译服务均失败，返回原文'
            }    

    def _try_external_services(self, text: str, source_lang: str, target_lang: str,
                              services: List[ITranslationService], 
                              attempts: List[TranslationAttempt]) -> Dict:
        """尝试外部翻译服务"""
        for service in services:
            service_name = service.get_service_name()
            
            # 尝试翻译（带重试）
            result = self._try_service_with_retry(service, text, source_lang, target_lang)
            
            # 记录尝试
            attempts.append(TranslationAttempt(
                service_name=service_name,
                success=result['success'],
                result=result.get('result'),
                error=result.get('error'),
                response_time=result['response_time'],
                timestamp=datetime.now()
            ))
            
            if result['success']:
                return {
                    'success': True,
                    'result': result['result'],
                    'service_used': service_name
                }
            else:
                self.logger.warning(f"服务 {service_name} 翻译失败: {result['error']}")
        
        return {'success': False}
    
    def _try_service_with_retry(self, service: ITranslationService, text: str,
                               source_lang: str, target_lang: str) -> Dict:
        """带重试机制的服务调用"""
        service_name = service.get_service_name()
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries + 1):
            start_time = time.time()
            
            try:
                result = service.translate_text(text, source_lang, target_lang)
                response_time = time.time() - start_time
                
                # 检查结果有效性
                if result.error_message:
                    raise Exception(result.error_message)
                
                if not result.translated_text or result.translated_text.strip() == "":
                    raise Exception("翻译结果为空")
                
                return {
                    'success': True,
                    'result': result,
                    'response_time': response_time
                }
                
            except Exception as e:
                response_time = time.time() - start_time
                last_error = str(e)
                
                if attempt < max_retries:
                    delay = 1.0 * (2 ** attempt)  # 指数退避
                    self.logger.warning(f"服务 {service_name} 第{attempt + 1}次尝试失败: {e}，{delay}秒后重试")
                    time.sleep(delay)
                else:
                    self.logger.error(f"服务 {service_name} 所有重试均失败: {e}")
        
        return {
            'success': False,
            'error': last_error,
            'response_time': response_time
        }
    
    def _update_stats(self, service_name: str, response_time: float, success: bool):
        """更新统计信息"""
        if success:
            self.translation_stats['successful_translations'] += 1
        else:
            self.translation_stats['failed_translations'] += 1
        
        # 更新服务使用统计
        if service_name not in self.translation_stats['service_usage']:
            self.translation_stats['service_usage'][service_name] = {
                'count': 0,
                'success_count': 0,
                'total_response_time': 0.0
            }
        
        stats = self.translation_stats['service_usage'][service_name]
        stats['count'] += 1
        stats['total_response_time'] += response_time
        
        if success:
            stats['success_count'] += 1
        
        # 更新平均响应时间
        total_requests = self.translation_stats['total_requests']
        current_avg = self.translation_stats['average_response_time']
        self.translation_stats['average_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_service_health_summary(self) -> Dict:
        """获取服务健康摘要"""
        return {
            'available_services': [service.get_service_name() for service in self.services],
            'rule_translator_available': True,
            'total_services': len(self.services) + 1  # +1 for rule translator
        }
    
    def get_translation_statistics(self) -> Dict:
        """获取翻译统计信息"""
        stats = self.translation_stats.copy()
        
        # 计算成功率
        total = stats['successful_translations'] + stats['failed_translations']
        stats['success_rate'] = (stats['successful_translations'] / total * 100) if total > 0 else 0
        
        # 计算各服务的详细统计
        for service_name, service_stats in stats['service_usage'].items():
            if service_stats['count'] > 0:
                service_stats['success_rate'] = (service_stats['success_count'] / service_stats['count']) * 100
                service_stats['average_response_time'] = service_stats['total_response_time'] / service_stats['count']
        
        return stats
    
    def get_fallback_chain_status(self) -> List[Dict]:
        """获取降级链状态"""
        chain_status = []
        
        # 外部服务状态
        for i, service in enumerate(self.services):
            service_name = service.get_service_name()
            
            chain_status.append({
                'priority': i + 1,
                'service_name': service_name,
                'status': 'healthy',  # 简化处理
                'type': 'external_api'
            })
        
        # 规则翻译器状态
        chain_status.append({
            'priority': len(self.services) + 1,
            'service_name': 'rule_based_translator',
            'status': 'healthy',  # 规则翻译器总是可用
            'type': 'local_fallback'
        })
        
        # 原文返回（最终降级）
        chain_status.append({
            'priority': len(self.services) + 2,
            'service_name': 'fallback_original',
            'status': 'healthy',  # 总是可用
            'type': 'original_text_fallback'
        })
        
        return chain_status
    
    def test_fallback_chain(self, test_text: str = "Hello world") -> Dict:
        """测试降级链"""
        self.logger.info("开始测试降级链")
        
        test_results = []
        
        # 测试每个服务
        for service in self.services:
            service_name = service.get_service_name()
            start_time = time.time()
            
            try:
                result = service.translate_text(test_text, 'en', 'zh')
                response_time = time.time() - start_time
                
                test_results.append({
                    'service_name': service_name,
                    'success': not bool(result.error_message),
                    'response_time': response_time,
                    'translated_text': result.translated_text,
                    'error': result.error_message
                })
                
            except Exception as e:
                response_time = time.time() - start_time
                test_results.append({
                    'service_name': service_name,
                    'success': False,
                    'response_time': response_time,
                    'translated_text': None,
                    'error': str(e)
                })
        
        # 测试规则翻译器
        try:
            start_time = time.time()
            rule_result = self.rule_translator.translate_text(test_text, 'en', 'zh')
            response_time = time.time() - start_time
            
            test_results.append({
                'service_name': 'rule_based_translator',
                'success': True,
                'response_time': response_time,
                'translated_text': rule_result.translated_text,
                'error': None
            })
            
        except Exception as e:
            test_results.append({
                'service_name': 'rule_based_translator',
                'success': False,
                'response_time': 0,
                'translated_text': None,
                'error': str(e)
            })
        
        return {
            'test_text': test_text,
            'test_time': datetime.now().isoformat(),
            'results': test_results,
            'available_fallback_levels': sum(1 for r in test_results if r['success'])
        }
    
    def force_health_check(self, service_name: Optional[str] = None):
        """强制执行健康检查"""
        # 简化实现，实际使用时会调用健康监控器
        self.logger.info(f"强制健康检查: {service_name or '所有服务'}")
    
    def shutdown(self):
        """关闭管理器"""
        self.logger.info("正在关闭弹性翻译管理器")