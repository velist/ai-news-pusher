#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版新闻翻译器的翻译质量优化功能
"""

import os
import sys
from datetime import datetime

# 添加translation模块到路径
sys.path.append('translation')

from translation.services.enhanced_news_translator import EnhancedNewsTranslator

def test_title_translation():
    """测试标题翻译质量"""
    print("🔤 测试标题翻译质量优化")
    print("=" * 60)
    
    # 初始化翻译器
    api_key = "sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa"
    translator = EnhancedNewsTranslator(api_key=api_key)
    
    # 测试用例
    test_cases = [
        {
            'title': 'OpenAI Releases GPT-4 Turbo with Enhanced Capabilities',
            'category': 'AI科技',
            'expected_terms': ['OpenAI', 'GPT-4']
        },
        {
            'title': 'PlayStation 5 Pro Launches with 8K Gaming Support',
            'category': '游戏科技',
            'expected_terms': ['PlayStation', '8K']
        },
        {
            'title': 'Tesla Stock Surges 15% After Q3 Earnings Beat',
            'category': '经济金融',
            'expected_terms': ['特斯拉', '15%']
        },
        {
            'title': 'Microsoft Azure Introduces New AI Services for Enterprises',
            'category': '科技创新',
            'expected_terms': ['微软', 'Azure', 'AI']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📰 测试案例 {i}: {test_case['category']}")
        print(f"原标题: {test_case['title']}")
        
        try:
            result = translator.translate_news_title(test_case['title'], test_case['category'])
            
            print(f"中文标题: {result.translated_text}")
            print(f"置信度: {result.confidence_score:.3f}")
            print(f"服务: {result.service_name}")
            
            # 检查专业术语保留
            terms_preserved = []
            for term in test_case['expected_terms']:
                if term in result.translated_text:
                    terms_preserved.append(term)
            
            print(f"术语保留: {', '.join(terms_preserved) if terms_preserved else '无'}")
            
            if result.error_message:
                print(f"❌ 错误: {result.error_message}")
            else:
                print("✅ 翻译成功")
                
        except Exception as e:
            print(f"❌ 翻译失败: {str(e)}")
        
        print("-" * 40)

def test_description_translation():
    """测试描述翻译质量"""
    print("\n📄 测试描述翻译质量优化")
    print("=" * 60)
    
    # 初始化翻译器
    api_key = "sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa"
    translator = EnhancedNewsTranslator(api_key=api_key)
    
    # 测试用例
    test_cases = [
        {
            'title': 'OpenAI Announces ChatGPT-5',
            'description': 'OpenAI has announced the development of ChatGPT-5, featuring advanced reasoning capabilities and multimodal processing. The new model will support text, image, and audio inputs simultaneously, marking a significant leap in AI technology. Beta testing is expected to begin in early 2024.',
            'category': 'AI科技'
        },
        {
            'title': 'Gaming Industry Revenue Hits Record High',
            'description': 'The global gaming industry has reached unprecedented revenue levels, with mobile gaming leading the growth. Major publishers report strong quarterly earnings, driven by popular titles and in-game purchases. The trend towards cloud gaming and subscription services continues to reshape the market landscape.',
            'category': '游戏科技'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📰 测试案例 {i}: {test_case['category']}")
        print(f"标题: {test_case['title']}")
        print(f"原描述: {test_case['description']}")
        
        try:
            result = translator.translate_news_description(
                test_case['description'], 
                test_case['title'], 
                test_case['category']
            )
            
            print(f"\n中文描述: {result.translated_text}")
            print(f"置信度: {result.confidence_score:.3f}")
            print(f"服务: {result.service_name}")
            
            if result.error_message:
                print(f"❌ 错误: {result.error_message}")
            else:
                print("✅ 翻译成功")
                
        except Exception as e:
            print(f"❌ 翻译失败: {str(e)}")
        
        print("-" * 40)

def test_long_description_segmentation():
    """测试长文本分段翻译"""
    print("\n📄 测试长文本分段翻译")
    print("=" * 60)
    
    # 初始化翻译器
    api_key = "sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa"
    translator = EnhancedNewsTranslator(api_key=api_key)
    
    # 长文本测试用例
    long_description = """
    Artificial Intelligence has reached a pivotal moment in its development, with large language models like GPT-4 and Claude demonstrating unprecedented capabilities in natural language understanding and generation. These models are being integrated into various applications, from customer service chatbots to creative writing assistants, fundamentally changing how we interact with technology.
    
    The impact extends beyond consumer applications. In healthcare, AI is being used to analyze medical images, predict patient outcomes, and assist in drug discovery. Financial institutions are leveraging machine learning algorithms for fraud detection, risk assessment, and algorithmic trading. The automotive industry is pushing forward with autonomous vehicle technology, promising to revolutionize transportation.
    
    However, these advances come with significant challenges. Concerns about job displacement, privacy, and the potential for AI systems to perpetuate or amplify existing biases are at the forefront of public discourse. Regulatory frameworks are struggling to keep pace with technological development, leading to calls for more comprehensive AI governance.
    
    Looking ahead, the next phase of AI development will likely focus on achieving artificial general intelligence (AGI), where machines can perform any intellectual task that humans can do. While this remains a distant goal, the rapid progress in recent years suggests that significant breakthroughs may be closer than previously anticipated.
    """
    
    print(f"原文长度: {len(long_description)} 字符")
    
    try:
        result = translator.translate_news_description(
            long_description.strip(), 
            "AI Technology Reaches New Milestone", 
            "AI科技"
        )
        
        print(f"\n中文翻译:")
        print(result.translated_text)
        print(f"\n翻译长度: {len(result.translated_text)} 字符")
        print(f"置信度: {result.confidence_score:.3f}")
        print(f"服务: {result.service_name}")
        
        if result.error_message:
            print(f"❌ 错误: {result.error_message}")
        else:
            print("✅ 长文本翻译成功")
            
    except Exception as e:
        print(f"❌ 长文本翻译失败: {str(e)}")

def main():
    """主测试函数"""
    print("🚀 增强版新闻翻译器质量测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # 测试标题翻译
        test_title_translation()
        
        # 测试描述翻译
        test_description_translation()
        
        # 测试长文本分段翻译
        test_long_description_segmentation()
        
        print("\n🎉 所有测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()