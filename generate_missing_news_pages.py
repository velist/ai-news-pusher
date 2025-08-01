#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成缺失的新闻详情页面
"""

import json
import os
from datetime import datetime, timezone, timedelta

# 读取新闻数据
with open('docs/enhanced_news_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data['articles']

def generate_news_detail_page(article):
    """生成新闻详情页面"""
    
    # 使用翻译后的标题和摘要（如果有的话）
    display_title = article.get('translated_title', article['title'])
    display_summary = article.get('translated_summary', article['summary'])
    ai_commentary = article.get('ai_commentary', '')
    extended_content = article.get('extended_content', '')
    
    # 获取北京时间
    beijing_tz = timezone(timedelta(hours=8))
    beijing_time = datetime.now(beijing_tz)
    formatted_time = beijing_time.strftime("%Y年%m月%d日 %H:%M")
    
    # 处理图片标签
    image_tag = ""
    if article.get('image'):
        image_tag = f'<img src="{article["image"]}" alt="{display_title}" class="article-image" onerror="this.style.display=\'none\'">'
    
    # 处理扩展内容
    content_section = ""
    if extended_content:
        content_section = f'<div class="article-content">{extended_content}</div>'
    
    # 处理AI点评
    commentary_section = ""
    if ai_commentary:
        commentary_section = f'<div class="ai-commentary"><h3>🤖 AI专家点评</h3><p>{ai_commentary}</p></div>'
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} - AI科技日报</title>
    <meta name="description" content="{display_summary[:150]}...">
    <meta name="keywords" content="AI新闻,人工智能,{article['category']},{article['source']}">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "SimSun", sans-serif;
            line-height: 1.8; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; 
            color: #333;
            padding: 20px 0;
        }}
        
        .container {{ 
            max-width: 900px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.95); 
            border-radius: 24px; 
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); 
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .back-link {{ 
            color: #667eea; 
            text-decoration: none; 
            font-weight: 600; 
            margin-bottom: 30px; 
            display: inline-block;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{ 
            color: #764ba2; 
            transform: translateX(-5px);
        }}
        
        .article-header {{ 
            border-bottom: 3px solid #667eea; 
            padding-bottom: 25px; 
            margin-bottom: 30px; 
        }}
        
        .article-title {{ 
            font-size: 2.2em; 
            font-weight: 800; 
            margin-bottom: 20px; 
            line-height: 1.3;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .article-meta {{ 
            display: flex; 
            flex-wrap: wrap; 
            gap: 15px; 
            align-items: center; 
            font-size: 0.95em; 
            color: #666;
        }}
        
        .meta-item {{ 
            background: rgba(102, 126, 234, 0.1); 
            color: #667eea; 
            padding: 8px 16px; 
            border-radius: 20px; 
            font-weight: 600;
        }}
        
        .category-badge {{ 
            background: rgba(118, 75, 162, 0.1);
            color: #764ba2;
        }}
        
        .article-image {{ 
            width: 100%; 
            max-height: 400px; 
            object-fit: cover; 
            border-radius: 16px; 
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .article-summary {{ 
            font-size: 1.2em; 
            line-height: 1.7; 
            color: #444; 
            background: rgba(102, 126, 234, 0.05); 
            padding: 25px; 
            border-radius: 16px; 
            margin: 30px 0;
            border-left: 4px solid #667eea;
        }}
        
        .article-content {{ 
            font-size: 1.1em; 
            line-height: 1.8; 
            color: #555;
            margin: 30px 0;
        }}
        
        .ai-commentary {{ 
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
            padding: 30px; 
            border-radius: 20px; 
            margin: 40px 0;
            border: 2px solid rgba(102, 126, 234, 0.2);
        }}
        
        .ai-commentary h3 {{ 
            color: #667eea; 
            font-size: 1.3em; 
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .original-link {{ 
            display: inline-block; 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 15px 30px; 
            border-radius: 30px; 
            text-decoration: none; 
            font-weight: 600; 
            margin: 30px 0;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .original-link:hover {{ 
            transform: translateY(-2px); 
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.4);
        }}
        
        .footer {{ 
            text-align: center; 
            margin-top: 50px; 
            padding-top: 30px; 
            border-top: 2px solid rgba(102, 126, 234, 0.1); 
            color: #888;
        }}
        
        /* 移动端优化 */
        @media (max-width: 768px) {{
            .container {{ padding: 25px; }}
            .article-title {{ font-size: 1.8em; }}
            .article-meta {{ flex-direction: column; align-items: flex-start; }}
            .article-summary {{ padding: 20px; }}
            .ai-commentary {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-link">← 返回首页</a>
        
        <div class="article-header">
            <h1 class="article-title">{display_title}</h1>
            <div class="article-meta">
                <span class="meta-item">{article['source']}</span>
                <span class="meta-item">{article['time']}</span>
                <span class="meta-item category-badge">{article['category_icon']} {article['category']}</span>
            </div>
        </div>
        
        {image_tag}
        
        <div class="article-summary">
            {display_summary}
        </div>
        
        {content_section}
        
        {commentary_section}
        
        <a href="{article['url']}" target="_blank" class="original-link">
            查看原文 →
        </a>
        
        <div class="footer">
            <p>🤖 AI科技日报 - 专注人工智能前沿资讯</p>
            <p>最后更新：{formatted_time}</p>
        </div>
    </div>
</body>
</html>'''
    
    return html_content

# 确保news目录存在
os.makedirs('docs/news', exist_ok=True)

# 生成所有新闻详情页
generated_count = 0
for article in articles:
    file_path = f"docs/news/{article['id']}.html"
    html_content = generate_news_detail_page(article)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    generated_count += 1

print(f"✅ 成功生成 {generated_count} 个新闻详情页面")
print("📁 文件保存在 docs/news/ 目录下")
print("🌐 新闻详情页面已可正常访问")