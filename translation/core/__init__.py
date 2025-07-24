#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务核心模块
"""

from .interfaces import (
    ITranslationService,
    ITranslationCache,
    IQualityAssessor,
    TranslationResult,
    NewsTranslation,
    QualityScore,
    CachedTranslation,
    ServiceStatus
)

__all__ = [
    'ITranslationService',
    'ITranslationCache',
    'IQualityAssessor',
    'TranslationResult',
    'NewsTranslation',
    'QualityScore',
    'CachedTranslation',
    'ServiceStatus'
]