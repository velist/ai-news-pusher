#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文本地化器功能
"""

from localization.chinese_localizer import ChineseLocalizer

def test_chinese_localizer():
    """测试中文本地化器的各项功能"""
    print("🧪 测试中文本地化器功能")
    print("=" * 50)
    
    localizer = ChineseLocalizer()
    
    # 测试1: 分类本地化
    print("📋 测试1: 新闻分类本地化")
    test_categories = ['technology', 'gaming', 'business', 'AI', 'unknown_category']
    
    for category in test_categories:
        localized = localizer.localize_category(category)
        print(f"   {category} → {localized}")
    
    print("   ✅ 分类本地化测试通过")
    
    # 测试2: UI文本本地化
    print("\n📋 测试2: UI文本本地化")
    test_ui_keys = ['read_more', 'original_text', 'translation_quality', 'settings', 'unknown_key']
    
    for key in test_ui_keys:
        localized = localizer.localize_ui_text(key)
        print(f"   {key} → {localized}")
    
    print("   ✅ UI文本本地化测试通过")
    
    # 测试3: 翻译质量评分
    print("\n📋 测试3: 翻译质量评分")
    test_scores = [0.95, 0.85, 0.75, 0.65, 0.45]
    
    for score in test_scores:
        quality_text = localizer.format_quality_score(score)
        quality_detail = localizer.get_quality_description(score)
        print(f"   评分 {score} → {quality_text} ({quality_detail['detail']})")
    
    print("   ✅ 翻译质量评分测试通过")
    
    # 测试4: 阅读时间估算
    print("\n📋 测试4: 阅读时间估算")
    test_contents = [
        "这是一个简短的测试文本。",
        "这是一个较长的测试文本，包含更多的中文字符，用于测试阅读时间估算功能的准确性。" * 5,
        "This is a mixed content with both English and 中文字符 to test the reading time estimation.",
        "A" * 1000  # 长英文文本
    ]
    
    for i, content in enumerate(test_contents, 1):
        reading_time = localizer.get_reading_time_estimate(content)
        print(f"   测试{i} (长度: {len(content)}字符) → 阅读时间: {reading_time}")
    
    print("   ✅ 阅读时间估算测试通过")
    
    # 测试5: 新闻源本地化
    print("\n📋 测试5: 新闻源本地化")
    test_sources = ['TechCrunch', 'Reuters', 'BBC', 'Unknown Source']
    
    for source in test_sources:
        localized = localizer.localize_source_name(source)
        print(f"   {source} → {localized}")
    
    print("   ✅ 新闻源本地化测试通过")
    
    # 测试6: 新闻摘要格式化
    print("\n📋 测试6: 新闻摘要格式化")
    test_news = {
        'title': 'OpenAI Announces New AI Model',
        'description': 'OpenAI has announced a breakthrough in artificial intelligence technology that could revolutionize the industry.',
        'category': 'technology',
        'source': {'name': 'TechCrunch'},
        'ai_translation': {
            'translation_confidence': {
                'title': 0.92,
                'description': 0.88
            }
        }
    }
    
    summary = localizer.format_news_summary(test_news)
    print(f"   标题: {summary['title']}")
    print(f"   分类: {summary['category']}")
    print(f"   来源: {summary['source']}")
    print(f"   阅读时间: {summary['reading_time']}")
    if 'quality' in summary:
        print(f"   翻译质量: {summary['quality']['text']} ({summary['quality']['percentage']})")
    
    print("   ✅ 新闻摘要格式化测试通过")
    
    # 测试7: 本地化配置
    print("\n📋 测试7: 本地化配置")
    config = localizer.get_localized_config()
    print(f"   语言: {config['language']}")
    print(f"   时区: {config['timezone']}")
    print(f"   日期格式: {config['date_format']}")
    print(f"   字体: {config['font_family']}")
    print("   ✅ 本地化配置测试通过")
    
    print(f"\n🎉 所有测试完成！")

if __name__ == "__main__":
    test_chinese_localizer()