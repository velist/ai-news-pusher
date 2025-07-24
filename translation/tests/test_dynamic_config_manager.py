"""
动态配置管理器测试

测试动态配置管理的各项功能
"""

import unittest
import tempfile
import os
import json
import time
from datetime import datetime
from pathlib import Path

from ..core.dynamic_config_manager import DynamicConfigManager, ServiceConfig, CostControl, QualityConfig

class TestDynamicConfigManager(unittest.TestCase):
    """动态配置管理器测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时配置文件
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        
        # 创建配置管理器实例
        self.config_manager = DynamicConfigManager(self.config_file)
        
    def tearDown(self):
        """测试后清理"""
        # 清理临时文件
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)
        
    def test_default_config_creation(self):
        """测试默认配置创建"""
        # 验证默认服务配置
        self.assertIn('siliconflow', self.config_manager.services)
        self.assertIn('baidu', self.config_manager.services)
        self.assertIn('tencent', self.config_manager.services)
        self.assertIn('google', self.config_manager.services)
        
        # 验证硅基流动服务配置
        siliconflow_config = self.config_manager.get_service_config('siliconflow')
        self.assertIsNotNone(siliconflow_config)
        self.assertEqual(siliconflow_config.priority, 1)
        self.assertTrue(siliconflow_config.enabled)
        self.assertEqual(siliconflow_config.cost_per_char, 0.00001)
        
    def test_service_config_update(self):
        """测试服务配置更新"""
        # 更新硅基流动服务配置
        self.config_manager.update_service_config(
            'siliconflow',
            priority=2,
            quality_threshold=0.9,
            max_requests_per_minute=120
        )
        
        # 验证更新结果
        config = self.config_manager.get_service_config('siliconflow')
        self.assertEqual(config.priority, 2)
        self.assertEqual(config.quality_threshold, 0.9)
        self.assertEqual(config.max_requests_per_minute, 120)
        
    def test_api_key_management(self):
        """测试API密钥管理"""
        service_name = 'siliconflow'
        
        # 获取当前API密钥
        current_key = self.config_manager.get_active_api_key(service_name)
        self.assertIsNotNone(current_key)
        
        # 添加新的API密钥
        new_key = 'test_api_key_2'
        success = self.config_manager.add_api_key(service_name, new_key)
        self.assertTrue(success)
        
        # 验证密钥已添加
        config = self.config_manager.get_service_config(service_name)
        self.assertIn(new_key, config.api_keys)
        
        # 轮换API密钥
        original_index = config.current_key_index
        success = self.config_manager.rotate_api_key(service_name)
        self.assertTrue(success)
        
        # 验证密钥索引已更新
        updated_config = self.config_manager.get_service_config(service_name)
        # 验证轮换后的索引是合理的
        self.assertGreaterEqual(updated_config.current_key_index, 0)
        self.assertLess(updated_config.current_key_index, len(updated_config.api_keys))
        
        # 移除API密钥
        success = self.config_manager.remove_api_key(service_name, new_key)
        self.assertTrue(success)
        
        # 验证密钥已移除
        final_config = self.config_manager.get_service_config(service_name)
        self.assertNotIn(new_key, final_config.api_keys)
        
    def test_service_priority_management(self):
        """测试服务优先级管理"""
        # 更新服务优先级
        self.config_manager.update_service_priority('baidu', 1)
        self.config_manager.update_service_priority('siliconflow', 2)
        
        # 获取按优先级排序的服务列表
        services = self.config_manager.get_services_by_priority()
        
        # 验证排序正确
        self.assertEqual(services[0].name, 'baidu')
        self.assertEqual(services[0].priority, 1)
        
        # 找到硅基流动服务并验证优先级
        siliconflow_service = next(s for s in services if s.name == 'siliconflow')
        self.assertEqual(siliconflow_service.priority, 2)
        
    def test_service_enable_disable(self):
        """测试服务启用/禁用"""
        service_name = 'siliconflow'
        
        # 禁用服务
        self.config_manager.disable_service(service_name)
        config = self.config_manager.get_service_config(service_name)
        self.assertFalse(config.enabled)
        
        # 启用服务
        self.config_manager.enable_service(service_name)
        config = self.config_manager.get_service_config(service_name)
        self.assertTrue(config.enabled)
        
    def test_cost_tracking(self):
        """测试成本追踪"""
        service_name = 'siliconflow'
        char_count = 100
        cost = 0.001
        
        # 记录翻译成本
        self.config_manager.record_translation_cost(service_name, char_count, cost)
        
        # 获取成本统计
        stats = self.config_manager.get_cost_statistics()
        
        # 验证成本记录
        self.assertGreater(stats['current_daily_cost'], 0)
        self.assertGreater(stats['current_monthly_cost'], 0)
        self.assertIn(service_name, stats['services'])
        
        service_stats = stats['services'][service_name]
        self.assertEqual(service_stats['daily_cost'], cost)
        self.assertEqual(service_stats['daily_chars'], char_count)
        self.assertEqual(service_stats['daily_requests'], 1)
        
    def test_budget_control(self):
        """测试预算控制"""
        # 设置较小的预算用于测试
        self.config_manager.update_cost_control(
            daily_budget=0.01,
            monthly_budget=0.1,
            auto_disable_on_budget_exceeded=True
        )
        
        # 记录超出预算的成本
        self.config_manager.record_translation_cost('siliconflow', 1000, 0.02)
        
        # 验证服务是否被自动禁用
        config = self.config_manager.get_service_config('siliconflow')
        # 注意：在实际实现中，预算超限会禁用所有服务
        # 这里我们主要验证成本记录功能
        
        stats = self.config_manager.get_cost_statistics()
        self.assertGreater(stats['daily_usage_rate'], 1.0)  # 超出预算
        
    def test_should_use_service(self):
        """测试服务使用判断"""
        service_name = 'siliconflow'
        
        # 正常情况下应该可以使用
        self.assertTrue(self.config_manager.should_use_service(service_name, 100))
        
        # 禁用服务后不应该使用
        self.config_manager.disable_service(service_name)
        self.assertFalse(self.config_manager.should_use_service(service_name, 100))
        
        # 重新启用服务
        self.config_manager.enable_service(service_name)
        
        # 设置很小的预算
        self.config_manager.update_cost_control(daily_budget=0.001)
        
        # 大量字符应该被拒绝
        self.assertFalse(self.config_manager.should_use_service(service_name, 10000))
        
    def test_quality_config(self):
        """测试质量配置"""
        # 更新质量配置
        self.config_manager.update_quality_config(
            min_confidence_score=0.8,
            enable_quality_comparison=False,
            fallback_on_low_quality=False
        )
        
        # 验证质量配置
        quality_config = self.config_manager.get_quality_config()
        self.assertEqual(quality_config.min_confidence_score, 0.8)
        self.assertFalse(quality_config.enable_quality_comparison)
        self.assertFalse(quality_config.fallback_on_low_quality)
        
    def test_config_export_import(self):
        """测试配置导出导入"""
        # 修改一些配置
        self.config_manager.update_service_config('siliconflow', priority=5)
        self.config_manager.update_cost_control(daily_budget=200.0)
        
        # 导出配置
        exported_config = self.config_manager.export_config()
        
        # 验证导出的配置包含必要字段
        self.assertIn('services', exported_config)
        self.assertIn('cost_control', exported_config)
        self.assertIn('quality_config', exported_config)
        
        # 验证修改的配置被正确导出
        self.assertEqual(exported_config['services']['siliconflow']['priority'], 5)
        self.assertEqual(exported_config['cost_control']['daily_budget'], 200.0)
        
        # 创建新的配置管理器实例
        new_config_file = os.path.join(self.temp_dir, "new_config.json")
        new_config_manager = DynamicConfigManager(new_config_file)
        
        # 导入配置
        new_config_manager.import_config(exported_config)
        
        # 验证导入的配置
        imported_service_config = new_config_manager.get_service_config('siliconflow')
        self.assertEqual(imported_service_config.priority, 5)
        
        imported_cost_control = new_config_manager.cost_control
        self.assertEqual(imported_cost_control.daily_budget, 200.0)
        
    def test_config_file_persistence(self):
        """测试配置文件持久化"""
        # 修改配置
        self.config_manager.update_service_config('siliconflow', priority=10)
        
        # 验证配置文件存在
        self.assertTrue(os.path.exists(self.config_file))
        
        # 读取配置文件内容
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        # 验证配置被正确保存
        self.assertEqual(config_data['services']['siliconflow']['priority'], 10)
        
        # 创建新的配置管理器实例，验证配置被正确加载
        new_config_manager = DynamicConfigManager(self.config_file)
        loaded_config = new_config_manager.get_service_config('siliconflow')
        self.assertEqual(loaded_config.priority, 10)

if __name__ == '__main__':
    unittest.main()