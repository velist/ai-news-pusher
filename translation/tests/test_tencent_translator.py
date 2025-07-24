#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯翻译服务单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from ..services.tencent_translator import TencentTranslator
from ..core.interfaces import ServiceStatus


class TestTencentTranslator(unittest.TestCase):
    """腾讯翻译服务测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.translator = TencentTranslator(
            secret_id="test_secret_id",
            secret_key="test_secret_key"
        )
    
    def test_service_name(self):
        """测试服务名称"""
        self.assertEqual(self.translator.get_service_name(), "tencent_translate")
    
    def test_sign_method(self):
        """测试签名方法"""
        key = b"test_key"
        msg = "test_message"
        signature = self.translator._sign(key, msg)
        self.assertIsInstance(signature, bytes)
        self.assertEqual(len(signature), 32)  # SHA256哈希长度
    
    def test_get_signature_key(self):
        """测试签名密钥生成"""
        key = "test_key"
        date_stamp = "2023-01-01"
        region = "ap-beijing"
        service = "tmt"
        
        signing_key = self.translator._get_signature_key(key, date_stamp, region, service)
        self.assertIsInstance(signing_key, bytes)
        self.assertEqual(len(signing_key), 32)
    
    @patch('urllib.request.urlopen')
    def test_translate_text_success(self, mock_urlopen):
        """测试成功翻译文本"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "Response": {
                "TargetText": "你好",
                "Source": "en",
                "Target": "zh",
                "RequestId": "test-request-id"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "你好")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "zh")
        self.assertEqual(result.service_name, "tencent_translate")
        self.assertEqual(result.confidence_score, 0.85)
        self.assertIsNone(result.error_message)
        self.assertIsInstance(result.timestamp, datetime)
    
    @patch('urllib.request.urlopen')
    def test_translate_text_api_error(self, mock_urlopen):
        """测试API错误处理"""
        # 模拟API错误响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "Response": {
                "Error": {
                    "Code": "AuthFailure",
                    "Message": "Authentication failed"
                }
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertIsNotNone(result.error_message)
        self.assertIn("AuthFailure", result.error_message)
    
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
            "Response": {
                "TargetTextList": ["你好", "世界"],
                "Source": "en",
                "Target": "zh",
                "RequestId": "test-request-id"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        results = self.translator.translate_batch(["hello", "world"], "en", "zh")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].translated_text, "你好")
        self.assertEqual(results[1].translated_text, "世界")
        self.assertEqual(results[0].service_name, "tencent_translate")
        self.assertEqual(results[1].service_name, "tencent_translate")
    
    @patch('urllib.request.urlopen')
    def test_translate_batch_fallback(self, mock_urlopen):
        """测试批量翻译回退到单个翻译"""
        # 模拟批量翻译失败，然后单个翻译成功
        def side_effect(*args, **kwargs):
            mock_response = MagicMock()
            # 第一次调用是批量翻译失败
            if not hasattr(side_effect, 'call_count'):
                side_effect.call_count = 0
            
            if side_effect.call_count == 0:
                # 批量翻译失败
                mock_response.read.return_value = json.dumps({
                    "Response": {
                        "Error": {
                            "Code": "InvalidParameter",
                            "Message": "Batch translation not supported"
                        }
                    }
                }).encode('utf-8')
            else:
                # 单个翻译成功
                mock_response.read.return_value = json.dumps({
                    "Response": {
                        "TargetText": "你好",
                        "Source": "en",
                        "Target": "zh"
                    }
                }).encode('utf-8')
            
            side_effect.call_count += 1
            return mock_response
        
        mock_urlopen.return_value.__enter__ = side_effect
        
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
            "Response": {
                "TargetText": "你好",
                "Source": "en",
                "Target": "zh"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.HEALTHY)
    
    @patch('urllib.request.urlopen')
    def test_get_service_status_degraded(self, mock_urlopen):
        """测试降级服务状态"""
        # 模拟限流错误
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "Response": {
                "Error": {
                    "Code": "RequestLimitExceeded",
                    "Message": "Request rate limit exceeded"
                }
            }
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
    
    @patch('urllib.request.urlopen')
    def test_check_health(self, mock_urlopen):
        """测试健康检查功能"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "Response": {
                "TargetText": "测试",
                "Source": "en",
                "Target": "zh"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        health_info = self.translator.check_health()
        
        self.assertEqual(health_info["service"], "tencent_translate")
        self.assertEqual(health_info["status"], "healthy")
        self.assertIsInstance(health_info["response_time"], float)
        self.assertIsNotNone(health_info["last_check"])
        self.assertIsNone(health_info["error"])
    
    def test_initialization_without_credentials(self):
        """测试无凭证初始化"""
        with self.assertRaises(ValueError) as context:
            TencentTranslator()
        
        self.assertIn("腾讯翻译API凭证未配置", str(context.exception))


if __name__ == '__main__':
    unittest.main()