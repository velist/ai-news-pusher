#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版翻译功能
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translation.services.enhanced_news_translator import EnhancedNewsTranslator


def test_title_translation():
    """测试标题翻译功能"""
    print("🧪 测试标题翻译功能")
    print("=" * 50)
    
    # 初始化翻译器
    try:
        translator = EnhancedNewsTranslator()
        print("✅ 翻译器初始化成功")
    except Exception as e:
        print(f"❌ 翻译器初始化失败: {e}")
        return
    
    # 测试用例
    test_titles = [
        {
            "title": "OpenAI releases GPT-4 with improved reasoning capabilities",
            "category": "AI科技"
        },
        {
            "title": "Microsoft integrates AI into Office 365 suite",
            "category": "AI科技"
        },
        {
            "title": "PlayStation 5 Pro announced with enhanced graphics",
            "category": "游戏科技"
        },
        {
            "title": "Bitcoin reaches new all-time high amid institutional adoption",
            "category": "经济金融"
        },
        {
            "title": "Apple unveils new MacBook Pro with M3 chip",
            "category": "科技创新"
        }
    ]
    
    for i, test_case in enumerate(test_titles, 1):
        print(f"\n📝 测试用例 {i}:")
        print(f"原文: {test_case['title']}")
        print(f"类别: {test_case['category']}")
        
        try:
            result = translator.translate_news_title(test_case['title'], test_case['category'])
            
            if result.error_message:
                print(f"❌ 翻译失败: {result.error_message}")
            else:
                print(f"译文: {result.translated_text}")
                print(f"置信度: {result.confidence_score:.2f}")
                print(f"服务: {result.service_name}")
        except Exception as e:
            print(f"❌ 翻译异常: {str(e)}")


def test_description_translation():
    """测试描述翻译功能"""
    print("\n\n🧪 测试描述翻译功能")
    print("=" * 50)
    
    # 初始化翻译器
    try:
        translator = EnhancedNewsTranslator()
        print("✅ 翻译器初始化成功")
    except Exception as e:
        print(f"❌ 翻译器初始化失败: {e}")
        return
    
    # 测试用例
    test_descriptions = [
        {
            "description": "OpenAI has announced a major breakthrough in artificial intelligence with the release of GPT-4, featuring enhanced reasoning capabilities and improved performance across various tasks.",
            "title": "OpenAI releases GPT-4 with improved reasoning capabilities",
            "category": "AI科技"
        },
        {
            "description": "The new PlayStation 5 Pro console promises to deliver unprecedented gaming experiences with its advanced GPU architecture, supporting 4K gaming at 60fps and ray tracing technology. Sony has partnered with leading game developers to optimize titles for the new hardware, ensuring players get the most immersive gaming experience possible. The console will be available in limited quantities starting next month, with pre-orders beginning this week.",
            "title": "PlayStation 5 Pro announced with enhanced graphics",
            "category": "游戏科技"
        }
    ]
    
    for i, test_case in enumerate(test_descriptions, 1):
        print(f"\n📄 测试用例 {i}:")
        print(f"标题: {test_case['title']}")
        print(f"类别: {test_case['category']}")
        print(f"原文长度: {len(test_case['description'])} 字符")
        print(f"原文: {test_case['description'][:100]}...")
        
        try:
            result = translator.translate_news_description(
                test_case['description'], 
                test_case['title'], 
                test_case['category']
            )
            
            if result.error_message:
                print(f"❌ 翻译失败: {result.error_message}")
            else:
                print(f"译文长度: {len(result.translated_text)} 字符")
                print(f"译文: {result.translated_text[:200]}...")
                print(f"置信度: {result.confidence_score:.2f}")
                print(f"服务: {result.service_name}")
        except Exception as e:
            print(f"❌ 翻译异常: {str(e)}")


def test_news_accumulator_integration():
    """测试新闻累积器集成"""
    print("\n\n🧪 测试新闻累积器集成")
    print("=" * 50)
    
    try:
        from news_accumulator import AINewsAccumulator
        
        accumulator = AINewsAccumulator()
        print("✅ 新闻累积器初始化成功")
        
        # 测试翻译功能
        test_title = "AI breakthrough in machine learning research"
        test_description = "Researchers have developed a new neural network architecture that significantly improves performance on natural language processing tasks."
        
        print(f"\n📝 测试标题翻译:")
        print(f"原文: {test_title}")
        translated_title = accumulator.translate_title(test_title, "AI科技")
        print(f"译文: {translated_title}")
        
        print(f"\n📄 测试描述翻译:")
        print(f"原文: {test_description}")
        translated_description = accumulator.translate_description(test_description, test_title, "AI科技")
        print(f"译文: {translated_description}")
        
        # 测试翻译元数据生成
        print(f"\n📊 测试翻译元数据:")
        metadata = accumulator._get_translation_metadata(
            test_title, test_description,
            translated_title, translated_description,
            "AI科技"
        )
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"❌ 集成测试失败: {str(e)}")


def main():
    """主测试函数"""
    print("🚀 开始增强版翻译功能测试")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("⚠️ 未设置SILICONFLOW_API_KEY环境变量")
        print("请设置API密钥后重新运行测试")
        return
    
    print(f"✅ API密钥已配置: {api_key[:10]}...")
    
    # 运行测试
    test_title_translation()
    test_description_translation()
    test_news_accumulator_integration()
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")


if __name__ == "__main__":
    main()