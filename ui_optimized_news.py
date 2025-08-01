#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
界面优化版 - 专注于解决用户体验问题
先隐藏调试信息，创建分类tab，后续再集成翻译
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import sys
import hashlib

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
        except Exception:
            return False
    return False

def get_news_categories():
    """定义新闻分类配置"""
    return {
        "热门": {
            "queries": ["OpenAI OR ChatGPT OR GPT OR Claude", "AI breakthrough"],
            "icon": "🔥",
            "description": "最新最热的AI资讯",
            "max_per_query": 8
        },
        "公司动态": {
            "queries": ["OpenAI OR Anthropic OR Google AI", "AI company funding"],
            "icon": "🏢", 
            "description": "AI公司动态",
            "max_per_query": 6
        },
        "技术突破": {
            "queries": ["AI model OR machine learning", "AI research algorithm"],
            "icon": "🚀",
            "description": "前沿技术进展",
            "max_per_query": 6
        },
        "行业应用": {
            "queries": ["AI application OR AI tool", "AI automation"],
            "icon": "⚡",
            "description": "AI实际应用案例",
            "max_per_query": 6
        },
        "投资并购": {
            "queries": ["AI investment OR funding", "AI IPO venture"],
            "icon": "💰",
            "description": "投资与商业动态",
            "max_per_query": 5
        },
        "政策监管": {
            "queries": ["AI regulation policy", "AI law ethics"],
            "icon": "📋",
            "description": "政策法规动向",
            "max_per_query": 5
        }
    }

def fetch_categorized_news(api_key):
    """按分类获取新闻"""
    categories = get_news_categories()
    all_articles = []
    
    print("🔍 开始按分类获取新闻...")
    
    for category_name, config in categories.items():
        print(f"📰 获取 {config['icon']} {category_name} 新闻...")
        category_articles = []
        
        for query in config['queries']:
            try:
                params = {
                    "q": query,
                    "lang": "en",
                    "country": "us",
                    "max": config['max_per_query'],
                    "sortby": "publishedAt",
                    "apikey": api_key
                }
                
                query_string = urllib.parse.urlencode(params)
                url = f"https://gnews.io/api/v4/search?{query_string}"
                
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0 (compatible; NewsBot/1.0)')
                
                with urllib.request.urlopen(req, timeout=15) as response:
                    data = json.loads(response.read().decode())
                
                if 'articles' in data and data['articles']:
                    for article in data['articles']:
                        if article.get('title') and article.get('url'):
                            processed_article = {
                                "id": hashlib.md5(f"{article['url']}{article['title']}".encode()).hexdigest()[:12],
                                "title": article.get('title', '').strip(),
                                "summary": article.get('description', '').strip(),
                                "source": article.get('source', {}).get('name', '未知来源'),
                                "url": article.get('url', ''),
                                "category": category_name,
                                "category_icon": config['icon'],
                                "publishedAt": article.get('publishedAt'),
                                "image": article.get('image'),
                                "time": format_publish_time(article.get('publishedAt'))
                            }
                            category_articles.append(processed_article)
                    
                    print(f"  ✅ 获取到 {len(data['articles'])} 条")
                    
            except Exception as e:
                print(f"  ❌ 查询失败: {e}")
        
        # 去重并限制数量
        seen_urls = set()
        unique_articles = []
        for article in category_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 按发布时间排序
        unique_articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        final_articles = unique_articles[:8]  # 每个分类最多8条
        
        all_articles.extend(final_articles)
        print(f"  📊 {category_name} 保留 {len(final_articles)} 条")
    
    print(f"📊 总计获取 {len(all_articles)} 条新闻")
    return all_articles

def format_publish_time(published_at):
    """格式化发布时间"""
    if not published_at:
        return "时间未知"
    
    try:
        if published_at.endswith('Z'):
            published_time = datetime.fromisoformat(published_at[:-1])
        else:
            published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        
        now = datetime.now()
        time_diff = now - published_time.replace(tzinfo=None)
        
        if time_diff.days > 0:
            if time_diff.days == 1:
                return "昨天"
            elif time_diff.days < 7:
                return f"{time_diff.days}天前"
            else:
                return published_time.strftime("%m月%d日")
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"{hours}小时前"
        elif time_diff.seconds > 60:
            minutes = time_diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
            
    except Exception:
        return "时间未知"

