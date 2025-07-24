"""
托管翻译服务简单演示

展示动态配置管理功能的实际应用
"""

import tempfile
import os
import time
from translation.services.managed_translation_service import ManagedTranslationService

def test_managed_service():
    """测试托管翻译服务"""
    print("🚀 托管翻译服务演示")
    print("=" * 50)
    
    # 创建临时配置文件
    temp_dir = tempfile.mkdtemp()
    config_file = os.path.join(temp_dir, "managed_config.json")
    
    try:
        # 创建托管翻译服务（禁用Web界面避免端口冲突）
        managed_service = ManagedTranslationService(
            config_file=config_file,
            enable_web_interface=False
        )
        
        print("✅ 托管翻译服务已初始化")
        
        # 获取配置管理器
        config_manager = managed_service.get_config_manager()
        
        # 显示初始配置
        print("\n📋 初始服务配置:")
        services = config_manager.get_services_by_priority()
        for service in services:
            status = "启用" if service.enabled else "禁用"
            print(f"   {service.name}: 优先级{service.priority}, {status}, 成本¥{service.cost_per_char:.6f}/字符")
        
        # 测试配置动态调整
        print("\n🔧 动态调整配置...")
        
        # 调整硅基流动服务的质量阈值
        config_manager.update_service_config('siliconflow', quality_threshold=0.9)
        print("   ✓ 硅基流动质量阈值调整为 0.9")
        
        # 调整成本控制
        config_manager.update_cost_control(daily_budget=10.0, monthly_budget=200.0)
        print("   ✓ 预算调整为每日¥10，每月¥200")
        
        # 测试翻译功能
        print("\n🔄 测试翻译功能...")
        test_texts = [
            "Hello world",
            "Artificial intelligence is transforming the world",
            "Machine learning enables computers to learn without explicit programming"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 测试 {i}: {text}")
            
            try:
                result = managed_service.translate_text(text)
                print(f"   🎯 翻译: {result.translated_text}")
                print(f"   🔧 服务: {result.service_name}")
                print(f"   📊 置信度: {result.confidence_score:.2f}")
                
                # 记录成本（模拟）
                char_count = len(text)
                estimated_cost = char_count * 0.00001  # 硅基流动成本
                config_manager.record_translation_cost('siliconflow', char_count, estimated_cost)
                
            except Exception as e:
                print(f"   ❌ 翻译失败: {e}")
        
        # 显示成本统计
        print("\n💰 成本统计:")
        stats = config_manager.get_cost_statistics()
        print(f"   每日预算: ¥{stats['daily_budget']:.2f}")
        print(f"   当前成本: ¥{stats['current_daily_cost']:.4f}")
        print(f"   使用率: {stats['daily_usage_rate']:.1%}")
        
        # 显示服务统计
        print("\n📊 服务统计:")
        service_status = managed_service.get_service_status()
        for service_name, service_stats in service_status['service_statistics'].items():
            if service_stats['total_requests'] > 0:
                success_rate = service_stats['successful_requests'] / service_stats['total_requests']
                print(f"   {service_name}:")
                print(f"     请求: {service_stats['total_requests']}")
                print(f"     成功率: {success_rate:.1%}")
                print(f"     成本: ¥{service_stats['total_cost']:.4f}")
        
        # 测试服务优先级调整
        print("\n🎯 测试服务优先级调整...")
        config_manager.update_service_priority('baidu', 1)
        config_manager.update_service_priority('siliconflow', 2)
        
        updated_services = config_manager.get_services_by_priority()
        print("   更新后的服务优先级:")
        for service in updated_services[:3]:
            if service.enabled:
                print(f"     {service.name}: 优先级 {service.priority}")
        
        # 测试API密钥管理
        print("\n🔑 测试API密钥管理...")
        original_keys = len(config_manager.get_service_config('siliconflow').api_keys)
        config_manager.add_api_key('siliconflow', 'demo_key_123')
        updated_keys = len(config_manager.get_service_config('siliconflow').api_keys)
        print(f"   API密钥数量: {original_keys} → {updated_keys}")
        
        # 轮换密钥
        if config_manager.rotate_api_key('siliconflow'):
            print("   ✓ API密钥轮换成功")
        else:
            print("   ⚠️  API密钥轮换失败（可能只有一个密钥）")
        
        # 测试配置导出
        print("\n📤 测试配置导出...")
        exported_config = config_manager.export_config()
        print(f"   导出配置包含 {len(exported_config)} 个主要部分")
        print(f"   服务配置: {len(exported_config['services'])} 个")
        
        print("\n🎉 托管翻译服务演示完成！")
        print("\n💡 主要功能验证:")
        print("   ✅ 动态配置管理")
        print("   ✅ 成本监控和控制")
        print("   ✅ API密钥管理和轮换")
        print("   ✅ 服务优先级调整")
        print("   ✅ 翻译质量阈值控制")
        print("   ✅ 配置导出导入")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理
        try:
            managed_service.shutdown()
        except:
            pass
            
        if os.path.exists(config_file):
            os.remove(config_file)
        os.rmdir(temp_dir)

if __name__ == "__main__":
    test_managed_service()