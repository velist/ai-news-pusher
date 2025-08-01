#!/usr/bin/env python3
"""
简单更新首页新闻数量和显示
"""

import json
import re
from pathlib import Path

def update_homepage():
    """更新首页显示50条新闻"""
    
    # 读取新闻数据
    data_file = Path('docs/enhanced_news_data.json')
    if not data_file.exists():
        print("❌ 新闻数据文件不存在")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    articles = news_data.get('articles', [])
    total_count = len(articles)
    
    print(f"📰 找到 {total_count} 条新闻")
    
    # 统计分类
    categories = {}
    for article in articles:
        category = article.get('category', '热门')
        categories[category] = categories.get(category, 0) + 1
    
    print(f"📊 分类统计: {categories}")
    
    # 读取首页文件
    index_file = Path('docs/index.html')
    if not index_file.exists():
        print("❌ 首页文件不存在")
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新Tab数量显示
    content = re.sub(
        r'📰 全部 \(\d+\)',
        f'📰 全部 ({total_count})',
        content
    )
    
    # 更新各分类数量
    for category, count in categories.items():
        icon_map = {
            '模型': '🤖',
            '技术突破': '🚀', 
            '热门': '🔥',
            '公司动态': '🏢',
            '投资并购': '💰'
        }
        icon = icon_map.get(category, '📰')
        
        pattern = rf'{re.escape(icon)} {re.escape(category)} \(\d+\)'
        replacement = f'{icon} {category} ({count})'
        content = re.sub(pattern, replacement, content)
    
    # 更新total_count
    content = re.sub(
        r'"total_count": \d+',
        f'"total_count": {total_count}',
        content
    )
    
    # 保存更新后的首页
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 首页已更新，显示 {total_count} 条新闻")
    print(f"📊 分类分布: {categories}")

if __name__ == "__main__":
    update_homepage()