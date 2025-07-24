#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务比较器 - 用于比较和选择最佳翻译结果
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime

from translation.core.interfaces import ITranslationService, TranslationResult, QualityScore
from translation.core.quality_assessor import TranslationQualityAssessor


@dataclass
class TranslationComparison:
    """翻译比较结果"""
    original_text: str
    best_translation: TranslationResult
    all_results: List[TranslationResult]
    quality_scores: List[QualityScore]
    comparison_metadata: Dict[str, any]


class TranslationComparator:
    """翻译服务比较器"""
    
    def __init__(self, services: List[ITranslationService], quality_assessor: Optional[TranslationQualityAssessor] = None):
        """
        初始化翻译比较器
        
        Args:
            services: 翻译服务列表
            quality_assessor: 质量评估器，如果为None则使用默认评估器
        """
        self.services = services
        self.quality_assessor = quality_assessor or TranslationQualityAssessor()
        self.logger = logging.getLogger(__name__)
        
    def compare_translations(self, text: str, source_lang: str = 'en', target_lang: str = 'zh', 
                           timeout: int = 30) -> TranslationComparison:
        """
        比较多个翻译服务的结果
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言
            target_lang: 目标语言
            timeout: 超时时间（秒）
            
        Returns:
            TranslationComparison: 比较结果
        """
        # 并行调用所有翻译服务
        translation_results = self._get_all_translations(text, source_lang, target_lang, timeout)
        
        if not translation_results:
            raise RuntimeError("所有翻译服务都失败了")
        
        # 提取翻译文本进行质量评估
        translations = [result.translated_text for result in translation_results]
        quality_scores = self.quality_assessor.compare_translations(text, translations)
        
        # 更新翻译结果的质量评分
        for i, result in enumerate(translation_results):
            if i < len(quality_scores):
                result.quality_score = quality_scores[i].overall_score
        
        # 选择最佳翻译
        best_translation = self._select_best_translation(translation_results, quality_scores)
        
        # 生成比较元数据
        metadata = self._generate_comparison_metadata(translation_results, quality_scores)
        
        return TranslationComparison(
            original_text=text,
            best_translation=best_translation,
            all_results=translation_results,
            quality_scores=quality_scores,
            comparison_metadata=metadata
        )
    
    def _get_all_translations(self, text: str, source_lang: str, target_lang: str, 
                            timeout: int) -> List[TranslationResult]:
        """并行获取所有翻译服务的结果"""
        results = []
        
        with ThreadPoolExecutor(max_workers=len(self.services)) as executor:
            # 提交所有翻译任务
            future_to_service = {
                executor.submit(self._safe_translate, service, text, source_lang, target_lang): service
                for service in self.services
            }
            
            # 收集结果
            for future in as_completed(future_to_service, timeout=timeout):
                service = future_to_service[future]
                try:
                    result = future.result()
                    if result and result.translated_text:
                        results.append(result)
                        self.logger.info(f"翻译服务 {service.get_service_name()} 成功返回结果")
                    else:
                        self.logger.warning(f"翻译服务 {service.get_service_name()} 返回空结果")
                except Exception as e:
                    self.logger.error(f"翻译服务 {service.get_service_name()} 失败: {e}")
        
        return results
    
    def _safe_translate(self, service: ITranslationService, text: str, 
                       source_lang: str, target_lang: str) -> Optional[TranslationResult]:
        """安全地调用翻译服务"""
        try:
            return service.translate_text(text, source_lang, target_lang)
        except Exception as e:
            self.logger.error(f"翻译服务 {service.get_service_name()} 调用失败: {e}")
            return None
    
    def _select_best_translation(self, results: List[TranslationResult], 
                               scores: List[QualityScore]) -> TranslationResult:
        """选择最佳翻译结果"""
        if not results:
            raise ValueError("没有可用的翻译结果")
        
        # 如果只有一个结果，直接返回
        if len(results) == 1:
            return results[0]
        
        # 根据质量评分和服务可靠性选择最佳结果
        best_result = results[0]
        best_score = 0.0
        
        for i, result in enumerate(results):
            # 综合评分：质量评分 + 服务可靠性加权
            service_weight = self._get_service_weight(result.service_name)
            quality_score = scores[i].overall_score if i < len(scores) else 0.5
            
            combined_score = quality_score * 0.8 + service_weight * 0.2
            
            if combined_score > best_score:
                best_score = combined_score
                best_result = result
        
        return best_result
    
    def _get_service_weight(self, service_name: str) -> float:
        """获取服务权重（基于可靠性和质量）"""
        weights = {
            'siliconflow': 0.9,  # 高质量AI翻译
            'baidu': 0.8,        # 稳定的商业服务
            'tencent': 0.75,     # 稳定的商业服务
            'google': 0.85,      # 高质量但可能不稳定
        }
        return weights.get(service_name.lower(), 0.5)
    
    def _generate_comparison_metadata(self, results: List[TranslationResult], 
                                    scores: List[QualityScore]) -> Dict[str, any]:
        """生成比较元数据"""
        metadata = {
            'total_services': len(self.services),
            'successful_services': len(results),
            'comparison_timestamp': datetime.now().isoformat(),
            'service_results': {}
        }
        
        for i, result in enumerate(results):
            service_data = {
                'service_name': result.service_name,
                'confidence_score': result.confidence_score,
                'quality_score': scores[i].overall_score if i < len(scores) else None,
                'response_time': (result.timestamp - datetime.now()).total_seconds() if result.timestamp else None
            }
            metadata['service_results'][result.service_name] = service_data
        
        # 计算平均质量评分
        if scores:
            metadata['average_quality_score'] = sum(score.overall_score for score in scores) / len(scores)
            metadata['best_quality_score'] = max(score.overall_score for score in scores)
            metadata['worst_quality_score'] = min(score.overall_score for score in scores)
        
        return metadata
    
    def get_service_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """获取服务性能统计"""
        stats = {}
        
        for service in self.services:
            service_name = service.get_service_name()
            stats[service_name] = {
                'status': service.get_service_status().value,
                'weight': self._get_service_weight(service_name)
            }
        
        return stats


