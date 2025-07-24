#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动翻译服务使用示例
"""

import os
from translation.services.siliconflow_translator import SiliconFlowTranslator


def demo_siliconflow_models():
    """演示不同硅基流动模型的翻译效果"""
    
    print("=== 硅基流动AI翻译服务演示 ===\n")
    
    # 测试文本
    test_texts = [
        "OpenAI has released a new version of ChatGPT with enhanced reasoning capabilities.",
        "The artificial intelligence revolution is transforming industries worldwide.",
        "Breaking: Tech giant announces breakthrough in quantum computing research."
    ]
    
    # 推荐的模型列表
    recommended_models = [
        {
            "name": "Qwen/Qwen2.5-7B-Instruct",
            "description": "性价比最高，适合大量翻译任务",
            "cost": "极低"
        },
        {
            "name": "Qwen/Qwen2.5-14B-Instruct", 
            "description": "质量更好，适合重要内容翻译",
            "cost": "低"
        },
        {
            "name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
            "description": "英文理解优秀，适合英文新闻翻译",
            "cost": "低"
        },
        {
            "name": "THUDM/glm-4-9b-chat",
            "description": "中文理解好，适合中英互译",
            "cost": "中"
        }
    ]
    
    print("📋 推荐模型列表：")
    for i, model in enumerate(recommended_models, 1):
        print(f"{i}. {model['name']}")
        print(f"   描述: {model['description']}")
        print(f"   成本: {model['cost']}")
        print()
    
    # 演示默认模型
    try:
        print("🚀 使用默认模型 (Qwen2.5-7B-Instruct) 进行翻译演示：")
        print("-" * 60)
        
        # 注意：需要设置环境变量 SILICONFLOW_API_KEY
        translator = SiliconFlowTranslator()
        
        # 获取模型信息
        model_info = translator.get_model_info()
        print(f"当前模型: {model_info['model']}")
        print(f"服务状态: {translator.get_service_status().value}")
        print()
        
        # 单个翻译演示
        print("📝 单个翻译演示：")
        for i, text in enumerate(test_texts, 1):
            print(f"\n{i}. 原文: {text}")
            result = translator.translate_text(text, "en", "zh")
            
            if result.error_message:
                print(f"   ❌ 翻译失败: {result.error_message}")
            else:
                print(f"   ✅ 译文: {result.translated_text}")
                print(f"   📊 置信度: {result.confidence_score:.2f}")
        
        # 批量翻译演示
        print(f"\n{'='*60}")
        print("📦 批量翻译演示：")
        batch_results = translator.translate_batch(test_texts[:2], "en", "zh")
        
        for i, result in enumerate(batch_results, 1):
            print(f"\n{i}. 原文: {result.original_text}")
            if result.error_message:
                print(f"   ❌ 翻译失败: {result.error_message}")
            else:
                print(f"   ✅ 译文: {result.translated_text}")
                print(f"   📊 置信度: {result.confidence_score:.2f}")
        
        # 健康检查演示
        print(f"\n{'='*60}")
        print("🏥 服务健康检查：")
        health = translator.check_health()
        print(f"服务: {health['service']}")
        print(f"模型: {health['model']}")
        print(f"状态: {health['status']}")
        print(f"响应时间: {health.get('response_time', 'N/A'):.3f}秒")
        print(f"功能支持:")
        for feature, supported in health['features'].items():
            status = "✅" if supported else "❌"
            print(f"  {status} {feature}")
            
    except ValueError as e:
        print(f"⚠️ 硅基流动配置错误: {e}")
        print("\n请设置环境变量: SILICONFLOW_API_KEY")
        print("获取API密钥: https://siliconflow.cn")
    except Exception as e:
        print(f"❌ 硅基流动翻译错误: {e}")


def demo_model_comparison():
    """演示不同模型的翻译效果对比"""
    
    print(f"\n{'='*60}")
    print("=== 模型翻译效果对比 ===")
    print("="*60)
    
    test_text = "The breakthrough in artificial intelligence has revolutionized the way we approach complex problem-solving in various industries."
    
    models_to_test = [
        "Qwen/Qwen2.5-7B-Instruct",
        "Qwen/Qwen2.5-14B-Instruct"
    ]
    
    print(f"测试文本: {test_text}\n")
    
    for model_name in models_to_test:
        try:
            print(f"🤖 模型: {model_name}")
            translator = SiliconFlowTranslator(model=model_name)
            
            result = translator.translate_text(test_text, "en", "zh")
            
            if result.error_message:
                print(f"   ❌ 翻译失败: {result.error_message}")
            else:
                print(f"   ✅ 译文: {result.translated_text}")
                print(f"   📊 置信度: {result.confidence_score:.2f}")
                print(f"   ⏱️ 时间: {result.timestamp.strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"   ❌ 模型 {model_name} 测试失败: {str(e)}")
        
        print()


def demo_cost_analysis():
    """演示成本分析"""
    
    print(f"\n{'='*60}")
    print("=== 硅基流动翻译成本分析 ===")
    print("="*60)
    
    # 硅基流动的大概价格（以Qwen2.5-7B为例）
    print("💰 成本优势分析：")
    print()
    
    print("📊 价格对比 (每百万字符)：")
    print("• 百度翻译:     ¥49-58")
    print("• 腾讯翻译:     ¥58")
    print("• Google翻译:   ¥140-280")
    print("• 硅基流动:     ¥2-10 (根据模型不同)")
    print()
    
    print("🎯 硅基流动优势：")
    print("✅ 成本极低 - 比传统翻译API便宜5-20倍")
    print("✅ 质量优秀 - AI大模型理解能力强")
    print("✅ 灵活性高 - 可选择不同模型")
    print("✅ 上下文理解 - 更好的语境翻译")
    print("✅ 专业术语 - 对技术词汇理解更准确")
    print()
    
    print("📈 推荐使用场景：")
    print("• 大量新闻翻译 - 使用Qwen2.5-7B (成本最低)")
    print("• 重要内容翻译 - 使用Qwen2.5-14B (质量更好)")
    print("• 英文新闻专门 - 使用Llama-3.1-8B (英文优势)")
    print("• 中英互译 - 使用GLM-4-9B (中文理解好)")
    print()
    
    # 计算示例成本
    daily_news = 100  # 每天100条新闻
    avg_chars = 200   # 每条平均200字符
    monthly_chars = daily_news * avg_chars * 30
    
    print(f"💡 成本计算示例 (月翻译量: {monthly_chars:,} 字符)：")
    print(f"• 百度翻译: ¥{(monthly_chars/1000000)*49:.2f}")
    print(f"• 腾讯翻译: ¥{(monthly_chars/1000000)*58:.2f}")
    print(f"• Google翻译: ¥{(monthly_chars/1000000)*140:.2f}")
    print(f"• 硅基流动: ¥{(monthly_chars/1000000)*5:.2f} (预估)")
    print()
    
    savings = ((monthly_chars/1000000)*49) - ((monthly_chars/1000000)*5)
    print(f"💰 每月可节省: ¥{savings:.2f} (相比百度翻译)")


if __name__ == "__main__":
    print("🌟 硅基流动翻译服务完整演示")
    print("=" * 60)
    print("注意：请确保已设置环境变量 SILICONFLOW_API_KEY")
    print("获取API密钥: https://siliconflow.cn")
    print()
    
    demo_siliconflow_models()
    demo_model_comparison()
    demo_cost_analysis()