#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的翻译服务管理器 - 集成质量评估和优化功能
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import uuid

from translation.core.interfaces import ITranslationService, TranslationResult
from translation.core.quality_assessor import TranslationQualityAssessor
from translation.core.translation_comparator import TranslationComparator, AdaptiveTranslationSelector
from translation.core.feedback_system import TranslationFeedbackSystem, UserFeedback, FeedbackType

# 导入现有的翻译服务
from translation.services.baidu_translator import BaiduTranslator
from translation.services.google_translator import GoogleTranslator
from translation.services.tencent_translator import TencentTranslator
from translation.services.siliconflow_translator import SiliconFlowTranslator


class EnhancedTranslationManager:
    """增强的翻译服务管理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化增强翻译管理器
        
        Args:
            config: 配置字典，包含各服务的API密钥等
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化翻译服务
        self.services = self._initialize_services()
        
        # 初始化质量评估和优化组件
        self.quality_assessor = TranslationQualityAssessor()
        self.comparator = TranslationComparator(self.services, self.quality_assessor)
        self.adaptive_selector = AdaptiveTranslationSelector()
        self.feedback_system = TranslationFeedbackSystem()
        
        # 统计信息
        self.translation_stats = {
            'total_translations': 0,
            'successful_translations': 0,
            'failed_translations': 0,
            'average_quality_score': 0.0
        }
    
    def _initialize_services(self) -> List[ITranslationService]:
        """初始化翻译服务列表"""
        services = []
        
        try:
            # 百度翻译
            if 'baidu' in self.config:
                baidu_service = BaiduTranslator(
                    app_id=self.config['baidu'].get('app_id'),
                    secret_key=self.config['baidu'].get('secret_key')
                )
                services.append(baidu_service)
                self.logger.info("百度翻译服务已初始化")
        except Exception as e:
            self.logger.warning(f"百度翻译服务初始化失败: {e}")
        
        try:
            # 谷歌翻译
            if 'google' in self.config:
                google_service = GoogleTranslator(
                    api_key=self.config['google'].get('api_key')
                )
                services.append(google_service)
                self.logger.info("谷歌翻译服务已初始化")
        except Exception as e:
            self.logger.warning(f"谷歌翻译服务初始化失败: {e}")
        
        try:
            # 腾讯翻译
            if 'tencent' in self.config:
                tencent_service = TencentTranslator(
                    secret_id=self.config['tencent'].get('secret_id'),
                    secret_key=self.config['tencent'].get('secret_key')
                )
                services.append(tencent_service)
                self.logger.info("腾讯翻译服务已初始化")
        except Exception as e:
            self.logger.warning(f"腾讯翻译服务初始化失败: {e}")
        
        try:
            # 硅基流动翻译
            if 'siliconflow' in self.config:
                siliconflow_service = SiliconFlowTranslator(
                    api_key=self.config['siliconflow'].get('api_key')
                )
                services.append(siliconflow_service)
                self.logger.info("硅基流动翻译服务已初始化")
        except Exception as e:
            self.logger.warning(f"硅基流动翻译服务初始化失败: {e}")
        
        if not services:
            self.logger.warning("没有可用的翻译服务")
        
        return services
    
    def translate_with_quality_assessment(self, text: str, source_lang: str = 'en', 
                                        target_lang: str = 'zh', 
                                        use_comparison: bool = True) -> Dict:
        """
        执行带质量评估的翻译
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            use_comparison: 是否使用多服务比较
            
        Returns:
            Dict: 包含翻译结果和质量评估的字典
        """
        self.translation_stats['total_translations'] += 1
        
        try:
            if use_comparison and len(self.services) > 1:
                # 使用多服务比较
                comparison = self.comparator.compare_translations(text, source_lang, target_lang)
                
                # 更新自适应选择器的统计信息
                for result in comparison.all_results:
                    quality_score = result.quality_score or 0.5
                    response_time = 1.0  # 简化的响应时间
                    self.adaptive_selector.update_service_performance(
                        result.service_name, quality_score, response_time, True
                    )
                
                self.translation_stats['successful_translations'] += 1
                self._update_average_quality_score(comparison.best_translation.quality_score or 0.5)
                
                return {
                    'success': True,
                    'best_translation': comparison.best_translation,
                    'all_translations': comparison.all_results,
                    'quality_scores': comparison.quality_scores,
                    'comparison_metadata': comparison.comparison_metadata,
                    'translation_id': str(uuid.uuid4())
                }
            
            else:
                # 使用单个服务（推荐的最佳服务）
                recommended_services = self.adaptive_selector.get_recommended_services(max_services=1)
                service_name = recommended_services[0] if recommended_services else self.services[0].get_service_name()
                
                service = next((s for s in self.services if s.get_service_name() == service_name), self.services[0])
                result = service.translate_text(text, source_lang, target_lang)
                
                # 评估质量
                quality_score = self.quality_assessor.assess_translation(text, result.translated_text)
                result.quality_score = quality_score.overall_score
                
                # 更新统计信息
                self.adaptive_selector.update_service_performance(
                    service_name, quality_score.overall_score, 1.0, True
                )
                
                self.translation_stats['successful_translations'] += 1
                self._update_average_quality_score(quality_score.overall_score)
                
                return {
                    'success': True,
                    'best_translation': result,
                    'all_translations': [result],
                    'quality_scores': [quality_score],
                    'comparison_metadata': {'single_service_used': service_name},
                    'translation_id': str(uuid.uuid4())
                }
        
        except Exception as e:
            self.logger.error(f"翻译失败: {e}")
            self.translation_stats['failed_translations'] += 1
            
            return {
                'success': False,
                'error': str(e),
                'translation_id': str(uuid.uuid4())
            }
    
    def submit_user_feedback(self, translation_id: str, original_text: str, 
                           translated_text: str, service_name: str,
                           feedback_type: str, rating: Optional[float] = None,
                           corrected_text: Optional[str] = None,
                           comments: Optional[str] = None,
                           user_id: Optional[str] = None) -> bool:
        """
        提交用户反馈
        
        Args:
            translation_id: 翻译ID
            original_text: 原文
            translated_text: 翻译文本
            service_name: 服务名称
            feedback_type: 反馈类型
            rating: 评分（1-5）
            corrected_text: 纠正的翻译
            comments: 评论
            user_id: 用户ID
            
        Returns:
            bool: 是否成功提交
        """
        try:
            feedback = UserFeedback(
                feedback_id=f"{translation_id}_{datetime.now().timestamp()}",
                original_text=original_text,
                translated_text=translated_text,
                service_name=service_name,
                feedback_type=FeedbackType(feedback_type),
                rating=rating,
                corrected_text=corrected_text,
                comments=comments,
                user_id=user_id
            )
            
            return self.feedback_system.submit_feedback(feedback)
        
        except Exception as e:
            self.logger.error(f"提交反馈失败: {e}")
            return False
    
    def get_service_recommendations(self) -> Dict[str, any]:
        """获取服务推荐信息"""
        recommended_services = self.adaptive_selector.get_recommended_services()
        service_stats = self.comparator.get_service_performance_stats()
        
        return {
            'recommended_services': recommended_services,
            'service_performance': service_stats,
            'should_use_comparison': len(self.services) > 1 and not any(
                self.adaptive_selector.should_use_single_service(service)
                for service in recommended_services[:1]
            )
        }
    
    def get_translation_statistics(self) -> Dict[str, any]:
        """获取翻译统计信息"""
        return {
            **self.translation_stats,
            'available_services': [service.get_service_name() for service in self.services],
            'service_count': len(self.services)
        }
    
    def get_service_feedback_summary(self, service_name: Optional[str] = None) -> Dict:
        """获取服务反馈摘要"""
        if service_name:
            return self.feedback_system.get_service_feedback_summary(service_name)
        else:
            return self.feedback_system.get_all_services_summary()
    
    def analyze_service_performance(self, service_name: str) -> Dict:
        """分析服务性能"""
        analysis = self.feedback_system.analyze_service_performance(service_name)
        return {
            'service_name': analysis.service_name,
            'total_feedback_count': analysis.total_feedback_count,
            'average_rating': analysis.average_rating,
            'common_issues': analysis.common_issues,
            'improvement_suggestions': analysis.improvement_suggestions,
            'quality_trend': analysis.quality_trend
        }
    
    def _update_average_quality_score(self, new_score: float):
        """更新平均质量评分"""
        current_avg = self.translation_stats['average_quality_score']
        successful_count = self.translation_stats['successful_translations']
        
        if successful_count == 1:
            self.translation_stats['average_quality_score'] = new_score
        else:
            # 计算新的平均值
            total_score = current_avg * (successful_count - 1) + new_score
            self.translation_stats['average_quality_score'] = total_score / successful_count
    
    def optimize_translation_quality(self, text: str, source_lang: str = 'en', 
                                   target_lang: str = 'zh') -> Dict:
        """
        优化翻译质量 - 使用最佳策略进行翻译
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            
        Returns:
            Dict: 优化后的翻译结果
        """
        # 获取推荐策略
        recommendations = self.get_service_recommendations()
        
        # 根据推荐决定使用单服务还是多服务比较
        use_comparison = recommendations['should_use_comparison']
        
        # 执行翻译
        result = self.translate_with_quality_assessment(
            text, source_lang, target_lang, use_comparison
        )
        
        # 添加优化信息
        if result['success']:
            result['optimization_info'] = {
                'strategy_used': 'multi_service_comparison' if use_comparison else 'single_best_service',
                'recommended_services': recommendations['recommended_services'],
                'quality_optimized': True
            }
        
        return result