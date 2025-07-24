#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动翻译服务单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from ..services.siliconflow_translator import SiliconFlowTranslator
from ..core.interfaces import ServiceStatus


class TestSiliconFlowTranslator(unittest.TestCase):
    """硅基流动翻译服务测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.translator = SiliconFlowTranslator(
            api_key="test_api_key",
            model="Qwen/Qwen2.5-7B-Instruct"
        )
    
    def test_service_name(self):
        """测试服务名称"""
        self.assertEqual(self.translator.get_service_name(), "siliconflow_Qwen2.5-7B-Instruct")
    
    def test_create_translation_prompt(self):
        """测试翻译提示词创建"""
        prompt = self.translator._create_translation_prompt("Hello", "en", "zh")
        self.assertIn("英文", prompt)
        self.assertIn("中文", prompt)
        self.assertIn("Hello", prompt)
        self.assertIn("新闻翻译专家", prompt)
    
    def test_calculate_confidence(self):
        """测试置信度计算"""
        # 测试短文本
        confidence = self.translator._calculate_confidence("hi", "你好")
        self.assertLess(confidence, 0.85)  # 短文本置信度较低
        
        # 测试长文本
        long_text = "This is a very long text that should have higher confidence score"
        confidence = self.translator._calculate_confidence(long_text, "这是一个很长的文本，应该有更高的置信度评分")
        self.assertGreater(confidence, 0.85)  # 长文本置信度较高
        
        # 测试带使用信息的置信度
        usage_info = {"completion_tokens": 50}
        confidence = self.translator._calculate_confidence("hello", "你好", usage_info)
        self.assertGreaterEqual(confidence, 0.82)  # 调整期望值
    
    def test_get_model_info(self):
        """测试模型信息获取"""
        info = self.translator.get_model_info()
        self.assertEqual(info["model"], "Qwen/Qwen2.5-7B-Instruct")
        self.assertEqual(info["service"], "siliconflow")
        self.assertIn("translation", info["capabilities"])
        self.assertIn("en", info["languages"])
        self.assertIn("zh", info["languages"])
    
    @patch('urllib.request.urlopen')
    def test_translate_text_success(self, mock_urlopen):
        """测试成功翻译文本"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "你好"
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 10,
                "total_tokens": 110
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "你好")
        self.assertEqual(result.source_language, "en")
        self.assertEqual(result.target_language, "zh")
        self.assertTrue(result.service_name.startswith("siliconflow_"))
        self.assertGreater(result.confidence_score, 0.0)
        self.assertIsNone(result.error_message)
        self.assertIsInstance(result.timestamp, datetime)
    
    @patch('urllib.request.urlopen')
    def test_translate_text_with_prefix_cleanup(self, mock_urlopen):
        """测试翻译结果前缀清理"""
        # 模拟带前缀的API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "翻译：你好世界"
                }
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello world", "en", "zh")
        
        self.assertEqual(result.translated_text, "你好世界")  # 前缀应该被清理
    
    @patch('urllib.request.urlopen')
    def test_translate_text_api_error(self, mock_urlopen):
        """测试API错误处理"""
        # 模拟API错误响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "error": {
                "type": "invalid_request_error",
                "message": "Invalid API key"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        result = self.translator.translate_text("hello", "en", "zh")
        
        self.assertEqual(result.original_text, "hello")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertIsNotNone(result.error_message)
        self.assertIn("invalid_request_error", result.error_message)
    
    def test_translate_empty_text(self):
        """测试空文本翻译"""
        result = self.translator.translate_text("", "en", "zh")
        
        self.assertEqual(result.original_text, "")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.confidence_score, 0.0)
        self.assertEqual(result.error_message, "输入文本为空")
    
    @patch('urllib.request.urlopen')
    def test_batch_translate_combined_success(self, mock_urlopen):
        """测试成功的组合批量翻译"""
        # 模拟批量翻译API响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "1. 你好\n2. 世界"
                }
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        results = self.translator.translate_batch(["hello", "world"], "en", "zh")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].translated_text, "你好")
        self.assertEqual(results[1].translated_text, "世界")
    
    @patch('urllib.request.urlopen')
    def test_batch_translate_fallback(self, mock_urlopen):
        """测试批量翻译回退到单个翻译"""
        # 第一次调用（批量翻译）失败，后续调用（单个翻译）成功
        def side_effect(*args, **kwargs):
            mock_response = MagicMock()
            if not hasattr(side_effect, 'call_count'):
                side_effect.call_count = 0
            
            if side_effect.call_count == 0:
                # 批量翻译失败
                mock_response.read.return_value = json.dumps({
                    "error": {
                        "type": "invalid_request_error",
                        "message": "Request too long"
                    }
                }).encode('utf-8')
            else:
                # 单个翻译成功
                mock_response.read.return_value = json.dumps({
                    "choices": [{
                        "message": {
                            "content": "你好"
                        }
                    }]
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
            "choices": [{
                "message": {
                    "content": "你好"
                }
            }]
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
            "error": {
                "type": "rate_limit_exceeded",
                "message": "Rate limit exceeded"
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
                "type": "invalid_request_error",
                "message": "Unauthorized"
            }
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        status = self.translator.get_service_status()
        self.assertEqual(status, ServiceStatus.UNAVAILABLE)
    
    @patch('urllib.request.urlopen')
    def test_check_health(self, mock_urlopen):
        """测试健康检查功能"""
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "测试"
                }
            }]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        health_info = self.translator.check_health()
        
        self.assertTrue(health_info["service"].startswith("siliconflow_"))
        self.assertEqual(health_info["model"], "Qwen/Qwen2.5-7B-Instruct")
        self.assertEqual(health_info["status"], "healthy")
        self.assertIsInstance(health_info["response_time"], float)
        self.assertIsNotNone(health_info["last_check"])
        self.assertIsNone(health_info["error"])
        self.assertTrue(health_info["features"]["translation"])
        self.assertTrue(health_info["features"]["batch_translation"])
        self.assertTrue(health_info["features"]["multilingual"])
        self.assertTrue(health_info["features"]["ai_powered"])
    
    def test_initialization_without_api_key(self):
        """测试无API密钥初始化"""
        with self.assertRaises(ValueError) as context:
            SiliconFlowTranslator()
        
        self.assertIn("硅基流动API密钥未配置", str(context.exception))
    
    def test_different_models(self):
        """测试不同模型的初始化"""
        models = [
            "Qwen/Qwen2.5-14B-Instruct",
            "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "THUDM/glm-4-9b-chat"
        ]
        
        for model in models:
            translator = SiliconFlowTranslator(api_key="test_key", model=model)
            self.assertEqual(translator.model, model)
            self.assertTrue(translator.get_service_name().startswith("siliconflow_"))


if __name__ == '__main__':
    unittest.main()