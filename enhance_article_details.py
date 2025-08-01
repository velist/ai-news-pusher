#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详情页内容增强脚本 - 添加关键新闻信息
"""

import os
import json
from datetime import datetime, timezone, timedelta

def format_full_beijing_time(iso_time_str):
    """格式化完整的北京时间用于详情页"""
    try:
        if iso_time_str.endswith('Z'):
            dt = datetime.fromisoformat(iso_time_str[:-1] + '+00:00')
        else:
            dt = datetime.fromisoformat(iso_time_str)
        
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = dt.astimezone(beijing_tz)
        
        return beijing_time.strftime("%Y年%m月%d日 %H:%M (北京时间)")
    except:
        return "未知时间"

def generate_enhanced_article_page(article):
    """生成增强版文章详情页HTML"""
    display_title = article.get('translated_title', article['title'])
    display_summary = article.get('translated_summary', article['summary'])
    
    # 完整时间显示
    full_time_display = format_full_beijing_time(article['publishedAt'])
    
    # 提取关键信息
    key_info = []
    
    # 分析标题和摘要中的关键信息
    content = article['title'] + " " + article['summary']
    
    # 提取数字信息（金额、用户数等）
    import re
    numbers = re.findall(r'\$?[\d,]+\.?\d*\s*(?:billion|million|thousand|B|M|K|万|亿|千万)', content.lower())
    if numbers:
        key_info.append(f"💰 关键数据: {', '.join(numbers)}")
    
    # 提取公司信息
    companies = []
    company_keywords = ['OpenAI', 'Google', 'Microsoft', 'Apple', 'Meta', 'Amazon', 'NVIDIA', 'Anthropic', 
                       'Tesla', 'Baidu', 'Alibaba', 'Tencent', '百度', '阿里巴巴', '腾讯']
    for company in company_keywords:
        if company.lower() in content.lower():
            companies.append(company)
    
    if companies:
        key_info.append(f"🏢 涉及公司: {', '.join(set(companies))}")
    
    # 提取产品/模型信息
    products = []
    product_keywords = ['ChatGPT', 'GPT-4', 'GPT-5', 'Gemini', 'Claude', 'LLaMA', 'DALL-E', 'Midjourney']
    for product in product_keywords:
        if product.lower() in content.lower():
            products.append(product)
    
    if products:
        key_info.append(f"🤖 相关产品: {', '.join(set(products))}")
    
    # 构建关键信息HTML
    key_info_html = ""
    if key_info:
        key_info_items = "\n".join([f"<li>{info}</li>" for info in key_info])
        key_info_html = f"""
        <div class="key-info-section">
            <h3>🔍 关键信息</h3>
            <ul class="key-info-list">
                {key_info_items}
            </ul>
        </div>
        """
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} - AI科技日报</title>
    <meta name="description" content="{display_summary[:150]}...">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "SimSun", sans-serif;
            line-height: 1.8; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; margin: 0; padding: 20px; color: #333;
        }}
        
        .article-container {{
            max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.95);
            border-radius: 24px; padding: 50px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .back-link {{
            display: inline-block; color: #667eea; text-decoration: none; 
            font-weight: 600; margin-bottom: 30px; font-size: 1.1em;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{ color: #764ba2; transform: translateX(-5px); }}
        
        .article-header {{
            border-bottom: 3px solid rgba(102, 126, 234, 0.1); 
            padding-bottom: 30px; margin-bottom: 40px;
        }}
        
        .article-category {{
            display: inline-block; background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 10px 20px; border-radius: 20px; 
            font-weight: 600; margin-bottom: 20px; font-size: 1em;
        }}
        
        .article-title {{
            font-size: 2.5em; font-weight: 800; line-height: 1.2; 
            margin-bottom: 20px; color: #333;
        }}
        
        .article-meta {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; background: rgba(102, 126, 234, 0.05); 
            padding: 20px; border-radius: 15px; margin-bottom: 30px;
        }}
        
        .meta-item {{
            display: flex; flex-direction: column; gap: 5px;
        }}
        
        .meta-label {{
            font-size: 0.9em; color: #666; font-weight: 600;
        }}
        
        .meta-value {{
            font-size: 1em; color: #333; font-weight: 500;
        }}
        
        .article-source {{
            background: rgba(102, 126, 234, 0.1); color: #667eea; 
            padding: 8px 16px; border-radius: 20px; font-weight: 600;
            display: inline-block; width: fit-content;
        }}
        
        .article-content {{
            font-size: 1.2em; line-height: 1.8; margin-bottom: 40px;
        }}
        
        .content-section {{
            margin-bottom: 30px;
        }}
        
        .content-section h3 {{
            color: #667eea; font-size: 1.4em; margin-bottom: 15px;
            font-weight: 700; border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        
        .key-info-section {{
            background: rgba(102, 126, 234, 0.08);
            padding: 25px; border-radius: 15px; margin-bottom: 30px;
            border-left: 4px solid #667eea;
        }}
        
        .key-info-list {{
            list-style: none; padding: 0; margin: 15px 0 0 0;
        }}
        
        .key-info-list li {{
            padding: 8px 0; border-bottom: 1px solid rgba(102, 126, 234, 0.1);
            font-size: 1.1em; color: #555;
        }}
        
        .key-info-list li:last-child {{
            border-bottom: none;
        }}
        
        .extended-content {{
            background: rgba(118, 75, 162, 0.05);
            padding: 25px; border-radius: 15px; margin-bottom: 30px;
            border-left: 4px solid #764ba2;
        }}
        
        .ai-commentary {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-left: 5px solid #667eea; padding: 30px; border-radius: 15px;
            margin-bottom: 30px;
        }}
        
        .ai-commentary h4 {{
            color: #667eea; font-size: 1.3em; margin-bottom: 15px; 
            font-weight: 700; display: flex; align-items: center; gap: 10px;
        }}
        
        .ai-commentary-content {{
            font-size: 1.1em; line-height: 1.7; color: #555;
        }}
        
        .article-actions {{
            text-align: center; padding-top: 30px; 
            border-top: 2px solid rgba(102, 126, 234, 0.1);
            display: flex; gap: 20px; justify-content: center;
            flex-wrap: wrap;
        }}
        
        .original-link {{
            display: inline-block; background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 15px 30px; border-radius: 25px; 
            text-decoration: none; font-weight: 600; font-size: 1.1em;
            transition: all 0.3s ease; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .original-link:hover {{
            transform: translateY(-3px); box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
        }}
        
        .share-btn {{
            background: rgba(102, 126, 234, 0.1); color: #667eea;
            padding: 15px 30px; border-radius: 25px; text-decoration: none;
            font-weight: 600; font-size: 1.1em; transition: all 0.3s ease;
            border: 2px solid #667eea;
        }}
        
        .share-btn:hover {{
            background: #667eea; color: white;
            transform: translateY(-3px);
        }}
        
        @media (max-width: 768px) {{
            .article-container {{ padding: 30px 25px; }}
            .article-title {{ font-size: 2em; }}
            .article-meta {{ grid-template-columns: 1fr; }}
            .article-actions {{ flex-direction: column; align-items: center; }}
        }}
    </style>
</head>
<body>
    <div class="article-container">
        <a href="../index.html" class="back-link">← 返回首页</a>
        
        <div class="article-header">
            <div class="article-category">{article['category_icon']} {article['category']}</div>
            <h1 class="article-title">{display_title}</h1>
            
            <div class="article-meta">
                <div class="meta-item">
                    <div class="meta-label">📰 新闻来源</div>
                    <div class="meta-value article-source">{article['source']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">⏰ 发布时间</div>
                    <div class="meta-value">{full_time_display}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">🏷️ 新闻分类</div>
                    <div class="meta-value">{article['category_icon']} {article['category']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">🌐 原文语言</div>
                    <div class="meta-value">English (已翻译)</div>
                </div>
            </div>
        </div>
        
        <div class="article-content">
            <div class="content-section">
                <h3>📋 新闻摘要</h3>
                <p>{display_summary}</p>
            </div>
            
            {key_info_html}
        </div>
        
        {('<div class="ai-commentary"><h4>🤖 AI专家点评</h4><div class="ai-commentary-content">' +
        article.get('ai_commentary', '暂无AI点评') + '</div></div>') if article.get('ai_commentary') else ''}
        
        <div class="article-actions">
            <a href="{article['url']}" target="_blank" class="original-link">查看英文原文 →</a>
            <a href="#" onclick="navigator.share ? navigator.share({{title: '{display_title}', url: window.location.href}}) : alert('分享功能需要在移动设备上使用')" class="share-btn">📱 分享新闻</a>
        </div>
    </div>
</body>
</html>'''

    return html

# 读取现有数据
with open('docs/enhanced_news_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data['articles']

print("🔄 正在增强详情页内容...")

# 为每篇文章生成增强的详情页
for i, article in enumerate(articles):
    print(f"📄 处理文章 {i+1}/{len(articles)}: {article['title'][:50]}...")
    
    enhanced_html = generate_enhanced_article_page(article)
    
    # 确保news目录存在
    os.makedirs('docs/news', exist_ok=True)
    
    # 保存增强的详情页
    with open(f"docs/news/{article['id']}.html", 'w', encoding='utf-8') as f:
        f.write(enhanced_html)

print("✅ 详情页内容增强完成！")
print("📋 增强内容包括:")
print("  - 🔍 关键信息提取（金额、公司、产品）")
print("  - 📊 完整的新闻元数据")
print("  - 🌐 原文语言标识")
print("  - 📱 移动端分享功能")
print("  - 🎨 更丰富的视觉设计")
print(f"📂 处理了 {len(articles)} 个详情页面")