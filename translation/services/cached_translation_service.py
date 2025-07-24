#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带缓存的翻译服务 - 集成智能缓存系统的完整翻译解决方案
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid

from translation.core.interfaces import TranslationResult
from translation.core.cache_system import SmartTranslationCache
from translation.services.enhanced_translation_manager import EnhancedTranslationManager


class CachedTranslationService:
    """带缓存的翻译服务"""
    
    def __init__(self, translation_config: Optional[Dict] = None, 
                 cache_config: Optional[Dict] = None):
        """
        初始化带缓存的翻译服务
        
        Args:
            translation_config: 翻译服务配置
            cache_config: 缓存系统配置
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化翻译管理器
        self.translation_manager = EnhancedTranslationManager(translation_config)
        
        # 初始化缓存系统
        self.cache = SmartTranslationCache(cache_config)
        
        # 性能统计
        self.performance_stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'translation_requests': 0,
            'average_response_time': 0.0
        }
    
    def translate(self, text: str, source_lang: str = 'en', target_lang: str = 'zh',
                 force_refresh: bool = False, use_quality_optimization: bool = True) -> Dict:
        """
        执行翻译（带缓存）
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            force_refresh: 是否强制刷新缓存
            use_quality_optimization: 是否使用质量优化
            
        Returns:
            Dict: 翻译结果
        """
        start_time = datetime.now()
        self.performance_stats['total_requests'] += 1
        
        try:
            # 1. 检查缓存（除非强制刷新）
            cached_result = None
            if not force_refresh:
                cached_result = self.cache.get_cached_translation(text, source_lang, target_lang)
            
            if cached_result:
                # 缓存命中
                self.performance_stats['cache_hits'] += 1
                
                response_time = (datetime.now() - start_time).total_seconds()
                self._update_average_response_time(response_time)
                
                return {
                    'success': True,
                    'translation_result': cached_result.translation_result,
                    'quality_score': cached_result.translation_result.quality_score,
                    'source': 'cache',
                    'cache_info': {
                        'usage_count': cached_result.usage_count,
                        'created_at': cached_result.created_at.isoformat(),
                        'expires_at': cached_result.expires_at.isoformat()
                    },
                    'response_time_ms': response_time * 1000,
                    'request_id': str(uuid.uuid4())
                }
            
            # 2. 缓存未命中，执行翻译
            self.performance_stats['cache_misses'] += 1
            self.performance_stats['translation_requests'] += 1
            
            if use_quality_optimization:
                translation_result = self.translation_manager.optimize_translation_quality(
                    text, source_lang, target_lang
                )
            else:
                translation_result = self.translation_manager.translate_with_quality_assessment(
                    text, source_lang, target_lang
                )
            
            if not translation_result['success']:
                return translation_result
            
            best_translation = translation_result['best_translation']
            
            # 3. 缓存翻译结果
            cache_success = self.cache.cache_translation(text, best_translation, source_lang, target_lang)
            
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_average_response_time(response_time)
            
            return {
                'success': True,
                'translation_result': best_translation,
                'quality_score': best_translation.quality_score,
                'source': 'translation_service',
                'service_info': {
                    'service_name': best_translation.service_name,
                    'confidence_score': best_translation.confidence_score,
                    'all_services_used': len(translation_result.get('all_translations', []))
                },
                'cache_info': {
                    'cached': cache_success,
                    'cache_key': self.cache._generate_cache_key(text, source_lang, target_lang)
                },
                'optimization_info': translation_result.get('optimization_info', {}),
                'response_time_ms': response_time * 1000,
                'request_id': str(uuid.uuid4())
            }
        
        except Exception as e:
            self.logger.error(f"翻译请求失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'request_id': str(uuid.uuid4())
            }
    
    def batch_translate(self, texts: List[str], source_lang: str = 'en', 
                       target_lang: str = 'zh', use_cache: bool = True) -> List[Dict]:
        """
        批量翻译
        
        Args:
            texts: 要翻译的文本列表
            source_lang: 源语言
            target_lang: 目标语言
            use_cache: 是否使用缓存
            
        Returns:
            List[Dict]: 翻译结果列表
        """
        results = []
        
        for text in texts:
            result = self.translate(
                text, source_lang, target_lang, 
                force_refresh=not use_cache
            )
            results.append(result)
        
        return results
    
    def get_performance_statistics(self) -> Dict:
        """获取性能统计信息"""
        cache_stats = self.cache.get_cache_statistics()
        translation_stats = self.translation_manager.get_translation_statistics()
        
        return {
            'service_performance': self.performance_stats,
            'cache_performance': cache_stats,
            'translation_performance': translation_stats,
            'overall_metrics': {
                'cache_hit_rate': (self.performance_stats['cache_hits'] / 
                                 max(self.performance_stats['total_requests'], 1)),
                'translation_efficiency': (self.performance_stats['cache_hits'] / 
                                          max(self.performance_stats['total_requests'], 1)),
                'average_response_time_ms': self.performance_stats['average_response_time'] * 1000
            }
        }
    
    def optimize_performance(self) -> Dict:
        """优化性能"""
        optimization_results = {
            'cache_optimization': self.cache.optimize_cache_performance(),
            'recommendations': []
        }
        
        # 分析性能并提供建议
        stats = self.get_performance_statistics()
        cache_hit_rate = stats['overall_metrics']['cache_hit_rate']
        
        if cache_hit_rate < 0.3:
            optimization_results['recommendations'].append(
                "缓存命中率较低，建议检查缓存配置或增加缓存容量"
            )
        
        if self.performance_stats['average_response_time'] > 2.0:
            optimization_results['recommendations'].append(
                "平均响应时间较长，建议优化翻译服务配置"
            )
        
        return optimization_results
    
    def clear_cache(self, expired_only: bool = True) -> Dict:
        """
        清理缓存
        
        Args:
            expired_only: 是否只清理过期缓存
            
        Returns:
            Dict: 清理结果
        """
        if expired_only:
            cleared_count = self.cache.clear_expired_cache()
            return {
                'success': True,
                'cleared_items': cleared_count,
                'type': 'expired_only'
            }
        else:
            # 清理所有缓存
            self.cache.memory_cache.clear()
            self.cache.file_cache.clear()
            # 注意：这里不清理数据库缓存，因为它是持久化存储
            
            return {
                'success': True,
                'type': 'memory_and_file_cache_cleared'
            }
    
    def submit_feedback(self, request_id: str, original_text: str, 
                       translated_text: str, service_name: str,
                       feedback_type: str, rating: Optional[float] = None,
                       corrected_text: Optional[str] = None,
                       comments: Optional[str] = None,
                       user_id: Optional[str] = None) -> bool:
        """
        提交用户反馈
        
        Args:
            request_id: 请求ID
            original_text: 原文
            translated_text: 翻译文本
            service_name: 服务名称
            feedback_type: 反馈类型
            rating: 评分
            corrected_text: 纠正的翻译
            comments: 评论
            user_id: 用户ID
            
        Returns:
            bool: 是否成功提交
        """
        return self.translation_manager.submit_user_feedback(
            request_id, original_text, translated_text, service_name,
            feedback_type, rating, corrected_text, comments, user_id
        )
    
    def get_service_recommendations(self) -> Dict:
        """获取服务推荐"""
        return self.translation_manager.get_service_recommendations()
    
    def analyze_service_performance(self, service_name: str) -> Dict:
        """分析服务性能"""
        return self.translation_manager.analyze_service_performance(service_name)
    
    def _update_average_response_time(self, new_time: float):
        """更新平均响应时间"""
        current_avg = self.performance_stats['average_response_time']
        total_requests = self.performance_stats['total_requests']
        
        if total_requests == 1:
            self.performance_stats['average_response_time'] = new_time
        else:
            # 计算新的平均值
            total_time = current_avg * (total_requests - 1) + new_time
            self.performance_stats['average_response_time'] = total_time / total_requests
    
    def health_check(self) -> Dict:
        """健康检查"""
        try:
            # 检查翻译服务
            translation_stats = self.translation_manager.get_translation_statistics()
            available_services = translation_stats['available_services']
            
            # 检查缓存系统
            cache_stats = self.cache.get_cache_statistics()
            
            # 执行简单的翻译测试
            test_result = self.translate("Hello", force_refresh=False)
            
            return {
                'status': 'healthy',
                'available_services': available_services,
                'service_count': len(available_services),
                'cache_hit_rate': cache_stats['hit_rate'],
                'test_translation_success': test_result['success'],
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }