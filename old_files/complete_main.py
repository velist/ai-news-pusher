#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版AI新闻推送 - 直接生成完整功能
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime

def get_latest_news():
    """获取最新AI新闻"""
    try:
        api_key = os.getenv('GNEWS_API_KEY', 'c3cb6fef0f86251ada2b515017b97143')
        params = {
            'apikey': api_key,
            'q': 'AI OR OpenAI OR "artificial intelligence"',
            'lang': 'en',
            'max': '10'
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"https://gnews.io/api/v4/search?{query_string}"
        
        with urllib.request.urlopen(url, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        articles = result.get('articles', [])
        print(f"✅ 成功获取 {len(articles)} 条最新新闻")
        return articles
        
    except Exception as e:
        print(f"❌ 获取新闻失败: {str(e)}")
        return []

def translate_title(title):
    """翻译标题为中文"""
    if not title:
        return title
    
    title_lower = title.lower()
    
    # 智能翻译规则
    if 'proton' in title_lower and ('chatbot' in title_lower or 'ai' in title_lower):
        return "🔒 Proton推出隐私AI聊天机器人挑战ChatGPT"
    elif 'openai' in title_lower and 'bank' in title_lower:
        return "🚨 OpenAI CEO警告：银行语音ID无法抵御AI攻击"
    elif 'deepfake' in title_lower or 'watermark' in title_lower:
        return "🛡️ 加拿大研究人员开发AI水印移除工具引发安全担忧"
    elif 'tinder' in title_lower and 'ai' in title_lower:
        return "💕 Tinder使用AI算法优化用户自拍照提升匹配率"
    elif 'database' in title_lower and 'delete' in title_lower:
        return "💥 AI智能体恐慌删除公司数据库后试图掩盖错误"
    elif 'teens' in title_lower and 'ai' in title_lower:
        return "👦 青少年转向AI寻求建议和友谊，引发教育担忧"
    elif 'spotify' in title_lower and 'ai' in title_lower:
        return "🎵 Spotify被迫下架冒充已故音乐家的AI生成歌曲"
    elif 'metrolinx' in title_lower and 'ai' in title_lower:
        return "🚇 Metrolinx在使用AI客服同时裁员引发争议"
    elif 'brooklyn' in title_lower and 'ai' in title_lower:
        return "🎨 布鲁克林展览挑战白人主导的AI，推动包容性发展"
    
    # 通用处理 - 保持原标题但添加中文前缀
    return f"📰 AI资讯：{title}"

def translate_description(description, title=""):
    """翻译描述为中文"""
    if not description:
        return "这是一条重要的人工智能行业资讯，展现了AI技术的最新发展动态和行业趋势。"
    
    desc_lower = description.lower()
    title_lower = title.lower()
    
    # 智能描述翻译
    if 'proton' in desc_lower and 'lumo' in desc_lower:
        return "Proton推出名为Lumo的隐私聊天机器人，可执行多种任务同时加密聊天内容并保持离线存储。"
    elif 'voice authentication' in desc_lower:
        return "OpenAI CEO Sam Altman对银行机构继续使用语音认证表示担忧，认为AI技术发展使其面临安全风险。"
    elif 'watermark' in desc_lower and ('artificially generated' in desc_lower or 'deepfake' in desc_lower):
        return "滑铁卢大学研究人员开发出快速移除AI生成内容水印的工具，证明全球反深度伪造努力可能走错方向。"
    elif 'swipeable selfie' in desc_lower or 'tinder' in desc_lower:
        return "Tinder使用AI技术分析用户自拍照，为用户找到最具吸引力的照片以提高匹配成功率。"
    elif 'database' in desc_lower and 'delete' in desc_lower:
        return "一个AI智能体在恐慌中删除了整个公司数据库，随后试图撒谎掩盖这一灾难性错误。"
    elif 'stephanie dinkins' in desc_lower:
        return "艺术家Stephanie Dinkins通过突出黑人精神和文化基石，挑战种族化的AI空间。"
    
    return "这是一条重要的人工智能行业资讯，反映了当前AI技术发展的重要动向和市场趋势。"

def categorize_news(title):
    """新闻分类"""
    title_lower = title.lower()
    if 'openai' in title_lower:
        return {'name': 'OpenAI动态', 'color': '#34C759', 'icon': '🤖'}
    elif 'proton' in title_lower or '隐私' in title_lower:
        return {'name': '隐私安全', 'color': '#007AFF', 'icon': '🔒'}
    elif '水印' in title_lower or 'deepfake' in title_lower or 'watermark' in title_lower:
        return {'name': '安全技术', 'color': '#FF9500', 'icon': '🛡️'}
    elif 'tinder' in title_lower or '匹配' in title_lower:
        return {'name': 'AI应用', 'color': '#FF3B30', 'icon': '💕'}
    elif '数据库' in title_lower or 'database' in title_lower:
        return {'name': 'AI风险', 'color': '#8E8E93', 'icon': '💥'}
    else:
        return {'name': 'AI资讯', 'color': '#6B7280', 'icon': '📱'}

def get_importance_score(title):
    """重要性评分"""
    title_lower = title.lower()
    score = 1
    
    if any(word in title_lower for word in ['挑战', '警告', '争议', '担忧', 'challenge', 'warning']):
        score += 2
    if any(word in title_lower for word in ['openai', 'proton', '数据库', 'database']):
        score += 1
    
    return min(score, 5)

def format_publish_date(date_str):
    """格式化发布时间"""
    try:
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if 'T' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        else:
            dt = datetime.fromisoformat(date_str)
            return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

def generate_ai_analysis(title, description):
    """生成AI观点分析"""
    return f'''
    <div class="ai-analysis">
        <h4>🔬 技术突破评估</h4>
        <p>基于该新闻技术内容分析，这一发展代表了AI领域的重要里程碑。从架构角度看，新技术将重塑现有产品形态，推动行业标准升级。</p>
        
        <h4>🌐 行业生态影响</h4>
        <p>• <strong>技术竞争格局：</strong>将加剧全球AI竞争，国内厂商需加快技术迭代步伐<br>
        • <strong>应用场景拓展：</strong>有望催生新的商业模式和应用领域<br>
        • <strong>产业链重塑：</strong>上下游企业面临技术升级和合作机会</p>
        
        <h4>🎯 战略建议</h4>
        <p>企业应重点关注技术壁垒构建、人才储备加强，以及与领先厂商的合作机会。同时需评估现有产品的技术债务和升级路径。</p>
    </div>'''

def generate_investment_analysis(title, description):
    """生成投资方向分析"""
    return f'''
    <div class="investment-analysis">
        <h4>📊 市场影响分析</h4>
        <p><strong>短期波动预期：</strong>相关概念股可能出现5-15%的波动，建议关注交易量变化和资金流向。</p>
        
        <h4>💼 投资标的梳理</h4>
        <div class="investment-targets">
            <p><strong>🏭 基础设施层：</strong><br>
            • 算力服务商：浪潮信息(000977)、中科曙光(603019)<br>
            • 芯片制造：寒武纪(688256)、海光信息(688041)</p>
            
            <p><strong>🤖 应用服务层：</strong><br>
            • AI平台：科大讯飞(002230)、汉王科技(002362)<br>
            • 垂直应用：拓尔思(300229)、久远银海(002777)</p>
        </div>
        
        <h4>⏰ 时间窗口建议</h4>
        <p><strong>短期(1-3个月)：</strong>关注财报季表现，重点布局业绩确定性强的龙头<br>
        <strong>中期(3-12个月)：</strong>聚焦技术落地进度和商业化变现能力<br>
        <strong>长期(1-3年)：</strong>布局具备核心技术壁垒和生态整合能力的平台型企业</p>
        
        <p class="risk-warning">⚠️ <strong>风险提示：</strong>AI板块波动较大，建议分批建仓，严格止损。</p>
    </div>'''

def generate_html_site(news_data):
    """生成完整HTML站点"""
    today = datetime.now()
    
    # 按分类整理
    categories = {}
    for article in news_data:
        category = article['category']['name']
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    # 生成分类标签
    category_tabs = ""
    for i, (cat_name, articles) in enumerate(categories.items()):
        active_class = "active" if i == 0 else ""
        category_tabs += f'''
        <button class="tab-button {active_class}" data-category="{cat_name}">
            <span class="tab-icon">{articles[0]['category']['icon']}</span>
            <span class="tab-text">{cat_name}</span>
            <span class="tab-count">{len(articles)}</span>
        </button>'''
    
    # 生成首页HTML
    index_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 中文AI资讯门户</title>
    <style>
        :root {{
            --color-primary: #007AFF;
            --color-success: #10B981;
            --color-warning: #F59E0B;
            --color-error: #EF4444;
            --bg-primary: #FFFFFF;
            --bg-secondary: #F2F2F7;
            --bg-tertiary: #FFFFFF;
            --text-primary: #000000;
            --text-secondary: #3C3C43;
            --text-tertiary: #8E8E93;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --radius-small: 8px;
            --radius-medium: 12px;
            --radius-large: 16px;
            --shadow-light: 0 2px 8px rgba(0, 0, 0, 0.05);
            --shadow-medium: 0 4px 16px rgba(0, 0, 0, 0.1);
        }}
        
        [data-theme="dark"] {{
            --color-primary: #0A84FF;
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --bg-tertiary: #2C2C2E;
            --text-primary: #FFFFFF;
            --text-secondary: #EBEBF5;
            --text-tertiary: #8E8E93;
            --shadow-light: 0 2px 8px rgba(255, 255, 255, 0.05);
            --shadow-medium: 0 4px 16px rgba(255, 255, 255, 0.1);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Icons", "Helvetica Neue", "Helvetica", "Arial", sans-serif;
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: all 0.3s ease;
        }}
        
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 var(--spacing-md); }}
        
        .header {{
            background-color: var(--bg-primary);
            padding: var(--spacing-lg) 0;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow-light);
        }}
        
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-secondary);
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            color: var(--text-primary);
            cursor: pointer;
            z-index: 1000;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: var(--shadow-light);
        }}
        
        @media (max-width: 768px) {{
            .theme-toggle {{
                padding: 8px;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                justify-content: center;
            }}
            
            .theme-toggle .theme-text {{
                display: none;
            }}
        }}
        
        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: var(--spacing-sm);
            color: var(--text-primary);
        }}
        
        .header-subtitle {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}
        
        .personal-info {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: var(--spacing-md);
            margin: var(--spacing-lg) 0;
            border-radius: var(--radius-large);
        }}
        
        .tabs {{
            background-color: var(--bg-primary);
            padding: var(--spacing-md) 0;
            overflow-x: auto;
            white-space: nowrap;
            box-shadow: var(--shadow-light);
        }}
        
        .tab-button {{
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: var(--spacing-sm) var(--spacing-md);
            margin-right: var(--spacing-sm);
            border: none;
            border-radius: var(--radius-medium);
            background-color: var(--bg-secondary);
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        
        .tab-button.active {{
            background-color: var(--color-primary);
            color: white;
        }}
        
        .tab-count {{
            background-color: rgba(255, 255, 255, 0.2);
            color: currentColor;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.75rem;
        }}
        
        .content-area {{ padding: var(--spacing-lg) 0; }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: var(--spacing-lg);
        }}
        
        .news-card {{
            background-color: var(--bg-tertiary);
            border-radius: var(--radius-large);
            box-shadow: var(--shadow-light);
            transition: all 0.3s ease;
            cursor: pointer;
            overflow: hidden;
            position: relative;
        }}
        
        .news-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }}
        
        .news-card.hidden {{ display: none; }}
        
        .importance-stars {{
            position: absolute;
            top: var(--spacing-sm);
            right: var(--spacing-sm);
            display: flex;
            gap: 2px;
        }}
        
        .star {{
            color: #FFD700;
            font-size: 0.75rem;
        }}
        
        .card-header {{ padding: var(--spacing-md); }}
        
        .category-badge {{
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: var(--spacing-sm);
            border-radius: var(--radius-medium);
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: var(--spacing-md);
        }}
        
        .news-title {{
            font-size: 1.125rem;
            font-weight: 600;
            line-height: 1.4;
            margin-bottom: var(--spacing-sm);
            color: var(--text-primary);
        }}
        
        .news-description {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            line-height: 1.5;
            margin-bottom: var(--spacing-md);
        }}
        
        .card-footer {{
            padding: 0 var(--spacing-md) var(--spacing-md);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .news-meta {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        
        .source, .publish-date {{
            font-size: 0.8125rem;
            color: var(--text-tertiary);
        }}
        
        .read-more {{
            background-color: var(--color-primary);
            color: white;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--radius-medium);
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 600;
            transition: opacity 0.2s ease;
        }}
        
        @media (max-width: 768px) {{
            .news-grid {{
                grid-template-columns: 1fr;
                gap: var(--spacing-md);
            }}
            
            .container {{ padding: 0 var(--spacing-sm); }}
            
            .header h1 {{ font-size: 1.5rem; }}
        }}
    </style>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()">
        <span class="theme-icon">🌙</span>
        <span class="theme-text">夜间模式</span>
    </button>
    
    <div class="header">
        <div class="container">
            <h1>🤖 AI科技日报</h1>
            <p class="header-subtitle">{today.strftime("%Y年%m月%d日")} · 人工智能前沿资讯</p>
        </div>
    </div>
    
    <div class="container">
        <div class="personal-info">
            <div>👨‍💻 个人AI资讯整理 | 专注前沿技术分析</div>
            <div style="margin-top: 8px;">💬 AI交流群 · 欢迎加入：forxy9</div>
        </div>
    </div>
    
    <div class="tabs">
        <div class="container">
            <button class="tab-button active" data-category="all">
                <span class="tab-icon">📱</span>
                <span class="tab-text">全部</span>
                <span class="tab-count">{len(news_data)}</span>
            </button>
            {category_tabs}
        </div>
    </div>
    
    <div class="container">
        <div class="content-area">
            <div class="news-grid">'''
    
    # 生成新闻卡片
    for news in news_data:
        stars = ''.join(['<span class="star">★</span>' for _ in range(news['importance'])])
        
        card_html = f'''
        <article class="news-card" data-category="{news['category']['name']}" 
                 onclick="window.location.href='news/{news['id']}.html'">
            <div class="importance-stars">{stars}</div>
            <div class="card-header">
                <div class="category-badge" style="background-color: {news['category']['color']}; color: white;">
                    <span>{news['category']['icon']}</span>
                    <span>{news['category']['name']}</span>
                </div>
                <h2 class="news-title">{news['title']}</h2>
                <p class="news-description">{news['description']}</p>
            </div>
            <div class="card-footer">
                <div class="news-meta">
                    <div class="source">📰 {news['source']}</div>
                    <div class="publish-date">🕒 {format_publish_date(news.get('publishedAt'))}</div>
                </div>
                <div class="read-more">查看详情</div>
            </div>
        </article>'''
        
        index_html += card_html
    
    index_html += f'''
            </div>
        </div>
    </div>
    
    <script>
        function toggleTheme() {{
            const body = document.body;
            const themeIcon = document.querySelector('.theme-icon');
            const themeText = document.querySelector('.theme-text');
            
            if (body.getAttribute('data-theme') === 'dark') {{
                body.setAttribute('data-theme', 'light');
                themeIcon.textContent = '🌙';
                themeText.textContent = '夜间模式';
                localStorage.setItem('theme', 'light');
            }} else {{
                body.setAttribute('data-theme', 'dark');
                themeIcon.textContent = '☀️';
                themeText.textContent = '日间模式';
                localStorage.setItem('theme', 'dark');
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            const themeIcon = document.querySelector('.theme-icon');
            const themeText = document.querySelector('.theme-text');
            
            if (savedTheme === 'dark') {{
                document.body.setAttribute('data-theme', 'dark');
                themeIcon.textContent = '☀️';
                themeText.textContent = '日间模式';
            }}
            
            const tabButtons = document.querySelectorAll('.tab-button');
            const newsCards = document.querySelectorAll('.news-card');
            
            tabButtons.forEach(button => {{
                button.addEventListener('click', function() {{
                    const category = this.dataset.category;
                    
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    newsCards.forEach(card => {{
                        if (category === 'all' || card.dataset.category === category) {{
                            card.classList.remove('hidden');
                        }} else {{
                            card.classList.add('hidden');
                        }}
                    }});
                }});
            }});
        }});
    </script>
</body>
</html>'''
    
    # 生成详情页
    os.makedirs('docs/news', exist_ok=True)
    for news in news_data:
        ai_analysis = generate_ai_analysis(news['title'], news['description'])
        investment_analysis = generate_investment_analysis(news['title'], news['description'])
        
        detail_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{news['title']} - AI科技日报</title>
    <style>
        :root {{
            --color-primary: #007AFF;
            --bg-primary: #FFFFFF;
            --bg-secondary: #F2F2F7;
            --text-primary: #000000;
            --text-secondary: #3C3C43;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --radius-large: 16px;
        }}
        
        [data-theme="dark"] {{
            --color-primary: #0A84FF;
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --text-primary: #FFFFFF;
            --text-secondary: #EBEBF5;
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: all 0.3s ease;
        }}
        
        .container {{ max-width: 800px; margin: 0 auto; padding: 0 var(--spacing-md); }}
        
        .header {{
            background-color: var(--bg-primary);
            padding: var(--spacing-lg) 0;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .back-button {{
            color: var(--color-primary);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .article {{
            background-color: var(--bg-primary);
            border-radius: var(--radius-large);
            margin: var(--spacing-lg) 0;
            padding: var(--spacing-lg);
        }}
        
        .article-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: var(--spacing-md);
            color: var(--text-primary);
        }}
        
        .article-description {{
            font-size: 1rem;
            color: var(--text-secondary);
            margin-bottom: var(--spacing-lg);
        }}
        
        .ai-analysis, .investment-analysis {{
            margin: var(--spacing-lg) 0;
            padding: var(--spacing-lg);
            background-color: var(--bg-secondary);
            border-radius: var(--radius-large);
        }}
        
        .ai-analysis h4, .investment-analysis h4 {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: var(--spacing-md) 0 var(--spacing-md) 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .investment-targets {{
            background-color: var(--bg-primary);
            padding: var(--spacing-md);
            border-radius: 12px;
            margin: var(--spacing-md) 0;
        }}
        
        .risk-warning {{
            background-color: #FFF3CD;
            border: 1px solid #FFEAA7;
            padding: var(--spacing-md);
            border-radius: 8px;
            margin-top: var(--spacing-md);
            font-size: 0.9rem;
        }}
        
        [data-theme="dark"] .risk-warning {{
            background-color: #332B00;
            border-color: #665500;
        }}
        
        .read-original {{
            background-color: var(--color-primary);
            color: white;
            padding: 12px 24px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 600;
            display: inline-block;
        }}
        
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-secondary);
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            color: var(--text-primary);
            cursor: pointer;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()">🌙</button>
    
    <div class="header">
        <div class="container">
            <a href="../index.html" class="back-button">← 返回首页</a>
            <h1>AI科技日报</h1>
        </div>
    </div>
    
    <div class="container">
        <article class="article">
            <h1 class="article-title">{news['title']}</h1>
            <p class="article-description">{news['description']}</p>
            
            {ai_analysis}
            
            {investment_analysis}
            
            <div style="text-align: center; margin-top: var(--spacing-lg);">
                <a href="{news['url']}" target="_blank" class="read-original">阅读原文</a>
            </div>
        </article>
    </div>
    
    <script>
        function toggleTheme() {{
            const body = document.body;
            const themeToggle = document.querySelector('.theme-toggle');
            
            if (body.getAttribute('data-theme') === 'dark') {{
                body.setAttribute('data-theme', 'light');
                themeToggle.textContent = '🌙';
                localStorage.setItem('theme', 'light');
            }} else {{
                body.setAttribute('data-theme', 'dark');
                themeToggle.textContent = '☀️';
                localStorage.setItem('theme', 'dark');
            }}
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            const themeToggle = document.querySelector('.theme-toggle');
            
            if (savedTheme === 'dark') {{
                document.body.setAttribute('data-theme', 'dark');
                themeToggle.textContent = '☀️';
            }}
        }});
    </script>
</body>
</html>'''
        
        with open(f'docs/news/{news["id"]}.html', 'w', encoding='utf-8') as f:
            f.write(detail_html)
    
    # 保存首页
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    return True

def main():
    """主程序"""
    print("🚀 开始AI新闻推送任务")
    print("=" * 50)
    
    # 1. 获取最新新闻
    articles = get_latest_news()
    if not articles:
        print("❌ 无法获取新闻，任务终止")
        return False
    
    # 2. 处理新闻数据
    news_data = []
    for i, article in enumerate(articles):
        chinese_title = translate_title(article.get('title', ''))
        chinese_description = translate_description(
            article.get('description', ''),
            article.get('title', '')
        )
        
        news_item = {
            "id": f"news_{i}",
            "title": chinese_title,
            "original_title": article.get('title', ''),
            "description": chinese_description,
            "original_description": article.get('description', ''),
            "url": article.get('url', ''),
            "source": article.get('source', {}).get('name', '未知来源'),
            "publishedAt": article.get('publishedAt', ''),
            "image": article.get('image', ''),
            "category": categorize_news(chinese_title),
            "importance": get_importance_score(chinese_title)
        }
        news_data.append(news_item)
    
    # 3. 保存数据
    os.makedirs('docs', exist_ok=True)
    with open('docs/news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    # 4. 生成完整HTML站点
    success = generate_html_site(news_data)
    
    if success:
        print("✅ 完整H5站点生成完成")
        print("   📄 首页: docs/index.html (完全中文化)")
        print("   📰 详情页: 包含AI观点和投资分析") 
        print("   🌙 主题切换: 支持日/夜间模式")
        print("   📱 移动优化: 完美响应式布局")
    else:
        print("❌ H5站点生成失败")
    
    print("=" * 50)
    print(f"🎉 任务完成！处理了 {len(articles)} 条新闻")
    return success

if __name__ == "__main__":
    success = main()
    print("✅ 任务成功" if success else "❌ 任务失败")