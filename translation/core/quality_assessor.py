#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译质量评估器实现
"""

import re
import math
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
from translation.core.interfaces import IQualityAssessor, QualityScore


@dataclass
class TerminologyMapping:
    """术语映射"""
    english: str
    chinese: str
    category: str  # 'tech', 'business', 'general'


class TranslationQualityAssessor(IQualityAssessor):
    """翻译质量评估器"""
    
    def __init__(self):
        self.tech_terms = self._load_tech_terminology()
        self.business_terms = self._load_business_terminology()
        self.common_patterns = self._load_common_patterns()
        
    def _load_tech_terminology(self) -> Dict[str, str]:
        """加载科技术语映射表"""
        return {
            'artificial intelligence': '人工智能',
            'machine learning': '机器学习',
            'deep learning': '深度学习',
            'neural network': '神经网络',
            'blockchain': '区块链',
            'cryptocurrency': '加密货币',
            'bitcoin': '比特币',
            'ethereum': '以太坊',
            'chatgpt': 'ChatGPT',
            'openai': 'OpenAI',
            'google': '谷歌',
            'microsoft': '微软',
            'apple': '苹果',
            'meta': 'Meta',
            'facebook': 'Facebook',
            'twitter': '推特',
            'tesla': '特斯拉',
            'nvidia': '英伟达',
            'amd': 'AMD',
            'intel': '英特尔',
            'cloud computing': '云计算',
            'big data': '大数据',
            'internet of things': '物联网',
            'iot': '物联网',
            'virtual reality': '虚拟现实',
            'vr': 'VR',
            'augmented reality': '增强现实',
            'ar': 'AR',
            'api': 'API',
            'sdk': 'SDK',
            'saas': 'SaaS',
            'paas': 'PaaS',
            'iaas': 'IaaS'
        }
    
    def _load_business_terminology(self) -> Dict[str, str]:
        """加载商业术语映射表"""
        return {
            'revenue': '营收',
            'profit': '利润',
            'market cap': '市值',
            'ipo': 'IPO',
            'merger': '合并',
            'acquisition': '收购',
            'investment': '投资',
            'funding': '融资',
            'venture capital': '风险投资',
            'startup': '初创公司',
            'unicorn': '独角兽',
            'valuation': '估值',
            'stock': '股票',
            'share': '股份',
            'dividend': '股息',
            'ceo': 'CEO',
            'cto': 'CTO',
            'cfo': 'CFO'
        }
    
    def _load_common_patterns(self) -> Dict[str, str]:
        """加载常见表达模式"""
        return {
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(million|billion|trillion)': r'\1{}\2',
            r'(\d+)%': r'\1%',
            r'Q(\d+)\s+(\d{4})': r'\2年第\1季度'
        }
    
    def assess_translation(self, original: str, translation: str) -> QualityScore:
        """评估单个翻译的质量"""
        # 语义准确性评估
        semantic_score = self._assess_semantic_accuracy(original, translation)
        
        # 流畅度评估
        fluency_score = self._assess_fluency(translation)
        
        # 术语准确性评估
        terminology_score = self._assess_terminology_accuracy(original, translation)
        
        # 上下文一致性评估
        context_score = self._assess_context_consistency(original, translation)
        
        # 计算总体评分（加权平均）
        overall_score = (
            semantic_score * 0.35 +
            fluency_score * 0.25 +
            terminology_score * 0.25 +
            context_score * 0.15
        )
        
        return QualityScore(
            overall_score=overall_score,
            semantic_accuracy=semantic_score,
            fluency=fluency_score,
            terminology_accuracy=terminology_score,
            context_consistency=context_score
        )
    
    def compare_translations(self, original: str, translations: List[str]) -> List[QualityScore]:
        """比较多个翻译结果的质量"""
        scores = []
        for translation in translations:
            score = self.assess_translation(original, translation)
            scores.append(score)
        
        # 按总体评分排序
        scores.sort(key=lambda x: x.overall_score, reverse=True)
        return scores
    
    def _assess_semantic_accuracy(self, original: str, translation: str) -> float:
        """评估语义准确性"""
        # 检查关键信息是否保留
        score = 0.5  # 基础分
        
        # 检查数字是否保留
        original_numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', original)
        translation_numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', translation)
        
        if len(original_numbers) > 0:
            number_preservation = len(set(original_numbers) & set(translation_numbers)) / len(original_numbers)
            score += number_preservation * 0.2
        else:
            score += 0.2
        
        # 检查专有名词是否保留
        proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', original)
        preserved_nouns = 0
        for noun in proper_nouns:
            if noun.lower() in translation.lower() or self._find_chinese_equivalent(noun.lower()) in translation:
                preserved_nouns += 1
        
        if len(proper_nouns) > 0:
            noun_preservation = preserved_nouns / len(proper_nouns)
            score += noun_preservation * 0.3
        else:
            score += 0.3
        
        return min(score, 1.0)
    
    def _assess_fluency(self, translation: str) -> float:
        """评估中文表达流畅度"""
        score = 0.5  # 基础分
        
        # 检查是否包含中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', translation))
        total_chars = len(translation.replace(' ', ''))
        
        if total_chars > 0:
            chinese_ratio = chinese_chars / total_chars
            score += chinese_ratio * 0.3
        
        # 检查句子结构合理性
        sentences = re.split(r'[。！？]', translation)
        valid_sentences = 0
        
        for sentence in sentences:
            if len(sentence.strip()) > 0:
                # 简单的句子结构检查
                if self._is_valid_chinese_sentence(sentence.strip()):
                    valid_sentences += 1
        
        if len(sentences) > 1:
            structure_score = valid_sentences / (len(sentences) - 1)  # 减1因为最后一个分割是空的
            score += structure_score * 0.2
        else:
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_terminology_accuracy(self, original: str, translation: str) -> float:
        """评估术语翻译准确性"""
        score = 0.7  # 基础分（假设大部分术语正确）
        
        # 检查技术术语
        tech_terms_found = 0
        tech_terms_correct = 0
        
        for eng_term, chi_term in self.tech_terms.items():
            if eng_term.lower() in original.lower():
                tech_terms_found += 1
                if chi_term in translation or eng_term.upper() in translation:
                    tech_terms_correct += 1
        
        # 检查商业术语
        business_terms_found = 0
        business_terms_correct = 0
        
        for eng_term, chi_term in self.business_terms.items():
            if eng_term.lower() in original.lower():
                business_terms_found += 1
                if chi_term in translation or eng_term.upper() in translation:
                    business_terms_correct += 1
        
        total_terms = tech_terms_found + business_terms_found
        total_correct = tech_terms_correct + business_terms_correct
        
        if total_terms > 0:
            terminology_accuracy = total_correct / total_terms
            score = 0.3 + terminology_accuracy * 0.7
        
        return min(score, 1.0)
    
    def _assess_context_consistency(self, original: str, translation: str) -> float:
        """评估上下文一致性"""
        score = 0.6  # 基础分
        
        # 检查句子数量是否匹配
        original_sentences = len(re.split(r'[.!?]', original))
        translation_sentences = len(re.split(r'[。！？]', translation))
        
        if original_sentences > 0:
            sentence_ratio = min(translation_sentences / original_sentences, 1.0)
            score += sentence_ratio * 0.2
        else:
            score += 0.2
        
        # 检查长度合理性（中文通常比英文短）
        if len(original) > 0:
            length_ratio = len(translation) / len(original)
            if 0.3 <= length_ratio <= 1.2:  # 合理的长度比例
                score += 0.2
            else:
                score += 0.1
        
        return min(score, 1.0)
    
    def _find_chinese_equivalent(self, english_term: str) -> str:
        """查找英文术语的中文对应词"""
        all_terms = {**self.tech_terms, **self.business_terms}
        return all_terms.get(english_term.lower(), '')
    
    def _is_valid_chinese_sentence(self, sentence: str) -> bool:
        """简单检查是否为有效的中文句子"""
        # 基本检查：包含中文字符且不全是标点符号
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', sentence)
        return len(chinese_chars) >= 2  # 至少包含2个中文字符
    
    def get_best_translation(self, original: str, translations: List[str]) -> Tuple[str, QualityScore]:
        """获取最佳翻译结果"""
        if not translations:
            raise ValueError("翻译列表不能为空")
        
        scores = self.compare_translations(original, translations)
        best_index = 0
        best_score = scores[0]
        
        # 找到评分最高的翻译
        for i, score in enumerate(scores):
            if score.overall_score > best_score.overall_score:
                best_score = score
                best_index = i
        
        return translations[best_index], best_score