def generate_clean_html(articles):
    """生成用户友好的HTML（隐藏技术信息）"""
    update_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    categories = get_news_categories()
    
    # 按分类组织文章
    categorized_articles = {}
    for category_name in categories.keys():
        categorized_articles[category_name] = [
            article for article in articles if article.get('category') == category_name
        ]
    
    # 添加"全部"分类
    categorized_articles = {"全部": articles, **categorized_articles}
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 专业AI资讯平台</title>
    <meta name="description" content="专注AI前沿资讯，提供OpenAI、ChatGPT等最新动态，您的专业AI信息门户">
    <meta name="keywords" content="AI新闻,人工智能,OpenAI,ChatGPT,AI投资,AI技术,AI应用">
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
        
        .stats {{ 
            display: flex; justify-content: center; gap: 40px; margin-top: 30px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{ 
            background: rgba(102, 126, 234, 0.1); padding: 20px 30px; 
            border-radius: 16px; text-align: center; min-width: 140px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }}
        
        .stat-number {{ 
            font-size: 2.2em; font-weight: 800; color: #667eea; 
            margin-bottom: 5px; display: block;
        }}
        
        .stat-label {{ font-size: 1em; color: #666; font-weight: 500; }}
        
        .tabs {{ 
            display: flex; gap: 15px; margin-bottom: 40px; 
            flex-wrap: wrap; justify-content: center;
            background: rgba(255,255,255,0.9); padding: 20px;
            border-radius: 20px; backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .tab {{ 
            background: rgba(255,255,255,0.8); color: #555; border: 2px solid rgba(0,0,0,0.1);
            padding: 15px 25px; border-radius: 25px; cursor: pointer; 
            font-size: 1.1em; font-weight: 600; transition: all 0.3s ease;
            display: flex; align-items: center; gap: 8px; white-space: nowrap;
        }}
        
        .tab:hover {{ 
            background: rgba(102, 126, 234, 0.1); border-color: #667eea;
            transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }}
        
        .tab.active {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; border-color: transparent;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        .news-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); 
            gap: 30px; margin-top: 20px;
        }}
        
        .news-card {{ 
            background: rgba(255,255,255,0.95); border-radius: 20px; 
            padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: all 0.4s ease; cursor: pointer; position: relative;
            backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.3);
            overflow: hidden;
        }}
        
        .news-card:hover {{ 
            transform: translateY(-8px); 
            box-shadow: 0 25px 60px rgba(0,0,0,0.15);
        }}
        
        .news-card::before {{ 
            content: ''; position: absolute; top: 0; left: 0; right: 0; 
            height: 5px; background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .category-tag {{ 
            position: absolute; top: 20px; right: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2); color: white;
            padding: 8px 16px; border-radius: 20px; font-size: 0.9em; 
            font-weight: 700; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            display: flex; align-items: center; gap: 5px;
        }}
        
        .news-title {{ 
            font-size: 1.4em; font-weight: 700; color: #333; 
            margin-bottom: 15px; line-height: 1.4; padding-right: 120px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .news-summary {{ 
            color: #666; margin-bottom: 20px; line-height: 1.7;
            font-size: 1em; display: -webkit-box; -webkit-line-clamp: 3; 
            -webkit-box-orient: vertical; overflow: hidden;
        }}
        
        .news-meta {{ 
            display: flex; justify-content: space-between; align-items: center;
            padding-top: 20px; border-top: 2px solid #f0f0f0; margin-top: 20px;
        }}
        
        .news-source {{ 
            font-weight: 700; color: #667eea; font-size: 1em;
            background: rgba(102, 126, 234, 0.1); padding: 6px 12px;
            border-radius: 15px;
        }}
        
        .news-time {{ 
            color: #999; font-size: 0.9em; font-weight: 500;
        }}
        
        .no-news {{ 
            text-align: center; color: #666; padding: 60px 20px; 
            font-size: 1.2em; background: rgba(255,255,255,0.9);
            border-radius: 20px; margin: 20px 0;
        }}
        
        .footer {{
            text-align: center; margin-top: 60px; padding: 40px;
            background: rgba(255,255,255,0.1); border-radius: 25px;
            backdrop-filter: blur(15px); color: rgba(255,255,255,0.9);
        }}
        
        .footer h3 {{ margin-bottom: 15px; font-size: 1.3em; }}
        .footer p {{ margin: 8px 0; font-size: 1em; }}
        .footer a {{ color: rgba(255,255,255,0.9); text-decoration: none; font-weight: 600; }}
        .footer a:hover {{ text-decoration: underline; }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .header {{ padding: 25px 20px; }}
            .header h1 {{ font-size: 2.2em; }}
            .stats {{ gap: 20px; }}
            .tabs {{ gap: 10px; padding: 15px; }}
            .tab {{ padding: 12px 18px; font-size: 1em; }}
            .news-grid {{ grid-template-columns: 1fr; gap: 20px; }}
            .news-card {{ padding: 20px; }}
            .news-title {{ padding-right: 80px; font-size: 1.2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">专注人工智能前沿资讯 · 每日精选 · 分类浏览</p>
            <div class="update-time">最后更新: {update_time}</div>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(articles)}</span>
                    <span class="stat-label">今日资讯</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(categorized_articles) - 1}</span>
                    <span class="stat-label">新闻分类</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">24/7</span>
                    <span class="stat-label">自动更新</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">AI</span>
                    <span class="stat-label">智能筛选</span>
                </div>
            </div>
        </div>
        
        <div class="tabs">'''
    
    # 生成标签
    for i, (category_name, articles_list) in enumerate(categorized_articles.items()):
        if category_name == "全部":
            icon = "📊"
            count = len(articles_list)
        else:
            category_config = categories.get(category_name, {})
            icon = category_config.get('icon', '📰')
            count = len(articles_list)
        
        active_class = ' active' if i == 0 else ''
        html += f'''            <div class="tab{active_class}" onclick="showCategory('{category_name}')">
                <span>{icon}</span>
                <span>{category_name}</span>
                <span>({count})</span>
            </div>
'''
    
    html += '        </div>\n'
    
    # 生成内容区域
    for i, (category_name, articles_list) in enumerate(categorized_articles.items()):
        active_class = ' active' if i == 0 else ''
        html += f'        <div id="category-{category_name}" class="tab-content{active_class}">\n'
        
        if articles_list:
            html += '            <div class="news-grid">\n'
            for article in articles_list:
                html += f'''                <div class="news-card" onclick="openDetail('{article.get('id', '')}')">
                    <div class="category-tag">
                        <span>{article.get('category_icon', '📰')}</span>
                        <span>{article.get('category', '未分类')}</span>
                    </div>
                    <h3 class="news-title">{article.get('title', '无标题')}</h3>
                    <p class="news-summary">{article.get('summary', '无摘要')}</p>
                    <div class="news-meta">
                        <span class="news-source">{article.get('source', '未知来源')}</span>
                        <span class="news-time">{article.get('time', '未知时间')}</span>
                    </div>
                </div>
'''
            html += '            </div>\n'
        else:
            html += '            <div class="no-news">该分类暂无新闻</div>\n'
        
        html += '        </div>\n'
    
    html += f'''        
        <div class="footer">
            <h3>🤖 AI科技日报</h3>
            <p>专注人工智能领域，为您提供最权威、最及时的AI资讯</p>
            <p>分类精选 · 每日更新 · 全球视野 · 专业可信</p>
            <p style="margin-top: 20px;">
                <a href="https://github.com/velist/ai-news-pusher" target="_blank">GitHub开源</a> · 
                <a href="mailto:contact@ai-daily.news">联系我们</a> · 
                <a href="#" onclick="alert('RSS功能开发中...')">RSS订阅</a>
            </p>
            <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                数据来源：GNews API | 更新频率：每2小时 | 响应式设计
            </p>
        </div>
    </div>
    
    <script>
        function showCategory(category) {{
            // 隐藏所有内容
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的内容
            document.getElementById('category-' + category).classList.add('active');
            event.target.closest('.tab').classList.add('active');
            
            // 滚动到顶部
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function openDetail(articleId) {{
            if (articleId) {{
                window.open('news/' + articleId + '.html', '_blank');
            }}
        }}
        
        // 页面加载动画
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.news-card');
            cards.forEach((card, index) => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                setTimeout(() => {{
                    card.style.transition = 'all 0.6s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }}, index * 100);
            }});
            
            // 统计信息动画
            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers.forEach((stat, index) => {{
                const finalText = stat.textContent;
                if (!isNaN(finalText)) {{
                    const finalNumber = parseInt(finalText);
                    let currentNumber = 0;
                    const increment = finalNumber / 30;
                    const timer = setInterval(() => {{
                        currentNumber += increment;
                        if (currentNumber >= finalNumber) {{
                            stat.textContent = finalNumber;
                            clearInterval(timer);
                        }} else {{
                            stat.textContent = Math.floor(currentNumber);
                        }}
                    }}, 50);
                }}
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

def generate_clean_detail_page(article):
    """生成简洁的详情页面"""
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article.get('title', '无标题')} - AI科技日报</title>
    <meta name="description" content="{article.get('summary', '无摘要')[:150]}...">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .back-btn {{ 
            background: rgba(255,255,255,0.9); color: #667eea; border: none;
            padding: 15px 30px; border-radius: 30px; text-decoration: none;
            display: inline-flex; align-items: center; gap: 10px; font-weight: 600;
            margin-bottom: 30px; transition: all 0.3s ease; font-size: 1.1em;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        .back-btn:hover {{ 
            background: #667eea; color: white; transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.3);
        }}
        .article {{ 
            background: rgba(255,255,255,0.95); border-radius: 25px; 
            padding: 50px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3);
        }}
        .article-title {{ 
            font-size: 2.5em; font-weight: 800; color: #2c3e50; 
            margin-bottom: 25px; line-height: 1.3;
        }}
        .article-meta {{ 
            display: flex; justify-content: space-between; align-items: center;
            padding: 25px 0; border-bottom: 3px solid #ecf0f1; margin-bottom: 35px;
            flex-wrap: wrap; gap: 15px;
        }}
        .meta-left {{ display: flex; align-items: center; gap: 15px; }}
        .article-source {{ 
            font-weight: 700; color: white; font-size: 1.2em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            padding: 10px 20px; border-radius: 25px;
        }}
        .article-time {{ color: #666; font-size: 1em; }}
        .article-category {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); color: white;
            padding: 10px 20px; border-radius: 25px; font-size: 1em; font-weight: 600;
            display: flex; align-items: center; gap: 8px;
        }}
        .article-content {{ 
            font-size: 1.2em; color: #2c3e50; line-height: 1.8; 
            margin-bottom: 35px; text-align: justify;
        }}
        .read-original {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); color: white;
            padding: 18px 40px; border-radius: 35px; text-decoration: none;
            display: inline-flex; align-items: center; gap: 12px; font-weight: 700;
            font-size: 1.2em; transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        .read-original:hover {{ 
            transform: translateY(-3px); 
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }}
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .article {{ padding: 30px 25px; }}
            .article-title {{ font-size: 2em; }}
            .article-meta {{ flex-direction: column; align-items: flex-start; }}
            .back-btn {{ padding: 12px 24px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-btn">
            <span>←</span>
            <span>返回首页</span>
        </a>
        
        <div class="article">
            <h1 class="article-title">{article.get('title', '无标题')}</h1>
            
            <div class="article-meta">
                <div class="meta-left">
                    <span class="article-source">{article.get('source', '未知来源')}</span>
                    <span class="article-time">{article.get('time', '未知时间')}</span>
                </div>
                <div class="article-category">
                    <span>{article.get('category_icon', '📰')}</span>
                    <span>{article.get('category', '未分类')}</span>
                </div>
            </div>
            
            <div class="article-content">
                <p>{article.get('summary', '暂无详细内容，请点击下方链接查看原文。')}</p>
            </div>
            
            <a href="{article.get('url', '#')}" target="_blank" class="read-original">
                <span>🔗</span>
                <span>阅读英文原文</span>
                <span>→</span>
            </a>
        </div>
    </div>
</body>
</html>'''
    return html

def main():
    """主函数 - 界面优化版"""
    print("🎨 界面优化版 - AI新闻推送系统")
    print("=" * 50)
    
    try:
        # 1. 加载环境变量
        load_env_file()
        
        # 2. 获取API密钥
        api_key = os.getenv('GNEWS_API_KEY')
        if not api_key:
            print("❌ 缺少GNEWS_API_KEY")
            return False
        
        # 3. 创建目录
        os.makedirs('docs', exist_ok=True)
        os.makedirs('docs/news', exist_ok=True)
        
        # 4. 获取分类新闻
        articles = fetch_categorized_news(api_key)
        
        if not articles:
            print("❌ 未获取到新闻")
            return False
        
        # 5. 生成用户友好的HTML页面（隐藏技术信息）
        print("🎨 生成用户友好的网页...")
        html_content = generate_clean_html(articles)
        
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 6. 生成详情页
        print("📄 生成详情页...")
        for article in articles:
            detail_html = generate_clean_detail_page(article)
            detail_path = f"docs/news/{article['id']}.html"
            with open(detail_path, 'w', encoding='utf-8') as f:
                f.write(detail_html)
        
        # 7. 保存数据
        news_data = {
            'last_updated': datetime.now().isoformat(),
            'total_count': len(articles),
            'categories': list(get_news_categories().keys()),
            'articles': articles
        }
        
        with open('docs/news_data.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 8. 最终报告
        print("\n" + "=" * 50)
        print("🎉 界面优化版生成完成！")
        print("=" * 50)
        print(f"📰 总新闻数: {len(articles)}")
        print(f"🏷️ 新闻分类: {len(get_news_categories())}")
        print(f"📁 详情页面: {len(articles)}")
        print(f"✨ 界面优化: 隐藏技术信息，分类浏览")
        print("🌐 GitHub Pages: https://velist.github.io/ai-news-pusher/docs/")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)