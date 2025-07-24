#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则翻译器测试
"""

import unittest
import tempfile
import json
from datetime import datetime

from ..services.rule_based_translator import RuleBasedTranslator
from ..core.interfaces import ServiceStatus


class TestRuleBasedTranslator(unittest.TestCase):
    """规则翻译器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.translator = RuleBasedTranslator()
    
    def test_service_status(self):
        """测试服务状态"""
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.HEALTHY)
    
    def test_service_name(self):
        """测试服务名称"""
        name = self.translator.get_service_name()
        self.assertEqual(name, "rule_based_translator")
    
    def test_translate_empty_text(self):
        """测试翻译空文本"""
        result = self.translator.translate_text("")
        self.assertEqual(result.original_text, "")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 1.0)
    
    def test_translate_tech_terms(self):
        """测试科技术语翻译"""
        text = "OpenAI released ChatGPT"
        result = self.translator.translate_text(text)
        
        self.assertEqual(result.original_text, text)
        self.assertIn("OpenAI", result.translated_text)
        self.assertIn("ChatGPT", result.translated_text)
        self.assertIn("发布", result.translated_text)
        self.assertGreater(result.confidence_score, 0.1)
    
    def test_translate_common_words(self):
        """测试常用词汇翻译"""
        text = "The company announced new technology"
        result = self.translator.translate_text(text)
        
        self.assertEqual(result.original_text, text)
        self.assertIn("公司", result.translated_text)
        self.assertIn("宣布", result.translated_text)
        self.assertIn("技术", result.translated_text)
        self.assertGreater(result.confidence_score, 0.1)
    
    def test_preserve_numbers_and_dates(self):
        """测试保持数字和日期"""
        text = "Released on 2024-07-24 with 100 features"
        result = self.translator.translate_text(text)
        
        # 数字和日期应该保持不变
        self.assertIn("2024-07-24", result.translated_text)
        self.assertIn("100", result.translated_text)
    
    def test_unsupported_language_pair(self):
        """测试不支持的语言对"""
        result = self.translator.translate_text("Hello", source_lang='fr', target_lang='de')
        
        self.assertEqual(result.translated_text, "Hello")  # 应该返回原文
        self.assertEqual(result.confidence_score, 0.1)
        self.assertIsNotNone(result.error_message)
    
    def test_batch_translation(self):
        """测试批量翻译"""
        texts = [
            "OpenAI announced ChatGPT",
            "Google released new AI model",
            "Microsoft developed advanced technology"
        ]
        
        results = self.translator.translate_batch(texts)
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertGreater(result.confidence_score, 0.1)
            self.assertIsNotNone(result.translated_text)
    
    def test_add_custom_term(self):
        """测试添加自定义术语"""
        # 添加自定义术语
        self.translator.add_custom_term("kiro", "Kiro助手", is_tech_term=True)
        
        text = "Kiro is an AI assistant"
        result = self.translator.translate_text(text)
        
        self.assertIn("Kiro助手", result.translated_text)
    
    def test_custom_dictionary_file(self):
        """测试自定义词典文件"""
        # 创建临时词典文件
        custom_dict = {
            "tech_terms": {
                "testai": "测试AI"
            },
            "common_words": {
                "testword": "测试词"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(custom_dict, f, ensure_ascii=False)
            dict_path = f.name
        
        # 使用自定义词典创建翻译器
        translator = RuleBasedTranslator(dictionary_path=dict_path)
        
        text = "TestAI is a testword"
        result = translator.translate_text(text)
        
        self.assertIn("测试AI", result.translated_text)
        self.assertIn("测试词", result.translated_text)
    
    def test_confidence_calculation(self):
        """测试置信度计算"""
        # 包含已知术语的文本应该有较高置信度
        text_with_known_terms = "OpenAI announced ChatGPT technology"
        result1 = self.translator.translate_text(text_with_known_terms)
        
        # 不包含已知术语的文本应该有较低置信度
        text_with_unknown_terms = "Xyz abc def ghi"
        result2 = self.translator.translate_text(text_with_unknown_terms)
        
        self.assertGreater(result1.confidence_score, result2.confidence_score)
    
    def test_mixed_content_translation(self):
        """测试混合内容翻译"""
        text = "Google announced AI model with 95% accuracy on 2024-07-24"
        result = self.translator.translate_text(text)
        
        # 应该翻译已知词汇
        self.assertIn("谷歌", result.translated_text)
        self.assertIn("宣布", result.translated_text)
        
        # 应该保持数字和日期
        self.assertIn("95%", result.translated_text)
        self.assertIn("2024-07-24", result.translated_text)


if __name__ == '__main__':
    unittest.main()