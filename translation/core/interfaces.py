#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务核心接口定义
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ServiceStatus(Enum):
    """服务状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class TranslationResult:
    """翻译结果数据模型"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    service_name: str
    confidence_score: float
    timestamp: datetime
    quality_score: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class NewsTranslation:
    """新闻翻译数据模型"""
    news_id: str
    original_title: str
    translated_title: str
    original_description: str
    translated_description: str
    translation_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class QualityScore:
    """翻译质量评分"""
    overall_score: float  # 0-1之间的总体评分
    semantic_accuracy: float  # 语义准确性
    fluency: float  # 流畅度
    terminology_accuracy: float  # 术语准确性
    context_consistency: float  # 上下文一致性


@dataclass
class CachedTranslation:
    """缓存的翻译结果"""
    content_hash: str
    translation_result: TranslationResult
    created_at: datetime
    expires_at: datetime
    usage_count: int = 0


class ITranslationService(ABC):
    """翻译服务接口"""
    
    @abstractmethod
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'zh') -> TranslationResult:
        """翻译单个文本"""
        pass
    
    @abstractmethod
    def translate_batch(self, texts: List[str], source_lang: str = 'en', target_lang: str = 'zh') -> List[TranslationResult]:
        """批量翻译文本"""
        pass
    
    @abstractmethod
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态"""
        pass
    
    @abstractmethod
    def get_service_name(self) -> str:
        """获取服务名称"""
        pass


class ITranslationCache(ABC):
    """翻译缓存接口"""
    
    @abstractmethod
    def get_translation(self, content_hash: str) -> Optional[CachedTranslation]:
        """获取缓存的翻译"""
        pass
    
    @abstractmethod
    def save_translation(self, content_hash: str, translation: TranslationResult) -> bool:
        """保存翻译到缓存"""
        pass
    
    @abstractmethod
    def clear_expired_cache(self) -> int:
        """清理过期缓存"""
        pass


class IQualityAssessor(ABC):
    """翻译质量评估接口"""
    
    @abstractmethod
    def assess_translation(self, original: str, translation: str) -> QualityScore:
        """评估翻译质量"""
        pass
    
    @abstractmethod
    def compare_translations(self, original: str, translations: List[str]) -> List[QualityScore]:
        """比较多个翻译结果"""
        pass