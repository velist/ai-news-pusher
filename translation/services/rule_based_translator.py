#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于规则的本地翻译器 - 作为最终降级方案
当所有外部翻译API都失败时，提供基础的翻译服务
"""

import re
import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

from ..core.interfaces import ITranslationService, TranslationResult, ServiceStatus


class RuleBasedTranslator(ITranslationService):
    """基于规则的本地翻译器"""
    
    def __init__(self, dictionary_path: Optional[str] = None):
        """初始化规则翻译器"""
        self.service_name = "rule_based_translator"
        self.dictionary_path = dictionary_path
        self.tech_terms_dict = {}
        self.common_words_dict = {}
        
        # 加载翻译词典
        self._load_dictionaries()
        
        # 如果有自定义词典文件，加载它
        if self.dictionary_path and Path(self.dictionary_path).exists():
            self._load_custom_dictionary()
    
    def _load_dictionaries(self):
        """加载翻译词典"""
        # 科技术语词典
        self.tech_terms_dict = {
            "artificial intelligence": "人工智能",
            "machine learning": "机器学习",
            "deep learning": "深度学习",
            "chatgpt": "ChatGPT",
            "openai": "OpenAI",
            "gpt": "GPT",
            "google": "谷歌",
            "microsoft": "微软",
            "apple": "苹果",
            "amazon": "亚马逊",
            "meta": "Meta",
            "facebook": "Facebook",
            "twitter": "推特",
            "tesla": "特斯拉",
            "nvidia": "英伟达",
            "blockchain": "区块链",
            "cryptocurrency": "加密货币",
            "bitcoin": "比特币",
            "ethereum": "以太坊",
        }
        
        # 常用词汇词典
        self.common_words_dict = {
            "announced": "宣布",
            "released": "发布",
            "launched": "推出",
            "developed": "开发",
            "created": "创建",
            "company": "公司",
            "technology": "技术",
            "product": "产品",
            "service": "服务",
            "new": "新的",
            "latest": "最新的",
            "advanced": "先进的",
        }   
 
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'zh') -> TranslationResult:
        """翻译单个文本"""
        if not text or not text.strip():
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                service_name=self.service_name,
                confidence_score=1.0,
                timestamp=datetime.now()
            )
        
        # 目前只支持英文到中文的翻译
        if source_lang != 'en' or target_lang != 'zh':
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                service_name=self.service_name,
                confidence_score=0.1,
                timestamp=datetime.now(),
                error_message=f"不支持从{source_lang}到{target_lang}的翻译"
            )
        
        try:
            translated_text = self._translate_english_to_chinese(text)
            confidence = self._calculate_confidence(text, translated_text)
            
            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=source_lang,
                target_language=target_lang,
                service_name=self.service_name,
                confidence_score=confidence,
                timestamp=datetime.now()
            )
        except Exception as e:
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                service_name=self.service_name,
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message=f"规则翻译失败: {str(e)}"
            )
    
    def translate_batch(self, texts: List[str], source_lang: str = 'en', target_lang: str = 'zh') -> List[TranslationResult]:
        """批量翻译文本"""
        results = []
        for text in texts:
            result = self.translate_text(text, source_lang, target_lang)
            results.append(result)
        return results
    
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态 - 规则翻译器总是可用的"""
        return ServiceStatus.HEALTHY
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return self.service_name  
  
    def _translate_english_to_chinese(self, text: str) -> str:
        """将英文文本翻译为中文"""
        result_text = text
        
        # 1. 首先翻译科技术语（优先级最高）
        for en_term, zh_term in self.tech_terms_dict.items():
            pattern = re.compile(r'\b' + re.escape(en_term) + r'\b', re.IGNORECASE)
            result_text = pattern.sub(zh_term, result_text)
        
        # 2. 翻译常用词汇
        for en_word, zh_word in self.common_words_dict.items():
            pattern = re.compile(r'\b' + re.escape(en_word) + r'\b', re.IGNORECASE)
            result_text = pattern.sub(zh_word, result_text)
        
        # 3. 清理和格式化
        result_text = self._clean_and_format(result_text)
        
        return result_text
    
    def _clean_and_format(self, text: str) -> str:
        """清理和格式化翻译结果"""
        # 移除多余的空格
        text = re.sub(r'\s+', ' ', text)
        
        # 修复标点符号周围的空格
        text = re.sub(r'\s*([，。！？；：])\s*', r'\1', text)
        text = re.sub(r'\s*([,\.!?;:])\s*', r'\1 ', text)
        
        # 去除首尾空格
        text = text.strip()
        
        return text
    
    def _calculate_confidence(self, original: str, translated: str) -> float:
        """计算翻译置信度"""
        if not original or not translated:
            return 0.0
        
        # 如果翻译结果与原文相同，说明没有进行翻译
        if original == translated:
            return 0.1
        
        # 计算翻译覆盖率
        original_words = set(original.lower().split())
        
        # 检查有多少原文词汇被翻译了
        known_terms = set(self.tech_terms_dict.keys()) | set(self.common_words_dict.keys())
        translated_count = 0
        total_translatable = 0
        
        for word in original_words:
            # 移除标点符号
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word in known_terms:
                total_translatable += 1
                # 检查是否在译文中找到对应的中文
                if clean_word in self.tech_terms_dict:
                    if self.tech_terms_dict[clean_word] in translated:
                        translated_count += 1
                elif clean_word in self.common_words_dict:
                    if self.common_words_dict[clean_word] in translated:
                        translated_count += 1
        
        if total_translatable == 0:
            # 如果没有可翻译的词汇，但产生了不同的输出，给予基础分数
            return 0.3 if original != translated else 0.1
        
        # 基于翻译覆盖率计算置信度
        coverage_ratio = translated_count / total_translatable
        
        # 规则翻译的置信度通常较低，最高0.6
        return min(0.6, 0.2 + coverage_ratio * 0.4)    

    def _load_custom_dictionary(self):
        """加载自定义词典文件"""
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                custom_dict = json.load(f)
                self.tech_terms_dict.update(custom_dict.get('tech_terms', {}))
                self.common_words_dict.update(custom_dict.get('common_words', {}))
        except Exception as e:
            print(f"加载自定义词典失败: {e}")
    
    def add_custom_term(self, english_term: str, chinese_term: str, is_tech_term: bool = True):
        """添加自定义术语"""
        if is_tech_term:
            self.tech_terms_dict[english_term.lower()] = chinese_term
        else:
            self.common_words_dict[english_term.lower()] = chinese_term
    
    def save_custom_dictionary(self, file_path: str):
        """保存自定义词典到文件"""
        custom_dict = {
            'tech_terms': self.tech_terms_dict,
            'common_words': self.common_words_dict
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(custom_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自定义词典失败: {e}")