#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成H5每日新闻页面 - 个性化卡片展示
"""

import json
import urllib.request
import urllib.parse
import time
from datetime import datetime
import os

class HTMLNewsGenerator:
    def __init__(self):
        self.gnews_api_key = "c3cb6fef0f86251ada2b515017b97143"
        self.gnews_base_url = "https://gnews.io/api/v4"
        
    def translate_title(self, title):
        """翻译标题"""
        if not title:
            return title
            
        replacements = [
            ('OpenAI', 'OpenAI'), ('Google', '谷歌'), ('Microsoft', '微软'), 
            ('Apple', '苹果'), ('NVIDIA', '英伟达'), ('Artificial Intelligence', '人工智能'),
            ('AI', 'AI'), ('Machine Learning', '机器学习'), ('ChatGPT', 'ChatGPT'),
            ('GPT-4', 'GPT-4'), ('GPT-5', 'GPT-5'), ('Launches', '发布'),
            ('Releases', '发布'), ('Announces', '宣布'), ('Introduces', '推出'),
            ('Updates', '更新'), ('New', '全新'), ('Latest', '最新'),
            ('Advanced', '先进的'), ('Revolutionary', '革命性'), ('Breakthrough', '突破性'),
        ]
        
        chinese_title = title
        for english, chinese in replacements:
            chinese_title = chinese_title.replace(english, chinese)
            chinese_title = chinese_title.replace(english.lower(), chinese)
        
        # 添加emoji前缀
        if any(word in title.lower() for word in ['launch', 'release', 'announce']):
            chinese_title = f"🚀 {chinese_title}"
        elif any(word in title.lower() for word in ['breakthrough', 'innovation']):
            chinese_title = f"💡 {chinese_title}"
        elif any(word in title.lower() for word in ['update', 'improve']):
            chinese_title = f"🔄 {chinese_title}"
        else:
            chinese_title = f"📰 {chinese_title}"
        
        return chinese_title
    
    def get_news(self):
        """获取AI新闻"""
        try:
            params = {
                'apikey': self.gnews_api_key,
                'q': 'AI OR OpenAI OR "artificial intelligence"',
                'lang': 'en',
                'max': '8'
            }
            
            query_string = urllib.parse.urlencode(params)
            url = f"{self.gnews_base_url}/search?{query_string}"
            
            with urllib.request.urlopen(url, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            articles = result.get('articles', [])
            print(f"✅ 获取 {len(articles)} 条新闻")
            
            # 处理新闻数据
            processed_news = []
            for article in articles:
                processed_article = {
                    'title': self.translate_title(article.get('title', '')),
                    'original_title': article.get('title', ''),
                    'description': article.get('description', '')[:200] + "...",
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', '未知来源'),
                    'publishedAt': article.get('publishedAt', ''),
                    'image': article.get('image', ''),
                    'category': self.categorize_news(article.get('title', '')),
                    'importance': self.get_importance_score(article.get('title', ''))
                }
                processed_news.append(processed_article)
            
            return processed_news
            
        except Exception as e:
            print(f"❌ 获取新闻失败: {str(e)}")
            return []
    
    def categorize_news(self, title):
        """新闻分类"""
        title_lower = title.lower()
        if any(word in title_lower for word in ['openai', 'gpt', 'chatgpt']):
            return {'name': 'OpenAI动态', 'color': '#10B981', 'icon': '🤖'}
        elif any(word in title_lower for word in ['google', 'bard', 'gemini']):
            return {'name': '谷歌AI', 'color': '#3B82F6', 'icon': '🔍'}
        elif any(word in title_lower for word in ['microsoft', 'copilot']):
            return {'name': '微软AI', 'color': '#8B5CF6', 'icon': '💼'}
        elif any(word in title_lower for word in ['nvidia', 'chip']):
            return {'name': 'AI硬件', 'color': '#F59E0B', 'icon': '🔧'}
        elif any(word in title_lower for word in ['invest', 'fund', 'stock']):
            return {'name': '投资动态', 'color': '#EF4444', 'icon': '💰'}
        else:
            return {'name': 'AI资讯', 'color': '#6B7280', 'icon': '📱'}
    
    def get_importance_score(self, title):
        """重要性评分"""
        title_lower = title.lower()
        score = 1
        
        # 关键词加权
        if any(word in title_lower for word in ['breakthrough', 'revolutionary', 'major']):
            score += 3
        if any(word in title_lower for word in ['openai', 'gpt-5', 'gpt-4']):
            score += 2
        if any(word in title_lower for word in ['launch', 'release', 'announce']):
            score += 1
        
        return min(score, 5)
    
    def generate_html(self, news_data):
        """生成HTML页面"""
        today = datetime.now()
        
        # 按重要性排序
        news_data.sort(key=lambda x: x['importance'], reverse=True)
        
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI科技日报 - {today.strftime('%Y年%m月%d日')}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
        }}
        
        .stat-item {{
            background: rgba(255, 255, 255, 0.1);
            padding: 15px 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            text-align: center;
            color: white;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}
        
        .news-card {{
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            position: relative;
            animation: slideInUp 0.6s ease forwards;
            opacity: 0;
            transform: translateY(30px);
        }}
        
        .news-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.2);
        }}
        
        .news-card.priority-high {{
            border-left: 5px solid #EF4444;
        }}
        
        .news-card.priority-medium {{
            border-left: 5px solid #F59E0B;
        }}
        
        .news-card.priority-low {{
            border-left: 5px solid #10B981;
        }}
        
        .card-header {{
            padding: 20px;
            position: relative;
        }}
        
        .category-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 15px;
        }}
        
        .news-title {{
            font-size: 1.3rem;
            font-weight: 700;
            line-height: 1.4;
            margin-bottom: 12px;
            color: #1F2937;
        }}
        
        .news-description {{
            color: #6B7280;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .card-footer {{
            padding: 0 20px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .source {{
            font-size: 0.9rem;
            color: #9CA3AF;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .read-more {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .read-more:hover {{
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .importance-stars {{
            position: absolute;
            top: 15px;
            right: 15px;
            display: flex;
            gap: 2px;
        }}
        
        .star {{
            color: #FFD700;
            font-size: 0.8rem;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            color: white;
            opacity: 0.8;
        }}
        
        @keyframes slideInUp {{
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stats {{
                flex-wrap: wrap;
            }}
            
            .news-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            body {{
                padding: 15px;
            }}
        }}
        
        .update-time {{
            background: rgba(255, 255, 255, 0.1);
            padding: 10px 20px;
            border-radius: 25px;
            backdrop-filter: blur(10px);
            color: white;
            font-size: 0.9rem;
            margin: 20px auto;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">{today.strftime('%Y年%m月%d日')} · 人工智能前沿资讯</p>
            <div class="update-time">
                <i class="fas fa-clock"></i> 更新时间：{today.strftime('%H:%M')}
            </div>
        </header>
        
        <div class="stats">
            <div class="stat-item">
                <span class="stat-number">{len(news_data)}</span>
                <span class="stat-label">今日新闻</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{len([n for n in news_data if n['importance'] >= 4])}</span>
                <span class="stat-label">重要资讯</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(set([n['category']['name'] for n in news_data]))}</span>
                <span class="stat-label">覆盖领域</span>
            </div>
        </div>
        
        <div class="news-grid">"""
        
        # 添加新闻卡片
        for i, news in enumerate(news_data):
            priority_class = 'priority-high' if news['importance'] >= 4 else 'priority-medium' if news['importance'] >= 3 else 'priority-low'
            
            stars = ''.join(['<i class="fas fa-star star"></i>' for _ in range(news['importance'])])
            
            card_html = f"""
            <article class="news-card {priority_class}" style="animation-delay: {i * 0.1}s;">
                <div class="importance-stars">
                    {stars}
                </div>
                <div class="card-header">
                    <div class="category-badge" style="background-color: {news['category']['color']};">
                        <span>{news['category']['icon']}</span>
                        <span>{news['category']['name']}</span>
                    </div>
                    <h2 class="news-title">{news['title']}</h2>
                    <p class="news-description">{news['description']}</p>
                </div>
                <div class="card-footer">
                    <div class="source">
                        <i class="fas fa-newspaper"></i>
                        <span>{news['source']}</span>
                    </div>
                    <a href="{news['url']}" target="_blank" class="read-more">
                        阅读原文 <i class="fas fa-external-link-alt"></i>
                    </a>
                </div>
            </article>"""
            
            html_template += card_html
        
        html_template += f"""
        </div>
        
        <footer class="footer">
            <p>🚀 由AI驱动的智能新闻聚合 · 每日8:00自动更新</p>
            <p style="margin-top: 10px; font-size: 0.8rem;">
                数据来源：GNews API · 生成时间：{today.strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </footer>
    </div>
    
    <script>
        // 添加交互动画
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.news-card');
            
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.style.opacity = '1';
                        entry.target.style.transform = 'translateY(0)';
                    }}
                }});
            }}, {{ threshold: 0.1 }});
            
            cards.forEach(card => observer.observe(card));
            
            // 点击卡片动画
            cards.forEach(card => {{
                card.addEventListener('click', function(e) {{
                    if (e.target.tagName !== 'A') {{
                        this.style.transform = 'scale(0.95)';
                        setTimeout(() => {{
                            this.style.transform = 'scale(1)';
                        }}, 150);
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>"""
        
        return html_template
    
    def create_daily_page(self):
        """创建每日新闻页面"""
        print("🎨 生成H5每日新闻页面...")
        
        # 获取新闻数据
        news_data = self.get_news()
        if not news_data:
            print("❌ 无法获取新闻数据")
            return False
        
        # 生成HTML
        html_content = self.generate_html(news_data)
        
        # 创建目录
        os.makedirs('docs', exist_ok=True)
        
        # 写入文件
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 创建GitHub Pages配置
        with open('docs/_config.yml', 'w', encoding='utf-8') as f:
            f.write('# GitHub Pages配置\\ntheme: jekyll-theme-minimal\\n')
        
        print(f"✅ HTML页面生成完成")
        print(f"📁 文件位置: docs/index.html")
        print(f"🔗 本地预览: file://{os.path.abspath('docs/index.html')}")
        
        return True

def main():
    generator = HTMLNewsGenerator()
    
    if generator.create_daily_page():
        print("\\n🎉 H5新闻页面生成成功！")
        print("\\n📋 接下来的步骤:")
        print("   1. 推送到GitHub")
        print("   2. 启用GitHub Pages")
        print("   3. 访问: https://你的用户名.github.io/ai-news-pusher")
        print("\\n💡 特色功能:")
        print("   ✨ 响应式设计 - 手机电脑完美适配")
        print("   🎨 动画效果 - 卡片滑入和悬停动画") 
        print("   📊 智能分类 - 按公司和重要性分类")
        print("   ⭐ 重要性评级 - 星级评分系统")

if __name__ == "__main__":
    main()