#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新闻增强功能 - 新鲜度管理和AI点评
"""

from localization.news_freshness_manager import NewsFreshnessManager
from localization.ai_commentary import AICommentary
from datetime import datetime, timedelta

def test_news_freshness_manager():
    """测试新闻新鲜度管理器"""
    print("🧪 测试新闻新鲜度管理器")
    print("=" * 50)
    
    manager = NewsFreshnessManager()
    
    # 创建测试新闻数据
    test_news = [
        {
            'title': 'OpenAI发布最新AI模型',
            'description': 'OpenAI公司今日发布了最新的人工智能模型...',
            'category': 'AI科技',
            'publishedAt': (datetime.now() - timedelta(hours=2)).isoformat() + 'Z',
            'source': {'name': 'TechCrunch'},
            'ai_translation': {
                'translation_confidence': {'title': 0.95, 'description': 0.90}
            }
        },
        {
            'title': '新游戏发布引发热议',
            'description': '最新发布的游戏获得了玩家的广泛关注...',
            'category': '游戏资讯',
            'publishedAt': (datetime.now() - timedelta(hours=6)).isoformat() + 'Z',
            'source': {'name': 'GameSpot'}
        },
        {
            'title': '股市今日大涨',
            'description': '受利好消息影响，股市今日出现大幅上涨...',
            'category': '经济新闻',
            'publishedAt': (datetime.now() - timedelta(days=1)).isoformat() + 'Z',
            'source': {'name': 'Reuters'}
        }
    ]
    
    # 测试1: 过滤新鲜新闻
    print("📋 测试1: 过滤新鲜新闻（24小时内）")
    fresh_news = manager.filter_fresh_news(test_news, 24)
    print(f"   原始新闻数: {len(test_news)}")
    print(f"   新鲜新闻数: {len(fresh_news)}")
    
    for news in fresh_news:
        if 'time_info' in news:
            print(f"   - {news['title']}: {news['time_info']['relative']}")
    
    print("   ✅ 新鲜新闻过滤测试通过")
    
    # 测试2: 按新鲜度排序
    print("\n📋 测试2: 按新鲜度排序")
    sorted_news = manager.sort_by_freshness(test_news.copy())
    
    for i, news in enumerate(sorted_news, 1):
        score = news.get('freshness_score', 0)
        print(f"   {i}. {news['title']} (评分: {score:.3f})")
    
    print("   ✅ 新鲜度排序测试通过")
    
    # 测试3: 按新鲜度分类
    print("\n📋 测试3: 按新鲜度分类")
    categorized = manager.categorize_by_freshness(test_news)
    
    for category, news_list in categorized.items():
        if news_list:
            print(f"   {category}: {len(news_list)} 条新闻")
    
    print("   ✅ 新鲜度分类测试通过")
    
    # 测试4: 获取新鲜度摘要
    print("\n📋 测试4: 获取新鲜度摘要")
    summary = manager.get_freshness_summary(test_news)
    
    print(f"   总新闻数: {summary['total_count']}")
    print(f"   新鲜新闻数: {summary['fresh_count']}")
    print(f"   新鲜度百分比: {summary['fresh_percentage']:.1f}%")
    print(f"   平均年龄: {summary['average_age_hours']:.1f} 小时")
    
    print("   ✅ 新鲜度摘要测试通过")
    
    # 测试5: 更新状态
    print("\n📋 测试5: 更新状态")
    status = manager.get_update_status()
    print(f"   {status['update_text']}")
    print(f"   时区: {status['timezone_name']}")
    print("   ✅ 更新状态测试通过")
    
    return True

def test_ai_commentary():
    """测试AI点评功能"""
    print("\n🧪 测试AI点评功能")
    print("=" * 50)
    
    commentary = AICommentary()
    
    # 测试新闻
    test_title = "OpenAI发布GPT-5模型，性能大幅提升"
    test_content = "OpenAI公司今日正式发布了最新的GPT-5人工智能模型，该模型在多项基准测试中表现出色，相比前代产品性能提升显著。新模型在自然语言理解、代码生成和创意写作等方面都有重大突破。"
    
    print("📋 测试1: 生成单条新闻点评")
    print(f"   新闻标题: {test_title}")
    
    # 生成点评
    result = commentary.generate_commentary(test_title, test_content)
    
    if result['success']:
        print("   ✅ AI点评生成成功")
        print(f"   📝 点评内容: {result['commentary']}")
        print(f"   📊 字数: {result['word_count']}")
        print(f"   🤖 模型: {result['model']}")
        print(f"   ⏰ 时间: {result['timestamp']}")
    else:
        print("   ⚠️ AI点评生成失败，使用备用方案")
        fallback = commentary.generate_fallback_commentary(test_title, "AI科技")
        print(f"   📝 备用点评: {fallback}")
    
    # 测试2: 批量生成点评
    print("\n📋 测试2: 批量生成点评")
    test_news_batch = [
        {
            'title': 'Meta发布新VR设备',
            'content': 'Meta公司发布了最新的VR头显设备，采用了更先进的显示技术...',
            'category': 'AI科技'
        },
        {
            'title': '比特币价格突破新高',
            'content': '加密货币市场今日表现强劲，比特币价格创下历史新高...',
            'category': '经济新闻'
        }
    ]
    
    batch_result = commentary.batch_generate_commentary(test_news_batch)
    
    print(f"   总数: {batch_result['total_count']}")
    print(f"   成功: {batch_result['success_count']}")
    print(f"   失败: {batch_result['error_count']}")
    
    for item in batch_result['commentaries']:
        print(f"   - {item['title']}: {'成功' if item['success'] else '使用备用'}")
    
    print("   ✅ 批量点评测试通过")
    
    return True

def main():
    """主测试流程"""
    print("🚀 测试新闻增强功能")
    print("=" * 60)
    
    # 测试新鲜度管理
    freshness_ok = test_news_freshness_manager()
    
    # 测试AI点评
    commentary_ok = test_ai_commentary()
    
    # 总结
    print(f"\n📊 测试结果总结:")
    print("=" * 60)
    print(f"✅ 新鲜度管理: {'通过' if freshness_ok else '失败'}")
    print(f"✅ AI点评功能: {'通过' if commentary_ok else '失败'}")
    
    if freshness_ok and commentary_ok:
        print("\n🎉 所有测试通过！新闻增强功能准备就绪")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能")

if __name__ == "__main__":
    main()