class AdaptiveTranslationSelector:
    """自适应翻译选择器 - 基于历史表现动态调整服务选择"""
    
    def __init__(self):
        self.service_stats = {}  # 服务统计信息
        self.quality_threshold = 0.8  # 质量阈值
        
    def update_service_performance(self, service_name: str, quality_score: float, 
                                 response_time: float, success: bool):
        """更新服务性能统计"""
        if service_name not in self.service_stats:
            self.service_stats[service_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_quality_score': 0.0,
                'total_response_time': 0.0,
                'last_updated': datetime.now()
            }
        
        stats = self.service_stats[service_name]
        stats['total_requests'] += 1
        
        if success:
            stats['successful_requests'] += 1
            stats['total_quality_score'] += quality_score
            stats['total_response_time'] += response_time
        
        stats['last_updated'] = datetime.now()
    
    def get_recommended_services(self, max_services: int = 3) -> List[str]:
        """获取推荐的翻译服务列表"""
        if not self.service_stats:
            # 如果没有统计数据，返回默认顺序
            return ['siliconflow', 'baidu', 'google']
        
        # 计算每个服务的综合评分
        service_scores = []
        
        for service_name, stats in self.service_stats.items():
            if stats['total_requests'] == 0:
                continue
                
            success_rate = stats['successful_requests'] / stats['total_requests']
            avg_quality = (stats['total_quality_score'] / stats['successful_requests'] 
                          if stats['successful_requests'] > 0 else 0)
            avg_response_time = (stats['total_response_time'] / stats['successful_requests'] 
                               if stats['successful_requests'] > 0 else float('inf'))
            
            # 综合评分：成功率 * 0.4 + 质量 * 0.4 + 响应时间 * 0.2
            response_score = 1.0 / (1.0 + avg_response_time) if avg_response_time != float('inf') else 0
            combined_score = success_rate * 0.4 + avg_quality * 0.4 + response_score * 0.2
            
            service_scores.append((service_name, combined_score))
        
        # 按评分排序并返回前N个
        service_scores.sort(key=lambda x: x[1], reverse=True)
        return [service[0] for service in service_scores[:max_services]]
    
    def should_use_single_service(self, service_name: str) -> bool:
        """判断是否应该只使用单个服务（基于历史表现）"""
        if service_name not in self.service_stats:
            return False
        
        stats = self.service_stats[service_name]
        if stats['total_requests'] < 10:  # 样本太少
            return False
        
        success_rate = stats['successful_requests'] / stats['total_requests']
        avg_quality = (stats['total_quality_score'] / stats['successful_requests'] 
                      if stats['successful_requests'] > 0 else 0)
        
        # 如果成功率和质量都很高，可以只使用这个服务
        return success_rate >= 0.95 and avg_quality >= self.quality_threshold