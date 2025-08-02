#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的AI新闻更新系统 - 使用免费API
"""
import json
import os
import requests
from datetime import datetime, timezone, timedelta
import hashlib
import re

def fetch_free_news():
    """使用免费API获取新闻"""
    gnews_key = os.getenv('GNEWS_API_KEY')
    if not gnews_key:
        print("未设置GNEWS_API_KEY，使用示例数据")
        return get_example_news()
    
    url = f"https://gnews.io/api/v4/search?q=artificial intelligence OR AI OR OpenAI OR ChatGPT&lang=en&country=us&max=10&apikey={gnews_key}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append({
                    'id': hashlib.md5(article['url'].encode()).hexdigest()[:12],
                    'title': article['title'],
                    'summary': article['description'] or article['title'],
                    'source': article['source']['name'],
                    'url': article['url'],
                    'publishedAt': article['publishedAt'],
                    'image': article.get('image', '')
                })
            return articles
    except Exception as e:
        print(f"API请求失败: {e}")
        return get_example_news()

def get_example_news():
    """获取示例新闻数据"""
    return [
        {
            'id': 'example1',
            'title': 'OpenAI releases new AI model',
            'summary': 'OpenAI has announced a new AI model with improved capabilities.',
            'source': 'Tech News',
            'url': 'https://example.com/news1',
            'publishedAt': datetime.now(timezone.utc).isoformat(),
            'image': ''
        },
        {
            'id': 'example2', 
            'title': 'AI industry sees major investment',
            'summary': 'Venture capital funding for AI companies reaches new heights.',
            'source': 'Business Daily',
            'url': 'https://example.com/news2',
            'publishedAt': datetime.now(timezone.utc).isoformat(),
            'image': ''
        }
    ]

def simple_translate(text):
    """简单的英翻中映射"""
    translations = {
        'OpenAI releases new AI model': 'OpenAI发布新AI模型',
        'OpenAI has announced a new AI model with improved capabilities.': 'OpenAI宣布推出功能改进的新AI模型。',
        'AI industry sees major investment': 'AI行业迎来重大投资',
        'Venture capital funding for AI companies reaches new heights.': '风险投资对AI公司的资金投入达到新高。',
        'Tech News': '科技新闻',
        'Business Daily': '商业日报'
    }
    return translations.get(text, text)

def categorize_news(title, summary):
    """简单分类"""
    content = (title + " " + summary).lower()
    
    if any(word in content for word in ['investment', 'funding', 'raise']):
        return '投资并购', '💰'
    elif any(word in content for word in ['openai', 'google', 'microsoft']):
        return '公司动态', '🏢'
    elif any(word in content for word in ['model', 'technology', 'research']):
        return '技术突破', '🚀'
    else:
        return '热门', '🔥'

def format_time_chinese(published_at):
    """格式化时间"""
    try:
        dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = dt.astimezone(beijing_tz)
        now = datetime.now(beijing_tz)
        
        diff = now - beijing_time
        
        if diff.days > 0:
            return f"{diff.days}天前"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}小时前"
        else:
            minutes = diff.seconds // 60
            return f"{minutes}分钟前"
    except:
        return "刚刚"

def generate_news_detail_html(article):
    """生成新闻详情页"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['translated_title']} - AI科技日报</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; margin: 0; padding: 20px;
        }}
        .container {{
            max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.95);
            border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }}
        .back-link {{
            color: #667eea; text-decoration: none; font-weight: 600;
            margin-bottom: 30px; display: inline-block;
        }}
        .title {{ font-size: 1.8em; font-weight: 700; margin-bottom: 20px; }}
        .meta {{ color: #666; margin-bottom: 30px; }}
        .content {{ font-size: 1.1em; line-height: 1.8; margin-bottom: 30px; }}
        .original-link {{
            background: linear-gradient(45deg, #667eea, #764ba2); color: white;
            padding: 12px 25px; border-radius: 25px; text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">← 返回首页</a>
        <h1 class="title">{article['translated_title']}</h1>
        <div class="meta">{article['source']} • {article['time']}</div>
        <div class="content">{article['translated_summary']}</div>
        <a href="{article['url']}" target="_blank" class="original-link">查看原文 →</a>
    </div>
</body>
</html>'''

def generate_homepage_html(news_data):
    """生成首页"""
    articles = news_data['articles']
    
    news_cards = ""
    for article in articles:
        news_cards += f'''
        <div class="news-card">
            <div class="news-meta">
                <span class="source">{article['source']}</span>
                <span class="time">{article['time']}</span>
            </div>
            <h3><a href="news/{article['id']}.html">{article['translated_title']}</a></h3>
            <p>{article['translated_summary']}</p>
            <a href="news/{article['id']}.html" class="read-more">阅读全文 →</a>
        </div>'''
    
    beijing_tz = timezone(timedelta(hours=8))
    update_time = datetime.now(beijing_tz).strftime('%Y年%m月%d日 %H:%M')
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center; background: rgba(255,255,255,0.95);
            border-radius: 20px; padding: 40px; margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em; margin-bottom: 15px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .update-time {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 10px 20px; border-radius: 20px;
        }}
        .news-grid {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
        }}
        .news-card {{
            background: rgba(255,255,255,0.95); border-radius: 15px;
            padding: 25px; transition: transform 0.3s ease;
        }}
        .news-card:hover {{ transform: translateY(-5px); }}
        .news-meta {{ color: #666; margin-bottom: 15px; }}
        .source {{ background: #f0f0f0; padding: 4px 8px; border-radius: 10px; }}
        .news-card h3 {{ margin-bottom: 15px; }}
        .news-card a {{ color: #333; text-decoration: none; }}
        .news-card a:hover {{ color: #667eea; }}
        .read-more {{ color: #667eea; text-decoration: none; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p>专注人工智能前沿资讯</p>
            <div class="update-time">最后更新：{update_time}</div>
        </div>
        <div class="news-grid">{news_cards}</div>
    </div>
</body>
</html>'''

def main():
    """主函数"""
    print("开始更新新闻...")
    
    # 获取新闻
    articles = fetch_free_news()
    print(f"获取到 {len(articles)} 条新闻")
    
    # 处理新闻
    processed_articles = []
    for article in articles:
        category, category_icon = categorize_news(article['title'], article['summary'])
        time_chinese = format_time_chinese(article['publishedAt'])
        
        processed_article = {
            **article,
            'translated_title': simple_translate(article['title']),
            'translated_summary': simple_translate(article['summary']),
            'category': category,
            'category_icon': category_icon,
            'time': time_chinese
        }
        processed_articles.append(processed_article)
    
    # 保存数据
    news_data = {
        'last_updated': datetime.now().isoformat(),
        'total_count': len(processed_articles),
        'articles': processed_articles
    }
    
    os.makedirs('docs', exist_ok=True)
    os.makedirs('docs/news', exist_ok=True)
    
    with open('docs/news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    # 生成页面
    homepage_html = generate_homepage_html(news_data)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(homepage_html)
    
    for article in processed_articles:
        detail_html = generate_news_detail_html(article)
        with open(f'docs/news/{article["id"]}.html', 'w', encoding='utf-8') as f:
            f.write(detail_html)
    
    print(f"✅ 更新完成! 生成了 {len(processed_articles)} 条新闻")

if __name__ == "__main__":
    main()