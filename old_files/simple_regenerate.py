#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用现有JSON数据重新生成HTML页面
"""

import json
import os
from datetime import datetime

def generate_html_from_json():
    """直接使用现有JSON数据生成HTML"""
    try:
        with open('docs/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print("📖 读取现有新闻数据...")
    except FileNotFoundError:
        print("❌ 未找到现有新闻数据文件")
        return False

    # 生成首页HTML
    index_html = generate_index_html(articles)
    
    # 确保目录存在
    os.makedirs('docs', exist_ok=True)
    os.makedirs('docs/news', exist_ok=True)
    
    # 写入首页
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # 生成详情页
    for article in articles:
        detail_html = generate_detail_html(article, articles)
        with open(f'docs/news/{article["id"]}.html', 'w', encoding='utf-8') as f:
            f.write(detail_html)
    
    print("✅ 使用现有数据重新生成完成:")
    print("   📄 首页: docs/index.html")
    print(f"   📰 详情页: docs/news/ ({len(articles)} 篇)")
    return True

def generate_index_html(articles):
    """生成首页HTML"""
    # 获取所有分类
    categories = {}
    for article in articles:
        cat = article['category']
        cat_name = cat['name']
        if cat_name not in categories:
            categories[cat_name] = {
                'name': cat_name,
                'color': cat['color'],
                'icon': cat['icon'],
                'count': 0
            }
        categories[cat_name]['count'] += 1
    
    # 生成分类标签HTML
    category_tabs = ''
    for i, (name, cat) in enumerate(categories.items()):
        active = 'active' if i == 0 else ''
        category_tabs += f'''
            <button class="tab-button {active}" data-category="{name}">
                <span class="tab-icon">{cat['icon']}</span>
                <span class="tab-text">{name}</span>
                <span class="tab-count">{cat['count']}</span>
            </button>'''
    
    # 生成新闻卡片HTML
    news_cards = ''
    for i, article in enumerate(articles):
        importance_stars = '★' * article['importance']
        priority_class = 'priority-high' if article['importance'] >= 4 else 'priority-medium' if article['importance'] >= 2 else 'priority-low'
        
        news_cards += f'''
            <article class="news-card {priority_class}" data-category="{article['category']['name']}" 
                     onclick="window.location.href='news/{article['id']}.html'" 
                     style="animation-delay: {i * 0.05}s;">
                <div class="priority-indicator"></div>
                <div class="importance-stars">
                    {importance_stars}
                </div>
                <div class="card-header">
                    <div class="category-badge" style="background-color: {article['category']['color']}; color: white;">
                        <span>{article['category']['icon']}</span>
                        <span>{article['category']['name']}</span>
                    </div>
                    <h2 class="news-title">{article['title']}</h2>
                    <p class="news-description">{article['description']}</p>
                </div>
                <div class="card-footer">
                    <div class="source">
                        <span>📰</span>
                        <span>{article['source']}</span>
                    </div>
                    <div class="read-more">
                        查看详情
                    </div>
                </div>
            </article>'''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI科技日报 - 人工智能前沿资讯</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIzMiIgaGVpZ2h0PSIzMiIgdmlld0JveD0iMCAwIDEwMCAxMDAiPjx0ZXh0IHk9Ii45ZW0iIGZvbnQtc2l6ZT0iOTAiPvCfpok8L3RleHQ+PC9zdmc+">
    <meta name="description" content="专为中国用户设计的AI科技资讯平台，提供最新人工智能技术动态、投资分析和市场洞察">
    <style>
        :root {{
            --color-primary: #007AFF;
            --color-success: #34C759;
            --color-warning: #FF9500;
            --color-danger: #FF3B30;
            --color-purple: #5856D6;
            --color-gray: #8E8E93;
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --bg-tertiary: #2C2C2E;
            --text-primary: #FFFFFF;
            --text-secondary: #98989D;
            --border-color: #38383A;
            --shadow-light: rgba(255, 255, 255, 0.1);
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            min-height: 100vh;
        }}

        .header {{
            text-align: center;
            padding: 2rem 1rem 1rem;
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
            border-bottom: 1px solid var(--border-color);
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #FF6B6B, #4ECDC4, #45B7D1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .header .subtitle {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}

        .tab-container {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            overflow-x: auto;
        }}

        .tab-list {{
            display: flex;
            justify-content: center;
            gap: 0.5rem;
            padding: 1rem;
            min-width: max-content;
        }}

        .tab-button {{
            background: transparent;
            border: 2px solid var(--border-color);
            border-radius: 20px;
            padding: 0.75rem 1.5rem;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            white-space: nowrap;
        }}

        .tab-button.active {{
            background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
            border-color: transparent;
            color: white;
            transform: scale(1.05);
        }}

        .tab-count {{
            background: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 0.25rem 0.5rem;
            font-size: 0.75rem;
            font-weight: bold;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}

        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
        }}

        .news-card {{
            background: linear-gradient(145deg, var(--bg-secondary), var(--bg-tertiary));
            border-radius: 16px;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            cursor: pointer;
            transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            transform: translateY(20px);
            position: relative;
        }}

        .news-card:hover {{
            transform: translateY(-4px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0, 122, 255, 0.3);
            border-color: var(--color-primary);
        }}

        .priority-indicator {{
            position: absolute;
            top: 0;
            right: 0;
            width: 8px;
            height: 100%;
            border-radius: 0 16px 16px 0;
            background: var(--color-success);
        }}

        .priority-high .priority-indicator {{ background: var(--color-danger); }}
        .priority-medium .priority-indicator {{ background: var(--color-warning); }}

        .importance-stars {{
            position: absolute;
            top: 1rem;
            right: 1.5rem;
            font-size: 0.75rem;
            color: #FFD700;
        }}

        .category-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}

        .news-title {{
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            line-height: 1.4;
            color: var(--text-primary);
        }}

        .news-description {{
            color: var(--text-secondary);
            margin-bottom: 1rem;
            line-height: 1.5;
            font-size: 0.9rem;
        }}

        .card-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }}

        .source {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}

        .read-more {{
            color: var(--color-primary);
            font-weight: 600;
            font-size: 0.875rem;
        }}

        @keyframes fadeInUp {{
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .news-grid {{ grid-template-columns: 1fr; }}
            .tab-list {{ justify-content: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI科技日报</h1>
        <p class="subtitle">{datetime.now().strftime('%Y年%m月%d日')} · 人工智能前沿资讯</p>
    </div>

    <div class="tab-container">
        <div class="tab-list">
            <button class="tab-button active" data-category="全部">
                <span class="tab-icon">📋</span>
                <span class="tab-text">全部</span>
                <span class="tab-count">{len(articles)}</span>
            </button>
            {category_tabs}
        </div>
    </div>

    <div class="container">
        <div class="content-area">
            <div class="news-grid">
            {news_cards}
            </div>
        </div>
    </div>

    <script>
        // 分类筛选功能
        document.querySelectorAll('.tab-button').forEach(button => {{
            button.addEventListener('click', () => {{
                // 移除其他活动状态
                document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
                button.classList.add('active');
                
                const category = button.getAttribute('data-category');
                const cards = document.querySelectorAll('.news-card');
                
                cards.forEach(card => {{
                    if (category === '全部' || card.getAttribute('data-category') === category) {{
                        card.style.display = 'block';
                    }} else {{
                        card.style.display = 'none';
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>'''

def generate_detail_html(article, all_articles):
    """生成详情页HTML"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - AI科技日报</title>
    <style>
        :root {{
            --color-primary: #007AFF;
            --color-success: #34C759;
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --bg-tertiary: #2C2C2E;
            --text-primary: #FFFFFF;
            --text-secondary: #98989D;
            --border-color: #38383A;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: linear-gradient(135deg, var(--bg-primary), var(--bg-secondary));
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}
        
        .back-button {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--color-primary);
            text-decoration: none;
            margin-bottom: 2rem;
            font-weight: 600;
        }}
        
        .article-header {{
            margin-bottom: 2rem;
        }}
        
        .article-title {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            line-height: 1.3;
        }}
        
        .article-meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            color: var(--text-secondary);
        }}
        
        .article-content {{
            background: var(--bg-secondary);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
        }}
        
        .section {{
            margin-bottom: 2rem;
        }}
        
        .section h3 {{
            color: var(--color-primary);
            margin-bottom: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-button">
            ← 返回首页
        </a>
        
        <div class="article-header">
            <h1 class="article-title">{article['title']}</h1>
            <div class="article-meta">
                <span>📰 {article['source']}</span>
                <span>⭐ {article['importance']}星</span>
            </div>
        </div>
        
        <div class="article-content">
            <div class="section">
                <h3>📄 内容摘要</h3>
                <p>{article['description']}</p>
            </div>
            
            <div class="section">
                <h3>🇨🇳 中国影响分析</h3>
                <p>{article['china_analysis']}</p>
            </div>
            
            <div class="section">
                <h3>💰 投资洞察</h3>
                <p>{article['investment_insight']}</p>
            </div>
            
            <div class="section">
                <h3>🔗 原文链接</h3>
                <a href="{article['url']}" target="_blank" style="color: var(--color-primary);">查看原文</a>
            </div>
        </div>
    </div>
</body>
</html>'''

if __name__ == "__main__":
    generate_html_from_json()