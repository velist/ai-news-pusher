"""
托管翻译服务测试

测试具备动态配置管理功能的翻译服务
"""

import unittest
import tempfile
import os
import time
from unittest.mock import Mock, patch

from ..services.managed_translation_service import ManagedTranslationService
from ..core.interfaces import TranslationResult
from datetime import datetime

class TestManagedTranslationService(unittest.TestCase):
    """托管翻译服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_managed_config.json")
        
        # 创建托管翻译服务实例（禁用Web界面以避免端口冲突）
        self.managed_service = ManagedTranslationService(
            config_file=self.config_file,
            enable_web_interface=False
        )
        
    def tearDown(self):
        """测试后清理"""
        # 关闭服务
        self.managed_service.shutdown()
        
        # 清理临时文件
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
        
    def test_service_initialization(self):
        """测试服务初始化"""
        # 验证配置管理器已创建
        self.assertIsNotNone(self.managed_service.config_manager)
        
        # 验证服务状态
        status = self.managed_service.get_service_status()
        self.assertIn('enabled_services', status)
        self.assertIn('total_services', status)
        self.assertIn('cost_statistics', status)
        self.assertIn('service_statistics', status)
        
    def test_config_manager_access(self):
        """测试配置管理器访问"""
        config_manager = self.managed_service.get_config_manager()
        self.assertIsNotNone(config_manager)
        
        # 测试配置更新
        config_manager.update_service_config('siliconflow', priority=5)
        
        # 验证配置更新
        config = config_manager.get_service_config('siliconflow')
        self.assertEqual(config.priority, 5)
        
    @patch('translation.services.siliconflow_translator.SiliconFlowTranslator')
    def test_translation_with_mock_service(self, mock_translator_class):
        """测试使用模拟服务进行翻译"""
        # 创建模拟翻译器实例
        mock_translator = Mock()
        mock_translator_class.return_value = mock_translator
        
        # 设置模拟翻译结果
        mock_result = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh",
            service_name="siliconflow",
            confidence_score=0.95,
            timestamp=datetime.now()
        )
        mock_translator.translate_text.return_value = mock_result
        
        # 执行翻译
        result = self.managed_service.translate_text("Hello world")
        
        # 验证翻译结果
        self.assertEqual(result.translated_text, "你好世界")
        self.assertEqual(result.service_name, "siliconflow")
        self.assertEqual(result.confidence_score, 0.95)
        
        # 验证模拟服务被调用
        mock_translator.translate_text.assert_called_once_with("Hello world", "en", "zh")
        
    def test_empty_text_translation(self):
        """测试空文本翻译"""
        # 测试空字符串
        result = self.managed_service.translate_text("")
        self.assertEqual(result.original_text, "")
        self.assertEqual(result.translated_text, "")
        self.assertEqual(result.service_name, "none")
        
        # 测试只有空格的字符串
        result = self.managed_service.translate_text("   ")
        self.assertEqual(result.original_text, "   ")
        self.assertEqual(result.translated_text, "   ")
        self.assertEqual(result.service_name, "none")
        
    def test_batch_translation(self):
        """测试批量翻译"""
        texts = ["Hello", "World", "Test"]
        
        # 由于没有真实的API密钥，这里主要测试批量处理逻辑
        results = self.managed_service.translate_batch(texts)
        
        # 验证结果数量
        self.assertEqual(len(results), len(texts))
        
        # 验证每个结果都有对应的原文
        for i, result in enumerate(results):
            self.assertEqual(result.original_text, texts[i])
            
    def test_service_statistics_tracking(self):
        """测试服务统计追踪"""
        # 获取初始统计
        initial_status = self.managed_service.get_service_status()
        initial_stats = initial_status['service_statistics']
        
        # 执行一次翻译（会失败，但会记录统计）
        self.managed_service.translate_text("Test translation")
        
        # 获取更新后的统计
        updated_status = self.managed_service.get_service_status()
        updated_stats = updated_status['service_statistics']
        
        # 验证统计信息结构
        self.assertIsInstance(updated_stats, dict)
        
    def test_cost_control_integration(self):
        """测试成本控制集成"""
        config_manager = self.managed_service.get_config_manager()
        
        # 设置很小的预算
        config_manager.update_cost_control(
            daily_budget=0.001,
            monthly_budget=0.01
        )
        
        # 尝试翻译大量文本（应该被预算限制阻止）
        large_text = "This is a very long text " * 1000
        result = self.managed_service.translate_text(large_text)
        
        # 验证翻译结果（可能使用降级方案）
        self.assertIsNotNone(result)
        self.assertEqual(result.original_text, large_text)
        
    def test_service_priority_handling(self):
        """测试服务优先级处理"""
        config_manager = self.managed_service.get_config_manager()
        
        # 调整服务优先级
        config_manager.update_service_priority('baidu', 1)
        config_manager.update_service_priority('siliconflow', 2)
        
        # 获取按优先级排序的服务
        services = config_manager.get_services_by_priority()
        
        # 验证优先级排序
        enabled_services = [s for s in services if s.enabled]
        if len(enabled_services) >= 2:
            self.assertLessEqual(enabled_services[0].priority, enabled_services[1].priority)
            
    def test_service_enable_disable_integration(self):
        """测试服务启用/禁用集成"""
        config_manager = self.managed_service.get_config_manager()
        
        # 禁用所有服务
        for service_name in config_manager.services:
            config_manager.disable_service(service_name)
            
        # 尝试翻译（应该使用降级方案）
        result = self.managed_service.translate_text("Test with all services disabled")
        
        # 验证使用了降级方案
        self.assertIsNotNone(result)
        self.assertIn(result.service_name, ['rule_based_fallback', 'fallback_original'])
        
        # 重新启用一个服务
        config_manager.enable_service('siliconflow')
        
        # 验证服务状态
        status = self.managed_service.get_service_status()
        self.assertEqual(status['enabled_services'], 1)
        
    def test_quality_threshold_enforcement(self):
        """测试质量阈值执行"""
        config_manager = self.managed_service.get_config_manager()
        
        # 设置很高的质量阈值
        config_manager.update_service_config('siliconflow', quality_threshold=0.99)
        
        # 由于模拟的翻译结果可能不满足高质量阈值，
        # 系统应该尝试其他服务或使用降级方案
        result = self.managed_service.translate_text("Quality test")
        
        # 验证翻译结果存在
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.translated_text)
        
    def test_api_key_rotation_integration(self):
        """测试API密钥轮换集成"""
        config_manager = self.managed_service.get_config_manager()
        
        # 添加额外的API密钥
        config_manager.add_api_key('siliconflow', 'test_key_2')
        config_manager.add_api_key('siliconflow', 'test_key_3')
        
        # 获取当前密钥索引
        config = config_manager.get_service_config('siliconflow')
        original_index = config.current_key_index
        
        # 轮换密钥
        success = config_manager.rotate_api_key('siliconflow')
        self.assertTrue(success)
        
        # 验证密钥索引已更改
        updated_config = config_manager.get_service_config('siliconflow')
        self.assertNotEqual(updated_config.current_key_index, original_index)
        
    def test_fallback_translation(self):
        """测试降级翻译"""
        # 禁用所有外部翻译服务
        config_manager = self.managed_service.get_config_manager()
        for service_name in config_manager.services:
            config_manager.disable_service(service_name)
            
        # 测试降级翻译
        result = self.managed_service._fallback_translate("Hello world", "en", "zh")
        
        # 验证降级翻译结果
        self.assertIsNotNone(result)
        self.assertEqual(result.original_text, "Hello world")
        self.assertIn(result.service_name, ['rule_based_fallback', 'fallback_original'])
        
    def test_web_interface_disabled(self):
        """测试Web界面禁用状态"""
        # 验证Web界面已禁用
        self.assertIsNone(self.managed_service.web_server)
        
        # 验证服务状态中Web界面URL为None
        status = self.managed_service.get_service_status()
        self.assertIsNone(status['web_interface_url'])

if __name__ == '__main__':
    unittest.main()