#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试集成翻译引擎后的新闻系统
"""

import json
from datetime import datetime
from news_accumulator import AINewsAccumulator

def test_news_translation_integration():
    """测试新闻翻译集成功能"""
    print("🚀 测试集成翻译引擎后的新闻系统")
    print("=" * 60)
    
    # 初始化新闻累积器
    accumulator = AINewsAccumulator()
    
    # 模拟新闻数据
    test_articles = [
        {
            'title': 'OpenAI Releases GPT-4 Turbo with Enhanced Reasoning Capabilities',
            'description': 'OpenAI has announced the release of GPT-4 Turbo, featuring improved reasoning capabilities and faster processing speeds. The new model demonstrates significant improvements in complex problem-solving tasks and maintains better context awareness across longer conversations.',
            'url': 'https://example.com/openai-gpt4-turbo',
            'source': {'name': 'TechCrunch'},
            'publishedAt': '2025-07-24T10:00:00Z',
            'image': 'https://example.com/image1.jpg',
            'search_category': 'AI科技'
        },
        {
            'title': 'PlayStation 5 Pro Launches with 8K Gaming and Ray Tracing Support',
            'description': 'Sony has officially launched the PlayStation 5 Pro, featuring enhanced hardware capable of 8K gaming and advanced ray tracing. The console promises to deliver unprecedented gaming experiences with improved graphics and performance.',
            'url': 'https://example.com/ps5-pro-launch',
            'source': {'name': 'GameSpot'},
            'publishedAt': '2025-07-24T09:30:00Z',
            'image': 'https://example.com/image2.jpg',
            'search_category': '游戏科技'
        },
        {
            'title': 'Tesla Stock Surges 20% Following Q3 Earnings Beat',
            'description': 'Tesla shares jumped 20% in after-hours trading following the company\'s third-quarter earnings report, which exceeded analyst expectations. The electric vehicle maker reported record deliveries and improved profit margins.',
            'url': 'https://example.com/tesla-earnings',
            'source': {'name': 'Reuters'},
            'publishedAt': '2025-07-24T08:45:00Z',
            'image': 'https://example.com/image3.jpg',
            'search_category': '经济金融'
        }
    ]
    
    print(f"📰 测试 {len(test_articles)} 条新闻的翻译集成")
    print("-" * 40)
    
    translated_news = []
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n🔄 处理第 {i} 条新闻: {article['search_category']}")
        print(f"原标题: {article['title']}")
        print(f"原描述: {article['description'][:100]}...")
        
        try:
            # 翻译标题
            chinese_title = accumulator.translate_title(
                article['title'], 
                article['search_category']
            )
            
            # 翻译描述
            chinese_description = accumulator.translate_description(
                article['description'],
                article['title'],
                article['search_category']
            )
            
            # 生成翻译元数据
            translation_metadata = accumulator._get_translation_metadata(
                article['title'],
                article['description'],
                chinese_title,
                chinese_description,
                article['search_category']
            )
            
            # 创建新闻项
            news_item = {
                "id": accumulator.generate_news_id(article),
                "title": chinese_title,
                "original_title": article['title'],
                "description": chinese_description,
                "original_description": article['description'],
                "url": article['url'],
                "source": article['source']['name'],
                "publishedAt": article['publishedAt'],
                "image": article['image'],
                "category": accumulator.categorize_news(chinese_title, article['search_category']),
                "importance": accumulator.get_importance_score(chinese_title),
                "added_time": datetime.now().isoformat(),
                "search_category": article['search_category'],
                "translation_metadata": translation_metadata
            }
            
            translated_news.append(news_item)
            
            print(f"✅ 中文标题: {chinese_title}")
            print(f"✅ 中文描述: {chinese_description[:100]}...")
            print(f"📊 翻译质量:")
            print(f"   - 标题置信度: {translation_metadata['title_translation']['confidence']:.3f}")
            print(f"   - 描述置信度: {translation_metadata['description_translation']['confidence']:.3f}")
            print(f"   - 整体成功率: {translation_metadata['overall_quality']['translation_success_rate']:.1%}")
            print(f"   - AI翻译: {'是' if translation_metadata['overall_quality']['has_ai_translation'] else '否'}")
            
        except Exception as e:
            print(f"❌ 处理失败: {str(e)}")
        
        print("-" * 40)
    
    # 保存测试结果
    test_result_file = 'test_translation_integration_result.json'
    try:
        with open(test_result_file, 'w', encoding='utf-8') as f:
            json.dump(translated_news, f, ensure_ascii=False, indent=2)
        print(f"\n💾 测试结果已保存到: {test_result_file}")
    except Exception as e:
        print(f"❌ 保存测试结果失败: {str(e)}")
    
    # 统计翻译质量
    if translated_news:
        print(f"\n📊 翻译质量统计:")
        total_confidence = 0
        ai_translation_count = 0
        
        for news in translated_news:
            metadata = news['translation_metadata']
            total_confidence += metadata['overall_quality']['average_confidence']
            if metadata['overall_quality']['has_ai_translation']:
                ai_translation_count += 1
        
        avg_confidence = total_confidence / len(translated_news)
        ai_translation_rate = ai_translation_count / len(translated_news)
        
        print(f"   - 平均置信度: {avg_confidence:.3f}")
        print(f"   - AI翻译覆盖率: {ai_translation_rate:.1%}")
        print(f"   - 处理成功率: {len(translated_news)}/{len(test_articles)} = {len(translated_news)/len(test_articles):.1%}")
    
    print(f"\n🎉 翻译集成测试完成!")

def main():
    """主测试函数"""
    print("🔧 新闻翻译系统集成测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        test_news_translation_integration()
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()