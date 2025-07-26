#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的HTML重新生成脚本
"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def regenerate_html():
    """使用enhanced_news_data.json重新生成HTML页面"""
    try:
        # 读取enhanced_news_data.json
        with open('docs/enhanced_news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f"📖 读取到 {len(articles)} 条新闻数据")
        
        # 生成HTML内容
        html_content = generate_html_template(articles)
        
        # 写入index.html
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ HTML页面重新生成完成！")
        return True
        
    except Exception as e:
        print(f"❌ 生成HTML失败: {e}")
        return False

def generate_html_template(articles):
    """生成HTML模板"""
    today = datetime.now()
    
    # 按重要性排序
    sorted_articles = sorted(articles, key=lambda x: x.get('importance', 1), reverse=True)
    
    # 生成新闻项HTML
    news_items_html = ""
    for article in sorted_articles[:20]:  # 只显示前20条
        # 获取翻译后的标题和描述
        title = article.get('title', '无标题')
        description = article.get('description', '无描述')
        
        # 如果有AI翻译，优先使用翻译内容
        ai_translation = article.get('ai_translation', {})
        if ai_translation.get('translated_title'):
            title = ai_translation['translated_title']
        if ai_translation.get('translated_description'):
            description = ai_translation['translated_description']
        
        # 获取分类信息
        category = article.get('category', {}).get('name', '未分类')
        category_icon = article.get('category', {}).get('icon', '📰')
        
        # 获取发布时间
        published_at = article.get('publishedAt', '')
        if published_at:
            try:
                pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                time_str = pub_time.strftime('%m-%d %H:%M')
            except:
                time_str = '未知时间'
        else:
            time_str = '未知时间'
        
        # 获取重要性星级
        importance = article.get('importance', 1)
        stars = '★' * min(importance, 5)
        
        news_items_html += f"""
            <div class="news-item">
                <div class="news-title">{title}</div>
                <div class="news-meta">
                    <span class="importance-stars">{stars}</span>
                    <span class="category">{category_icon} {category}</span>
                    <span class="time">🕒 {time_str}</span>
                </div>
                <div class="news-description">{description}</div>
            </div>
        """
    
    # 完整HTML模板
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 中文AI资讯门户</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .news-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .news-item {{
            border-bottom: 1px solid #eee;
            padding: 20px 0;
            transition: all 0.3s ease;
        }}
        
        .news-item:hover {{
            background: rgba(102, 126, 234, 0.05);
            border-radius: 10px;
            padding: 20px 15px;
        }}
        
        .news-item:last-child {{
            border-bottom: none;
        }}
        
        .news-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
            line-height: 1.4;
        }}
        
        .news-meta {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .importance-stars {{
            color: #f39c12;
            font-weight: bold;
        }}
        
        .category {{
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }}
        
        .time {{
            color: #7f8c8d;
        }}
        
        .news-description {{
            color: #555;
            line-height: 1.6;
            font-size: 0.95em;
        }}
        
        .update-time {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .news-container {{
                padding: 20px;
            }}
            
            .news-meta {{
                flex-wrap: wrap;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p>中文AI资讯门户 · 每日更新</p>
        </div>
        
        <div class="news-container">
            {news_items_html}
            
            <div class="update-time">
                📅 最后更新: {today.strftime('%Y年%m月%d日 %H:%M')}
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_template

if __name__ == '__main__':
    regenerate_html()