#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务比较器测试
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from translation.core.interfaces import TranslationResult, ServiceStatus
from translation.core.translation_comparator import TranslationComparator, AdaptiveTranslationSelector
from translation.core.quality_assessor import TranslationQualityAssessor


class TestTranslationComparator(unittest.TestCase):
    """翻译服务比较器测试类"""
    
    def setUp(self):
        """测试初始化"""
        # 创建模拟的翻译服务
        self.mock_service1 = Mock()
        self.mock_service1.get_service_name.return_value = "baidu"
        self.mock_service1.get_service_status.return_value = ServiceStatus.HEALTHY
        
        self.mock_service2 = Mock()
        self.mock_service2.get_service_name.return_value = "google"
        self.mock_service2.get_service_status.return_value = ServiceStatus.HEALTHY
        
        self.mock_service3 = Mock()
        self.mock_service3.get_service_name.return_value = "siliconflow"
        self.mock_service3.get_service_status.return_value = ServiceStatus.HEALTHY
        
        self.services = [self.mock_service1, self.mock_service2, self.mock_service3]
        self.comparator = TranslationComparator(self.services)
    
    def test_compare_translations_success(self):
        """测试成功的翻译比较"""
        # 设置模拟返回值
        self.mock_service1.translate_text.return_value = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh",
            service_name="baidu",
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        
        self.mock_service2.translate_text.return_value = TranslationResult(
            original_text="Hello world",
            translated_text="你好，世界",
            source_language="en",
            target_language="zh",
            service_name="google",
            confidence_score=0.95,
            timestamp=datetime.now()
        )
        
        self.mock_service3.translate_text.return_value = TranslationResult(
            original_text="Hello world",
            translated_text="您好，世界",
            source_language="en",
            target_language="zh",
            service_name="siliconflow",
            confidence_score=0.92,
            timestamp=datetime.now()
        )
        
        # 执行比较
        comparison = self.comparator.compare_translations("Hello world")
        
        # 验证结果
        self.assertIsNotNone(comparison)
        self.assertEqual(comparison.original_text, "Hello world")
        self.assertEqual(len(comparison.all_results), 3)
        self.assertEqual(len(comparison.quality_scores), 3)
        self.assertIsNotNone(comparison.best_translation)
        
        # 验证所有服务都被调用
        self.mock_service1.translate_text.assert_called_once()
        self.mock_service2.translate_text.assert_called_once()
        self.mock_service3.translate_text.assert_called_once()
    
    def test_compare_translations_with_failures(self):
        """测试部分服务失败的翻译比较"""
        # 设置一个服务成功，两个服务失败
        self.mock_service1.translate_text.return_value = TranslationResult(
            original_text="Test text",
            translated_text="测试文本",
            source_language="en",
            target_language="zh",
            service_name="baidu",
            confidence_score=0.8,
            timestamp=datetime.now()
        )
        
        self.mock_service2.translate_text.side_effect = Exception("Service unavailable")
        self.mock_service3.translate_text.side_effect = Exception("API error")
        
        # 执行比较
        comparison = self.comparator.compare_translations("Test text")
        
        # 验证结果
        self.assertIsNotNone(comparison)
        self.assertEqual(len(comparison.all_results), 1)
        self.assertEqual(comparison.best_translation.service_name, "baidu")
    
    def test_compare_translations_all_failures(self):
        """测试所有服务都失败的情况"""
        # 设置所有服务都失败
        self.mock_service1.translate_text.side_effect = Exception("Service error")
        self.mock_service2.translate_text.side_effect = Exception("Service error")
        self.mock_service3.translate_text.side_effect = Exception("Service error")
        
        # 执行比较应该抛出异常
        with self.assertRaises(RuntimeError):
            self.comparator.compare_translations("Test text")
    
    def test_service_weight_calculation(self):
        """测试服务权重计算"""
        # 测试已知服务的权重
        self.assertEqual(self.comparator._get_service_weight("siliconflow"), 0.9)
        self.assertEqual(self.comparator._get_service_weight("google"), 0.85)
        self.assertEqual(self.comparator._get_service_weight("baidu"), 0.8)
        self.assertEqual(self.comparator._get_service_weight("unknown"), 0.5)
    
    def test_get_service_performance_stats(self):
        """测试获取服务性能统计"""
        stats = self.comparator.get_service_performance_stats()
        
        # 验证统计信息
        self.assertIn("baidu", stats)
        self.assertIn("google", stats)
        self.assertIn("siliconflow", stats)
        
        for service_name, service_stats in stats.items():
            self.assertIn("status", service_stats)
            self.assertIn("weight", service_stats)


class TestAdaptiveTranslationSelector(unittest.TestCase):
    """自适应翻译选择器测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.selector = AdaptiveTranslationSelector()
    
    def test_update_service_performance(self):
        """测试更新服务性能"""
        # 更新服务性能
        self.selector.update_service_performance("baidu", 0.8, 1.5, True)
        self.selector.update_service_performance("google", 0.9, 2.0, True)
        self.selector.update_service_performance("baidu", 0.7, 1.8, True)
        
        # 验证统计信息
        self.assertIn("baidu", self.selector.service_stats)
        self.assertIn("google", self.selector.service_stats)
        
        baidu_stats = self.selector.service_stats["baidu"]
        self.assertEqual(baidu_stats["total_requests"], 2)
        self.assertEqual(baidu_stats["successful_requests"], 2)
    
    def test_get_recommended_services_no_data(self):
        """测试没有数据时的推荐服务"""
        recommended = self.selector.get_recommended_services()
        
        # 应该返回默认顺序
        self.assertEqual(recommended, ['siliconflow', 'baidu', 'google'])
    
    def test_get_recommended_services_with_data(self):
        """测试有数据时的推荐服务"""
        # 添加一些性能数据
        self.selector.update_service_performance("baidu", 0.7, 2.0, True)
        self.selector.update_service_performance("baidu", 0.8, 1.8, True)
        self.selector.update_service_performance("google", 0.9, 1.2, True)
        self.selector.update_service_performance("google", 0.85, 1.5, True)
        self.selector.update_service_performance("siliconflow", 0.95, 1.0, True)
        
        recommended = self.selector.get_recommended_services(max_services=2)
        
        # 验证推荐结果
        self.assertLessEqual(len(recommended), 2)
        self.assertIn("siliconflow", recommended)  # 应该包含表现最好的服务
    
    def test_should_use_single_service(self):
        """测试是否应该使用单个服务"""
        # 添加高质量服务数据
        for _ in range(15):
            self.selector.update_service_performance("siliconflow", 0.9, 1.0, True)
        
        # 应该推荐使用单个服务
        self.assertTrue(self.selector.should_use_single_service("siliconflow"))
        
        # 低质量服务不应该单独使用
        for _ in range(15):
            self.selector.update_service_performance("poor_service", 0.5, 3.0, True)
        
        self.assertFalse(self.selector.should_use_single_service("poor_service"))
    
    def test_should_use_single_service_insufficient_data(self):
        """测试数据不足时不应该使用单个服务"""
        # 只有少量数据
        self.selector.update_service_performance("baidu", 0.9, 1.0, True)
        
        # 数据不足，不应该单独使用
        self.assertFalse(self.selector.should_use_single_service("baidu"))


if __name__ == '__main__':
    unittest.main()