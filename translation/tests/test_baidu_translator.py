#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度翻译服务单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from ..services.baidu_translator import BaiduTranslator
from ..core.interfaces import ServiceStatus


class TestBaiduTranslator(unittest.TestCase):
    """百度翻译服务测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.translator = BaiduTranslator(app_id="test_app_id", secret_key="test_secret_key")
    
    def test_service_name(self):
        """测试服务名称"""
        self.assertEqual(self.translator.get_service_name(), "baidu_translate")
    
    def test_generate_sign(self):
        """测试签名生成"""
        query = "hello"
        salt = "12345"
        sign = self.translator._generate_sign(query, salt)
        self.assertIsInstance(sign, str)
        self.assertEqual(len(sign), 32)  # MD5哈希长度
    
    def test_get_error_message(self):
        """测试错误信息获取"""
        self.assertEqual(self.translator._get_error_message('52001'), 'APP ID无效')
        self.assertEqual(self.translator._get_error_message('54004'), '账户余额不足')
        self.assertTrue(self.translator._get_error_message('99999').startswith('未知错误'))
    
    @patch('urllib.request.urlopen')
    def test_translate_text_success(self, mock_urlopen):
        """测试成功翻译文本"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "trans_result": [{"src": "hello", "dst": "你好"}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "你好")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "zh")
        self.assertEqual(result.service_name, "baidu_translate")
        self.assertEqual(result.confidence_score, 0.9)
        self.assertIsNone(result.error_message)
        self.assertIsInstance(result.timestamp, datetime)
    
    @patch('urllib.request.urlopen')
    def test_translate_text_api_error(self, mock_urlopen):
        """测试API错误处理"""
        # 模拟API错误响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "error_code": "52001"
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertIsNotNone(result.error_message)
        self.assertIn("APP ID无效", result.error_message)
    
    def test_translate_empty_text(self):
        """测试空文本翻译"""
        result = self.translator.translate_text("", "en", "zh")
        
        self.assertEqual(result.original_text, "")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertEqual(result.error_message, "输入文本为空")
    
    @patch('urllib.request.urlopen')
    def test_translate_batch(self, mock_urlopen):
        """测试批量翻译"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.read.side_effect = [
            json.dumps({"trans_result": [{"src": "hello", "dst": "你好"}]}).encode('utf-8'),
            json.dumps({"trans_result": [{"src": "world", "dst": "世界"}]}).encode('utf-8')
        ]
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        results = self.translator.translate_batch(["hello", "world"], "en", "zh")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].translated_text, "你好")
        self.assertEqual(results[1].translated_text, "世界")
    
    @patch('urllib.request.urlopen')
    def test_get_service_status_healthy(self, mock_urlopen):
        """测试健康服务状态"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "trans_result": [{"src": "hello", "dst": "你好"}]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.HEALTHY)
    
    @patch('urllib.request.urlopen')
    def test_get_service_status_degraded(self, mock_urlopen):
        """测试降级服务状态"""
        # 模拟频率限制错误
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "error_code": "54003"
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.DEGRADED)
    
    @patch('urllib.request.urlopen')
    def test_get_service_status_unavailable(self, mock_urlopen):
        """测试不可用服务状态"""
        # 模拟网络异常
        mock_urlopen.side_effect = Exception("Network error")
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.UNAVAILABLE)
    
    def test_initialization_without_credentials(self):
        """测试无凭证初始化"""
        with self.assertRaises(ValueError) as context:
            BaiduTranslator()
        
        self.assertIn("百度翻译API凭证未配置", str(context.exception))


if __name__ == '__main__':
    unittest.main()