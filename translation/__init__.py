#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务包
"""

from .core.interfaces import (
    ITranslationService,
    ITranslationCache,
    IQualityAssessor,
    TranslationResult,
    NewsTranslation,
    QualityScore,
    CachedTranslation,
    ServiceStatus
)

from .services.baidu_translator import BaiduTranslator
from .services.tencent_translator import TencentTranslator
from .services.google_translator import GoogleTranslator
from .services.siliconflow_translator import SiliconFlowTranslator

__version__ = "1.0.0"
__all__ = [
    # 接口
    'ITranslationService',
    'ITranslationCache', 
    'IQualityAssessor',
    # 数据模型
    'TranslationResult',
    'NewsTranslation',
    'QualityScore',
    'CachedTranslation',
    'ServiceStatus',
    # 翻译服务
    'BaiduTranslator',
    'TencentTranslator',
    'GoogleTranslator',
    'SiliconFlowTranslator'
]