#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复新闻数据时间字段
"""

import json
from datetime import datetime, timezone, timedelta

def format_beijing_time(iso_time_str):
    """将ISO时间字符串转换为北京时间并格式化显示"""
    try:
        if not iso_time_str:
            return "未知时间"
            
        if iso_time_str.endswith('Z'):
            dt = datetime.fromisoformat(iso_time_str[:-1] + '+00:00')
        else:
            dt = datetime.fromisoformat(iso_time_str)
        
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = dt.astimezone(beijing_tz)
        now_beijing = datetime.now(beijing_tz)
        time_diff = now_beijing - beijing_time
        
        if time_diff.days > 0:
            return f"{time_diff.days}天前"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"{hours}小时前"
        elif time_diff.seconds > 60:
            minutes = time_diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
    except:
        return "未知时间"

def categorize_article(title, summary):
    """智能分类文章"""
    title_lower = title.lower()
    summary_lower = summary.lower()
    combined = (title_lower + " " + summary_lower)
    
    # 模型相关关键词
    model_keywords = [
        'gpt', 'chatgpt', 'gemini', 'claude', 'llama', 'qwen', 'baichuan', 'chatglm',
        'model', 'llm', 'large language model', 'ai model', 'neural network',
        'transformer', 'bert', 'dall-e', 'midjourney', 'stable diffusion'
    ]
    
    if any(word in combined for word in model_keywords):
        return '模型', '🤖'
    elif any(word in combined for word in ['funding', 'investment', 'raise', 'billion', 'million', 'valuation']):
        return '投资并购', '💰'
    elif any(word in combined for word in ['openai', 'google', 'microsoft', 'apple', 'meta', 'amazon', 'nvidia']):
        return '公司动态', '🏢'
    elif any(word in combined for word in ['breakthrough', 'research', 'algorithm', 'technology', 'innovation']):
        return '技术突破', '🚀'
    elif any(word in combined for word in ['regulation', 'policy', 'government', 'law', 'compliance']):
        return '政策监管', '⚖️'
    elif any(word in combined for word in ['application', 'healthcare', 'finance', 'education', 'automotive']):
        return '行业应用', '🎯'
    
    return '热门', '🔥'

# 读取并处理数据
with open('docs/enhanced_news_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data['articles']

# 为每篇文章添加缺失的字段
for article in articles:
    if 'time' not in article:
        article['time'] = format_beijing_time(article.get('publishedAt', ''))
    
    if 'category' not in article or 'category_icon' not in article:
        category, category_icon = categorize_article(article.get('title', ''), article.get('summary', ''))
        article['category'] = category
        article['category_icon'] = category_icon

# 保存更新后的数据
data['articles'] = articles
with open('docs/enhanced_news_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ 已修复 {len(articles)} 条新闻的字段")
print("📊 分类统计:")

category_count = {}
for article in articles:
    cat = article.get('category', '未分类')
    category_count[cat] = category_count.get(cat, 0) + 1

for cat, count in category_count.items():
    print(f"  {cat}: {count} 条")