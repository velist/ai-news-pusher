#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google翻译服务单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from ..services.google_translator import GoogleTranslator
from ..core.interfaces import ServiceStatus


class TestGoogleTranslator(unittest.TestCase):
    """Google翻译服务测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.translator = GoogleTranslator(api_key="test_api_key")
    
    def test_service_name(self):
        """测试服务名称"""
        self.assertEqual(self.translator.get_service_name(), "google_translate")
    
    def test_calculate_confidence(self):
        """测试置信度计算"""
        # 测试短文本
        confidence = self.translator._calculate_confidence("hi", "你好")
        self.assertLess(confidence, 0.8)  # 短文本置信度较低
        
        # 测试长文本
        long_text = "This is a very long text that should have higher confidence"
        confidence = self.translator._calculate_confidence(long_text, "这是一个很长的文本，应该有更高的置信度")
        self.assertGreater(confidence, 0.8)  # 长文本置信度较高
        
        # 测试带语言检测的置信度
        confidence = self.translator._calculate_confidence("hello", "你好", "en")
        self.assertGreater(confidence, 0.8)  # 有语言检测的置信度更高
    
    @patch('urllib.request.urlopen')
    def test_detect_language(self, mock_urlopen):
        """测试语言检测"""
        # 模拟语言检测API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "detections": [[{
                    "language": "en",
                    "isReliable": True,
                    "confidence": 0.99
                }]]
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        detected_lang = self.translator.detect_language("Hello world")
        self.assertEqual(detected_lang, "en")
    
    @patch('urllib.request.urlopen')
    def test_translate_text_success(self, mock_urlopen):
        """测试成功翻译文本"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "translations": [{
                    "translatedText": "你好",
                    "detectedSourceLanguage": "en"
                }]
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "你好")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "zh")
        self.assertEqual(result.service_name, "google_translate")
        self.assertGreater(result.confidence_score, 0.0)
        self.assertIsNone(result.error_message)
        self.assertIsInstance(result.timestamp, datetime)
    
    @patch('urllib.request.urlopen')
    def test_translate_text_api_error(self, mock_urlopen):
        """测试API错误处理"""
        # 模拟API错误响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "error": {
                "code": 403,
                "message": "The request is missing a valid API key."
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertIsNotNone(result.error_message)
        self.assertIn("403", result.error_message)
    
    def test_translate_empty_text(self):
        """测试空文本翻译"""
        result = self.translator.translate_text("", "en", "zh")
        
        self.assertEqual(result.original_text, "")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertEqual(result.error_message, "输入文本为空")
    
    @patch('urllib.request.urlopen')
    def test_translate_batch_success(self, mock_urlopen):
        """测试成功批量翻译"""
        # 模拟批量翻译API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "translations": [
                    {"translatedText": "你好"},
                    {"translatedText": "世界"}
                ]
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        results = self.translator.translate_batch(["hello", "world"], "en", "zh")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].translated_text, "你好")
        self.assertEqual(results[1].translated_text, "世界")
        self.assertEqual(results[0].service_name, "google_translate")
        self.assertEqual(results[1].service_name, "google_translate")
    
    @patch('urllib.request.urlopen')
    def test_translate_batch_fallback(self, mock_urlopen):
        """测试批量翻译回退到单个翻译"""
        # 第一次调用（批量翻译）失败，后续调用（单个翻译）成功
        mock_response_batch_fail = MagicMock()
        mock_response_batch_fail.read.return_value = json.dumps({
            "error": {
                "code": 400,
                "message": "Bad Request"
            }
        }).encode('utf-8')
        
        mock_response_single_success = MagicMock()
        mock_response_single_success.read.return_value = json.dumps({
            "data": {
                "translations": [{
                    "translatedText": "你好"
                }]
            }
        }).encode('utf-8')
        
        # 设置多次调用的返回值
        mock_urlopen.return_value.__enter__.side_effect = [
            mock_response_batch_fail,  # 批量翻译失败
            mock_response_single_success,  # 第一个单个翻译成功
            mock_response_single_success   # 第二个单个翻译成功
        ]
        
        results = self.translator.translate_batch(["hello", "world"], "en", "zh")
        
        self.assertEqual(len(results), 2)
        # 由于回退到单个翻译，两个结果都应该是"你好"
        self.assertEqual(results[0].translated_text, "你好")
        self.assertEqual(results[1].translated_text, "你好")
    
    def test_translate_batch_empty_list(self):
        """测试空列表批量翻译"""
        results = self.translator.translate_batch([], "en", "zh")
        self.assertEqual(len(results), 0)
    
    @patch('urllib.request.urlopen')
    def test_get_service_status_healthy(self, mock_urlopen):
        """测试健康服务状态"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "translations": [{
                    "translatedText": "你好"
                }]
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.HEALTHY)
    
    @patch('urllib.request.urlopen')
    def test_get_service_status_degraded_quota(self, mock_urlopen):
        """测试配额限制导致的降级状态"""
        # 模拟配额限制错误
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "error": {
                "code": 429,
                "message": "Quota exceeded"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.DEGRADED)
    
    @patch('urllib.request.urlopen')
    def test_get_service_status_unavailable(self, mock_urlopen):
        """测试不可用服务状态"""
        # 模拟认证失败
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "error": {
                "code": 403,
                "message": "Forbidden"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.UNAVAILABLE)
    
    @patch('urllib.request.urlopen')
    def test_get_supported_languages(self, mock_urlopen):
        """测试获取支持的语言列表"""
        # 模拟支持语言API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "data": {
                "languages": [
                    {"language": "en", "name": "English"},
                    {"language": "zh", "name": "Chinese"},
                    {"language": "ja", "name": "Japanese"}
                ]
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        languages = self.translator.get_supported_languages()
        
        self.assertEqual(len(languages), 3)
        self.assertEqual(languages[0]["language"], "en")
        self.assertEqual(languages[1]["language"], "zh")
        self.assertEqual(languages[2]["language"], "ja")
    
    @patch('urllib.request.urlopen')
    def test_check_health(self, mock_urlopen):
        """测试健康检查功能"""
        # 模拟翻译和语言检测成功响应
        mock_translate_response = MagicMock()
        mock_translate_response.read.return_value = json.dumps({
            "data": {
                "translations": [{
                    "translatedText": "测试"
                }]
            }
        }).encode('utf-8')
        
        mock_detect_response = MagicMock()
        mock_detect_response.read.return_value = json.dumps({
            "data": {
                "detections": [[{
                    "language": "en",
                    "confidence": 0.99
                }]]
            }
        }).encode('utf-8')
        
        # 设置多次调用的返回值
        mock_urlopen.return_value.__enter__.side_effect = [
            mock_translate_response,  # 翻译测试
            mock_detect_response      # 语言检测测试
        ]
        
        health_info = self.translator.check_health()
        
        self.assertEqual(health_info["service"], "google_translate")
        self.assertEqual(health_info["status"], "healthy")
        self.assertIsInstance(health_info["response_time"], float)
        self.assertIsNotNone(health_info["last_check"])
        self.assertIsNone(health_info["error"])
        self.assertTrue(health_info["features"]["translation"])
        self.assertTrue(health_info["features"]["language_detection"])
        self.assertTrue(health_info["features"]["batch_translation"])
    
    def test_initialization_without_api_key(self):
        """测试无API密钥初始化"""
        with self.assertRaises(ValueError) as context:
            GoogleTranslator()
        
        self.assertIn("Google翻译API密钥未配置", str(context.exception))


if __name__ == '__main__':
    unittest.main()