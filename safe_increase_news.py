#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的新闻数量增加脚本 - 保持中文显示
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import hashlib
import time

def load_env_file():
    """加载环境变量"""
    env_path = '.env'
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            return True
        except Exception as e:
            print(f"环境变量加载失败: {e}")
            return False
    return False

def get_more_gnews():
    """从GNews获取更多新闻"""
    load_env_file()
    gnews_key = os.environ.get('GNEWS_API_KEY')
    
    if not gnews_key:
        print("❌ 缺少GNews API密钥")
        return []
    
    all_articles = []
    queries = [
        "AI OR artificial intelligence",
        "OpenAI OR ChatGPT OR GPT", 
        "Google AI OR Gemini",
        "machine learning OR deep learning",
        "AI startup OR AI funding",
        "AI research OR AI breakthrough"
    ]
    
    print("📡 从GNews获取更多新闻...")
    
    for i, query in enumerate(queries):
        try:
            print(f"  查询 {i+1}: {query}")
            url = f"https://gnews.io/api/v4/search?q={urllib.parse.quote(query)}&lang=en&max=8&apikey={gnews_key}"
            
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if 'articles' in data:
                for article in data['articles']:
                    all_articles.append({
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', '未知来源'),
                        'publishedAt': article.get('publishedAt', ''),
                        'image': article.get('image', ''),
                        'api_source': 'gnews'
                    })
            
            time.sleep(2)  # 避免API限制
        except Exception as e:
            print(f"    错误: {e}")
    
    # 去重
    seen_titles = set()
    unique_articles = []
    
    for article in all_articles:
        if article['title'] and article['summary']:
            title_hash = hashlib.md5(article['title'].encode()).hexdigest()[:12]
            if title_hash not in seen_titles:
                seen_titles.add(title_hash)
                article['id'] = title_hash
                unique_articles.append(article)
    
    print(f"✅ 获取到 {len(unique_articles)} 条新闻")
    return unique_articles

def update_news_data():
    """更新新闻数据"""
    # 获取新新闻
    new_articles = get_more_gnews()
    
    # 读取现有数据
    try:
        with open('docs/enhanced_news_data.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        existing_articles = existing_data.get('articles', [])
    except:
        existing_articles = []
    
    # 合并数据
    all_articles = new_articles + existing_articles
    
    # 去重
    seen_ids = set()
    final_articles = []
    
    for article in all_articles:
        article_id = article.get('id')
        if article_id and article_id not in seen_ids:
            seen_ids.add(article_id)
            final_articles.append(article)
    
    # 限制到50条
    final_articles = final_articles[:50]
    
    print(f"🎉 最终数据: {len(final_articles)} 条新闻")
    
    # 保存数据
    updated_data = {
        'last_updated': datetime.now().isoformat(),
        'total_count': len(final_articles),
        'categories': list(set(article.get('category', '热门') for article in final_articles)),
        'articles': final_articles
    }
    
    with open('docs/enhanced_news_data.json', 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    
    print("✅ 新闻数据已更新")
    return final_articles

if __name__ == "__main__":
    print("🚀 安全增加新闻数量...")
    articles = update_news_data()