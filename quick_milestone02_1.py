#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
里程碑02.1快速测试版 - 验证新功能
1. 全部Tab分类
2. 模型分类
3. 详情页结构优化
"""

import json
from datetime import datetime, timezone, timedelta

# 读取现有数据
with open('docs/enhanced_news_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

articles = data['articles']

def categorize_article_new(title, summary):
    """重新分类，添加模型分类"""
    title_lower = title.lower()
    summary_lower = summary.lower()
    combined = (title_lower + " " + summary_lower)
    
    # 模型相关关键词 (新增分类)
    model_keywords = [
        'gpt', 'chatgpt', 'gemini', 'claude', 'llama', 'qwen', 'baichuan', 'chatglm',
        'model', 'llm', 'large language model', 'ai model', 'neural network',
        'transformer', 'bert', 'dall-e', 'midjourney', 'stable diffusion',
        '通义', '文心', '混元', '智谱', '百川', '讯飞', 'minimax'
    ]
    
    if any(word in combined for word in model_keywords):
        return '模型', '🤖'
    
    # 投资并购关键词
    elif any(word in combined for word in ['funding', 'investment', 'raise', 'billion', 'million', 'valuation', 'ipo', 'acquisition', 'merger']):
        return '投资并购', '💰'
    
    # 公司动态关键词
    elif any(word in combined for word in ['openai', 'google', 'microsoft', 'apple', 'meta', 'amazon', 'nvidia', 'anthropic', 'baidu', 'alibaba', 'tencent']):
        return '公司动态', '🏢'
    
    # 技术突破关键词
    elif any(word in combined for word in ['breakthrough', 'research', 'algorithm', 'technology', 'innovation', 'development', 'discovery']):
        return '技术突破', '🚀'
    
    # 政策监管关键词
    elif any(word in combined for word in ['regulation', 'policy', 'government', 'law', 'compliance', 'ethics', 'safety']):
        return '政策监管', '⚖️'
    
    # 行业应用关键词
    elif any(word in combined for word in ['application', 'healthcare', 'finance', 'education', 'automotive', 'industry']):
        return '行业应用', '🎯'
    
    # 默认为热门
    return '热门', '🔥'

# 重新分类所有文章
for article in articles:
    new_category, new_icon = categorize_article_new(article['title'], article['summary'])
    article['category'] = new_category
    article['category_icon'] = new_icon

# 生成改进的主页HTML
def generate_improved_main_page(articles):
    """生成包含全部分类的主页"""
    
    # 按分类组织文章
    categories = {}
    for article in articles:
        cat = article['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(article)
    
    # 生成分类tabs - 添加"全部"分类
    category_tabs = []
    category_contents = []
    
    # 全部分类排在第一位
    all_categories = ['全部', '热门', '模型', '公司动态', '技术突破', '行业应用', '投资并购', '政策监管']
    
    for i, cat in enumerate(all_categories):
        if cat == '全部':
            # 全部分类显示所有文章
            cat_articles = articles
            icon = '📰'
        else:
            cat_articles = categories.get(cat, [])
            icon = cat_articles[0]['category_icon'] if cat_articles else '📰'
        
        if cat_articles:  # 只显示有文章的分类
            # Tab按钮
            active_class = 'active' if i == 0 else ''
            category_tabs.append(f'''
                <div class="tab {active_class}" data-category="{cat}">
                    {icon} {cat} ({len(cat_articles)})
                </div>
            ''')
            
            # Tab内容
            news_cards = []
            for article in cat_articles:
                display_title = article.get('translated_title', article['title'])
                display_summary = article.get('translated_summary', article['summary'])
                
                news_cards.append(f'''
                    <div class="news-card">
                        <div class="news-meta">
                            <span class="news-source">{article['source']}</span>
                            <span class="news-time">{article['time']}</span>
                            <span class="news-category">{article['category_icon']} {article['category']}</span>
                        </div>
                        <h3 class="news-title">
                            <a href="news/{article['id']}.html">{display_title}</a>
                        </h3>
                        <p class="news-summary">{display_summary}</p>
                        <div class="news-footer">
                            <a href="news/{article['id']}.html" class="read-more">阅读全文 →</a>
                        </div>
                    </div>
                ''')
            
            category_contents.append(f'''
                <div class="tab-content {active_class}" id="{cat}">
                    <div class="news-grid">
                        {''.join(news_cards)}
                    </div>
                </div>
            ''')
    
    # 获取北京时间
    beijing_tz = timezone(timedelta(hours=8))
    beijing_time = datetime.now(beijing_tz)
    formatted_time = beijing_time.strftime("%Y年%m月%d日 %H:%M")
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 专业AI资讯平台</title>
    <meta name="description" content="专注AI前沿资讯，提供OpenAI、ChatGPT、AI模型等最新动态，智能翻译+专家点评，您的AI信息门户">
    <meta name="keywords" content="AI新闻,人工智能,OpenAI,ChatGPT,AI投资,AI技术,AI应用,AI模型,Gemini,Claude">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "SimSun", sans-serif;
            line-height: 1.6; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: #333;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        
        .header {{ 
            text-align: center; background: rgba(255,255,255,0.95); 
            border-radius: 24px; padding: 40px 30px; margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .header h1 {{ 
            font-size: 3em; margin-bottom: 15px; font-weight: 800;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; letter-spacing: -1px;
        }}
        
        .header .subtitle {{ 
            color: #666; font-size: 1.2em; margin-bottom: 25px; font-weight: 400;
        }}
        
        .update-time {{ 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 12px 28px; border-radius: 30px; 
            display: inline-block; font-weight: 600; font-size: 1.1em;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        
        /* 横向滑动的Tab样式 */
        .tabs-container {{
            background: rgba(255,255,255,0.9); 
            border-radius: 20px; 
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .tabs {{ 
            display: flex; 
            overflow-x: auto; 
            padding: 20px;
            gap: 15px;
            scrollbar-width: none; /* Firefox */
            -ms-overflow-style: none; /* IE 10+ */
        }}
        
        .tabs::-webkit-scrollbar {{ display: none; }} /* Chrome/Safari */
        
        .tab {{ 
            background: rgba(255,255,255,0.8); 
            color: #555; 
            border: 2px solid rgba(0,0,0,0.1);
            padding: 15px 25px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 1.1em; 
            font-weight: 600; 
            transition: all 0.3s ease;
            display: flex; 
            align-items: center; 
            gap: 8px; 
            white-space: nowrap;
            flex-shrink: 0; /* 防止Tab收缩 */
            min-width: fit-content;
        }}
        
        .tab:hover {{ 
            background: rgba(102, 126, 234, 0.1); 
            border-color: #667eea;
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }}
        
        .tab.active {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            border-color: transparent;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        .news-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); 
            gap: 30px; 
            margin-top: 20px;
        }}
        
        .news-card {{ 
            background: rgba(255,255,255,0.95); 
            border-radius: 20px; 
            padding: 30px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px); 
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease; 
            height: fit-content;
        }}
        
        .news-card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}
        
        .news-meta {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin-bottom: 15px; 
            font-size: 0.9em; 
            color: #666;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .news-source {{ 
            background: rgba(102, 126, 234, 0.1); 
            color: #667eea; 
            padding: 6px 12px; 
            border-radius: 15px; 
            font-weight: 600;
        }}
        
        .news-category {{
            background: rgba(118, 75, 162, 0.1);
            color: #764ba2;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .news-time {{ font-weight: 500; }}
        
        .news-title {{ 
            font-size: 1.4em; 
            margin-bottom: 15px; 
            font-weight: 700; 
            line-height: 1.3;
        }}
        
        .news-title a {{ 
            color: #333; 
            text-decoration: none; 
            transition: color 0.3s ease;
        }}
        
        .news-title a:hover {{ color: #667eea; }}
        
        .news-summary {{ 
            color: #666; 
            margin-bottom: 20px; 
            line-height: 1.6;
        }}
        
        .news-footer {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        
        .read-more {{ 
            color: #667eea; 
            text-decoration: none; 
            font-weight: 600; 
            font-size: 1.1em;
            transition: all 0.3s ease;
        }}
        
        .read-more:hover {{ 
            color: #764ba2; 
            transform: translateX(5px);
        }}
        
        /* 移动端优化 */
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            
            .header {{ padding: 30px 20px; }}
            
            .header h1 {{ font-size: 2.2em; }}
            
            .tabs {{ padding: 15px; gap: 10px; }}
            
            .tab {{ 
                padding: 12px 20px; 
                font-size: 1em;
                min-width: 120px;
            }}
            
            .news-grid {{ 
                grid-template-columns: 1fr; 
                gap: 20px;
            }}
            
            .news-card {{ padding: 25px; }}
            
            .news-title {{ font-size: 1.2em; }}
            
            .news-meta {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}
        }}
        
        /* 超小屏幕优化 */
        @media (max-width: 480px) {{
            .header h1 {{ font-size: 1.8em; }}
            
            .header .subtitle {{ font-size: 1em; }}
            
            .update-time {{ 
                padding: 10px 20px; 
                font-size: 1em;
            }}
            
            .tab {{ 
                padding: 10px 16px; 
                min-width: 100px;
            }}
            
            .news-card {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">专注人工智能前沿资讯，每日精选优质内容</p>
            <div class="update-time">最后更新：{formatted_time}</div>
        </div>
        
        <div class="tabs-container">
            <div class="tabs">
                {''.join(category_tabs)}
            </div>
        </div>
        
        {''.join(category_contents)}
    </div>
    
    <script>
        // Tab切换功能
        document.addEventListener('DOMContentLoaded', function() {{
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {{
                tab.addEventListener('click', function() {{
                    const category = this.dataset.category;
                    
                    // 移除所有active类
                    tabs.forEach(t => t.classList.remove('active'));
                    contents.forEach(c => c.classList.remove('active'));
                    
                    // 添加active类到当前选中的
                    this.classList.add('active');
                    document.getElementById(category).classList.add('active');
                }});
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

# 生成改进的主页
print("🎯 生成里程碑02.1改进版主页...")
improved_html = generate_improved_main_page(articles)

# 保存到文件
with open('docs/index.html', 'w', encoding='utf-8') as f:
    f.write(improved_html)

print("✅ 里程碑02.1改进完成！")
print("📋 新增功能:")
print("  - ✅ 添加'全部'Tab分类")
print("  - ✅ 新增'模型'分类")
print("  - ✅ 重新分类所有文章")
print("  - ✅ 优化移动端显示")
print("🌐 访问地址: https://velist.github.io/ai-news-pusher/docs/")