"""
托管翻译服务使用示例

演示如何使用具备动态配置管理功能的翻译服务
"""

import time
import logging
from services.managed_translation_service import ManagedTranslationService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("🚀 托管翻译服务演示")
    print("=" * 50)
    
    # 创建托管翻译服务实例
    # Web配置界面将在 http://localhost:8080 启动
    managed_service = ManagedTranslationService(
        config_file="config/managed_translation_config.json",
        enable_web_interface=True,
        web_port=8080
    )
    
    try:
        print(f"📊 Web配置界面: {managed_service.get_service_status()['web_interface_url']}")
        print("💡 您可以通过Web界面实时调整翻译服务配置")
        print()
        
        # 测试文本
        test_texts = [
            "OpenAI has released a new version of ChatGPT with improved capabilities.",
            "The artificial intelligence revolution is transforming various industries.",
            "Machine learning algorithms are becoming more sophisticated every day.",
            "Blockchain technology offers new possibilities for decentralized applications.",
            "Cloud computing has revolutionized how businesses operate and scale."
        ]
        
        print("🔄 开始翻译测试...")
        print("-" * 30)
        
        # 逐个翻译测试
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 测试 {i}: {text[:50]}...")
            
            start_time = time.time()
            result = managed_service.translate_text(text)
            end_time = time.time()
            
            print(f"🎯 翻译结果: {result.translated_text}")
            print(f"🔧 使用服务: {result.service_name}")
            print(f"📈 置信度: {result.confidence_score:.2f}")
            print(f"⏱️  耗时: {end_time - start_time:.2f}秒")
            
            # 短暂延迟，便于观察
            time.sleep(1)
            
        print("\n" + "=" * 50)
        print("📊 服务状态统计")
        print("-" * 30)
        
        # 获取服务状态
        status = managed_service.get_service_status()
        
        print(f"✅ 启用服务数: {status['enabled_services']}")
        print(f"📦 总服务数: {status['total_services']}")
        
        # 成本统计
        cost_stats = status['cost_statistics']
        print(f"💰 今日成本: ¥{cost_stats['current_daily_cost']:.4f}")
        print(f"📅 本月成本: ¥{cost_stats['current_monthly_cost']:.4f}")
        print(f"📊 今日预算使用率: {cost_stats['daily_usage_rate']:.1%}")
        print(f"📈 本月预算使用率: {cost_stats['monthly_usage_rate']:.1%}")
        
        # 服务统计
        print("\n🔧 各服务统计:")
        for service_name, stats in status['service_statistics'].items():
            if stats['total_requests'] > 0:
                success_rate = stats['successful_requests'] / stats['total_requests']
                print(f"  {service_name}:")
                print(f"    请求总数: {stats['total_requests']}")
                print(f"    成功率: {success_rate:.1%}")
                print(f"    总字符数: {stats['total_chars']}")
                print(f"    总成本: ¥{stats['total_cost']:.4f}")
                print(f"    平均响应时间: {stats['avg_response_time']:.2f}秒")
                
        print("\n" + "=" * 50)
        print("🎛️  配置管理演示")
        print("-" * 30)
        
        # 获取配置管理器
        config_manager = managed_service.get_config_manager()
        
        # 演示动态配置调整
        print("📝 当前硅基流动服务配置:")
        siliconflow_config = config_manager.get_service_config('siliconflow')
        if siliconflow_config:
            print(f"  优先级: {siliconflow_config.priority}")
            print(f"  启用状态: {siliconflow_config.enabled}")
            print(f"  质量阈值: {siliconflow_config.quality_threshold}")
            print(f"  每字符成本: ¥{siliconflow_config.cost_per_char:.6f}")
            
        # 演示配置更新
        print("\n🔧 演示配置更新...")
        original_threshold = siliconflow_config.quality_threshold if siliconflow_config else 0.85
        
        # 临时调整质量阈值
        config_manager.update_service_config('siliconflow', quality_threshold=0.9)
        print("✅ 已将硅基流动质量阈值调整为 0.9")
        
        # 测试一次翻译，观察配置变更效果
        test_result = managed_service.translate_text("This is a configuration test.")
        print(f"🧪 配置测试翻译: {test_result.translated_text}")
        print(f"🔧 使用服务: {test_result.service_name}")
        
        # 恢复原始配置
        config_manager.update_service_config('siliconflow', quality_threshold=original_threshold)
        print(f"🔄 已恢复硅基流动质量阈值为 {original_threshold}")
        
        print("\n" + "=" * 50)
        print("🌐 Web界面功能说明")
        print("-" * 30)
        print("通过Web界面，您可以:")
        print("• 📊 实时查看成本统计和预算使用情况")
        print("• ⚙️  动态调整各翻译服务的配置参数")
        print("• 🔑 管理API密钥，支持轮换和负载均衡")
        print("• 🎯 调整服务优先级和启用/禁用服务")
        print("• 💰 设置成本控制和预算限制")
        print("• 📈 监控翻译质量和服务性能")
        
        print(f"\n🔗 请访问: {status['web_interface_url']}")
        print("💡 建议在浏览器中打开Web界面，体验实时配置管理功能")
        
        # 保持服务运行一段时间，便于用户测试Web界面
        print("\n⏳ 服务将保持运行60秒，便于您测试Web界面...")
        print("   按 Ctrl+C 可提前退出")
        
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n⚡ 用户中断，准备退出...")
            
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        
    finally:
        # 关闭服务
        print("\n🔚 正在关闭托管翻译服务...")
        managed_service.shutdown()
        print("✅ 服务已关闭")

if __name__ == "__main__":
    main()