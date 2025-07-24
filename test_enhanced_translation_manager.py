#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强的翻译管理器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translation.services.enhanced_translation_manager import EnhancedTranslationManager


def test_enhanced_translation_manager():
    """测试增强翻译管理器的功能"""
    
    print("=== 增强翻译管理器测试 ===")
    
    # 配置信息（使用模拟配置）
    config = {
        'siliconflow': {
            'api_key': 'sk-test-key'  # 测试用的API密钥
        }
    }
    
    # 初始化管理器
    manager = EnhancedTranslationManager(config)
    
    print(f"可用翻译服务数量: {len(manager.services)}")
    print(f"服务列表: {[service.get_service_name() for service in manager.services]}")
    
    # 测试文本
    test_texts = [
        "OpenAI released ChatGPT, a revolutionary AI chatbot that can engage in human-like conversations.",
        "Apple reported record revenue of $100 billion in Q4 2023, driven by strong iPhone sales.",
        "Tesla's stock price surged 15% after announcing breakthrough in autonomous driving technology."
    ]
    
    print("\n=== 翻译质量评估测试 ===")
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n--- 测试 {i} ---")
        print(f"原文: {text}")
        
        try:
            # 执行带质量评估的翻译
            result = manager.translate_with_quality_assessment(
                text, 
                use_comparison=False  # 先测试单服务模式
            )
            
            if result['success']:
                best_translation = result['best_translation']
                quality_scores = result['quality_scores'][0]
                
                print(f"翻译结果: {best_translation.translated_text}")
                print(f"服务: {best_translation.service_name}")
                print(f"置信度: {best_translation.confidence_score:.3f}")
                print(f"质量评分:")
                print(f"  - 总体评分: {quality_scores.overall_score:.3f}")
                print(f"  - 语义准确性: {quality_scores.semantic_accuracy:.3f}")
                print(f"  - 流畅度: {quality_scores.fluency:.3f}")
                print(f"  - 术语准确性: {quality_scores.terminology_accuracy:.3f}")
                print(f"  - 上下文一致性: {quality_scores.context_consistency:.3f}")
                
                # 模拟用户反馈
                feedback_success = manager.submit_user_feedback(
                    translation_id=result['translation_id'],
                    original_text=text,
                    translated_text=best_translation.translated_text,
                    service_name=best_translation.service_name,
                    feedback_type='quality_rating',
                    rating=4.0,
                    comments="翻译质量不错，术语处理得当"
                )
                
                if feedback_success:
                    print("✓ 用户反馈已提交")
                
            else:
                print(f"翻译失败: {result.get('error', '未知错误')}")
        
        except Exception as e:
            print(f"测试失败: {e}")
    
    # 获取统计信息
    print("\n=== 翻译统计信息 ===")
    stats = manager.get_translation_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 获取服务推荐
    print("\n=== 服务推荐信息 ===")
    recommendations = manager.get_service_recommendations()
    print(f"推荐服务: {recommendations['recommended_services']}")
    print(f"是否使用多服务比较: {recommendations['should_use_comparison']}")
    
    # 测试优化翻译功能
    print("\n=== 优化翻译测试 ===")
    optimization_text = "Google announced new AI features for Android smartphones."
    print(f"原文: {optimization_text}")
    
    try:
        optimized_result = manager.optimize_translation_quality(optimization_text)
        
        if optimized_result['success']:
            best_translation = optimized_result['best_translation']
            optimization_info = optimized_result.get('optimization_info', {})
            
            print(f"优化翻译结果: {best_translation.translated_text}")
            print(f"使用策略: {optimization_info.get('strategy_used', 'unknown')}")
            print(f"质量已优化: {optimization_info.get('quality_optimized', False)}")
        else:
            print(f"优化翻译失败: {optimized_result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"优化翻译测试失败: {e}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_enhanced_translation_manager()