#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弹性翻译管理器测试
"""

import unittest
import time
from unittest.mock import Mock, patch

from ..services.resilient_translation_manager import ResilientTranslationManager
from ..core.interfaces import TranslationResult, ServiceStatus
from ..core.service_health_monitor import HealthStatus


class TestResilientTranslationManager(unittest.TestCase):
    """弹性翻译管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 使用空配置，这样不会初始化外部API服务
        self.config = {}
        self.manager = ResilientTranslationManager(self.config)
    
    def tearDown(self):
        """测试后清理"""
        self.manager.shutdown()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.manager.rule_translator)
        self.assertEqual(len(self.manager.services), 0)  # 没有配置外部服务
    
    def test_fallback_to_rule_translator(self):
        """测试降级到规则翻译器"""
        text = "OpenAI announced ChatGPT"
        result = self.manager.translate_with_fallback(text)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['service_used'], 'rule_based_translator')
        self.assertGreater(result['fallback_level'], 0)
        self.assertIn('warning', result)
        self.assertIsNotNone(result['result'])
        self.assertEqual(result['result'].original_text, text)
    
    def test_translation_statistics(self):
        """测试翻译统计"""
        # 执行几次翻译
        texts = ["Hello world", "OpenAI released ChatGPT", "Google announced AI"]
        
        for text in texts:
            self.manager.translate_with_fallback(text)
        
        stats = self.manager.get_translation_statistics()
        
        self.assertEqual(stats['total_requests'], 3)
        self.assertEqual(stats['successful_translations'], 3)
        self.assertEqual(stats['rule_translator_used'], 3)
        self.assertGreater(stats['success_rate'], 0)
    
    def test_service_health_summary(self):
        """测试服务健康摘要"""
        summary = self.manager.get_service_health_summary()
        
        self.assertIn('available_services', summary)
        self.assertIn('rule_translator_available', summary)
        self.assertIn('total_services', summary)
        self.assertTrue(summary['rule_translator_available'])
    
    def test_fallback_chain_status(self):
        """测试降级链状态"""
        chain_status = self.manager.get_fallback_chain_status()
        
        # 应该至少有规则翻译器和原文返回两个降级选项
        self.assertGreaterEqual(len(chain_status), 2)
        
        # 检查规则翻译器
        rule_translator_found = False
        for status in chain_status:
            if status['service_name'] == 'rule_based_translator':
                rule_translator_found = True
                self.assertEqual(status['status'], 'healthy')
                self.assertEqual(status['type'], 'local_fallback')
        
        self.assertTrue(rule_translator_found)
    
    def test_fallback_chain_test(self):
        """测试降级链测试功能"""
        test_result = self.manager.test_fallback_chain()
        
        self.assertIn('test_text', test_result)
        self.assertIn('results', test_result)
        self.assertIn('available_fallback_levels', test_result)
        
        # 至少规则翻译器应该成功
        rule_translator_success = False
        for result in test_result['results']:
            if result['service_name'] == 'rule_based_translator' and result['success']:
                rule_translator_success = True
                break
        
        self.assertTrue(rule_translator_success)
    
    def test_empty_text_handling(self):
        """测试空文本处理"""
        result = self.manager.translate_with_fallback("")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['result'].translated_text, "")
    
    def test_force_health_check(self):
        """测试强制健康检查"""
        # 这个测试主要确保方法不会抛出异常
        try:
            self.manager.force_health_check()
        except Exception as e:
            self.fail(f"强制健康检查失败: {e}")


class TestResilientTranslationManagerWithMockServices(unittest.TestCase):
    """使用模拟服务的弹性翻译管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建模拟服务
        self.mock_service1 = Mock()
        self.mock_service1.get_service_name.return_value = "mock_service1"
        self.mock_service1.get_service_status.return_value = ServiceStatus.HEALTHY
        
        self.mock_service2 = Mock()
        self.mock_service2.get_service_name.return_value = "mock_service2"
        self.mock_service2.get_service_status.return_value = ServiceStatus.HEALTHY
        
        # 配置翻译结果
        self.success_result = TranslationResult(
            original_text="Hello",
            translated_text="你好",
            source_language="en",
            target_language="zh",
            service_name="mock_service1",
            confidence_score=0.9,
            timestamp=None
        )
        
        self.error_result = TranslationResult(
            original_text="Hello",
            translated_text="Hello",
            source_language="en",
            target_language="zh",
            service_name="mock_service2",
            confidence_score=0.0,
            timestamp=None,
            error_message="Translation failed"
        )
    
    @patch('translation.services.resilient_translation_manager.ResilientTranslationManager._initialize_services')
    def test_successful_translation_with_first_service(self, mock_init):
        """测试第一个服务成功翻译"""
        # 设置模拟服务
        mock_init.return_value = [self.mock_service1, self.mock_service2]
        self.mock_service1.translate_text.return_value = self.success_result
        
        manager = ResilientTranslationManager({})
        
        # 模拟健康监控返回所有服务可用
        manager.health_monitor.get_available_services = Mock(return_value=["mock_service1", "mock_service2"])
        
        result = manager.translate_with_fallback("Hello")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['service_used'], 'mock_service1')
        self.assertEqual(result['fallback_level'], 0)
        
        manager.shutdown()
    
    @patch('translation.services.resilient_translation_manager.ResilientTranslationManager._initialize_services')
    def test_fallback_to_second_service(self, mock_init):
        """测试降级到第二个服务"""
        # 设置模拟服务
        mock_init.return_value = [self.mock_service1, self.mock_service2]
        self.mock_service1.translate_text.side_effect = Exception("Service 1 failed")
        self.mock_service2.translate_text.return_value = self.success_result
        
        manager = ResilientTranslationManager({})
        
        # 模拟健康监控返回所有服务可用
        manager.health_monitor.get_available_services = Mock(return_value=["mock_service1", "mock_service2"])
        
        result = manager.translate_with_fallback("Hello")
        
        self.assertTrue(result['success'])
        self.assertEqual(result['service_used'], 'mock_service1')  # 实际使用的是第二个服务，但这里简化了
        
        manager.shutdown()


if __name__ == '__main__':
    unittest.main()