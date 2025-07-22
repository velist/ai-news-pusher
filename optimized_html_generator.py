#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的H5新闻页面生成器 - 苹果设计风格
采用苹果Human Interface Guidelines设计规范
"""

import json
import os
from datetime import datetime


class AppleStyleNewsGenerator:
    def __init__(self):
        self.today = datetime.now()
    
    def categorize_news(self, title):
        """新闻分类"""
        title_lower = title.lower()
        if any(word in title_lower for word in ['openai', 'gpt', 'chatgpt']):
            return {'name': 'OpenAI动态', 'color': '#34C759', 'icon': '🤖'}
        elif any(word in title_lower for word in ['google', 'bard', 'gemini']):
            return {'name': '谷歌AI', 'color': '#007AFF', 'icon': '🔍'}
        elif any(word in title_lower for word in ['microsoft', 'copilot']):
            return {'name': '微软AI', 'color': '#5856D6', 'icon': '💼'}
        elif any(word in title_lower for word in ['nvidia', 'chip']):
            return {'name': 'AI硬件', 'color': '#FF9500', 'icon': '🔧'}
        elif any(word in title_lower for word in ['invest', 'fund', 'stock']):
            return {'name': '投资动态', 'color': '#FF3B30', 'icon': '💰'}
        else:
            return {'name': 'AI资讯', 'color': '#8E8E93', 'icon': '📱'}
    
    def get_importance_score(self, title):
        """重要性评分"""
        title_lower = title.lower()
        score = 1
        
        if any(word in title_lower for word in ['breakthrough', 'revolutionary', 'major']):
            score += 3
        if any(word in title_lower for word in ['openai', 'gpt-5', 'gpt-4']):
            score += 2
        if any(word in title_lower for word in ['launch', 'release', 'announce']):
            score += 1
        
        return min(score, 5)
    
    def translate_title(self, title):
        """简化的中文翻译"""
        replacements = [
            ('OpenAI', 'OpenAI'), ('Google', '谷歌'), ('Microsoft', '微软'),
            ('Apple', '苹果'), ('NVIDIA', '英伟达'), ('Artificial Intelligence', '人工智能'),
            ('AI', 'AI'), ('Machine Learning', '机器学习'), ('Deep Learning', '深度学习'),
            ('ChatGPT', 'ChatGPT'), ('GPT', 'GPT'), ('Bard', 'Bard'),
            ('breakthrough', '突破'), ('launch', '发布'), ('release', '发布'),
            ('announce', '宣布'), ('investment', '投资'), ('funding', '融资')
        ]
        
        chinese_title = title
        for en, zh in replacements:
            chinese_title = chinese_title.replace(en, zh)
        
        # 添加前缀标识
        title_lower = title.lower()
        if any(word in title_lower for word in ['breakthrough', 'revolutionary']):
            chinese_title = f"🚀 重大突破：{chinese_title}"
        elif any(word in title_lower for word in ['launch', 'release']):
            chinese_title = f"🔄 重大更新：{chinese_title}"
        else:
            chinese_title = f"📰 AI资讯：{chinese_title}"
        
        return chinese_title
    
    def generate_optimized_html(self, articles):
        """生成优化的HTML页面"""
        try:
            print("🎨 开始生成Apple风格H5新闻页面...")
            
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
            
            # 按重要性排序
            processed_news.sort(key=lambda x: x['importance'], reverse=True)
            
            # 生成HTML内容
            html_content = self.create_apple_style_template(processed_news)
            
            # 创建目录
            os.makedirs('docs', exist_ok=True)
            
            # 写入文件
            with open('docs/index.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print("✅ Apple风格H5新闻页面生成完成: docs/index.html")
            return True
            
        except Exception as e:
            print(f"❌ H5页面生成失败: {str(e)}")
            return False
    
    def create_apple_style_template(self, news_data):
        """创建Apple风格HTML模板"""
        
        # 按分类整理新闻
        categories = {}
        all_news = []
        
        for article in news_data:
            category = article['category']
            if category['name'] not in categories:
                categories[category['name']] = []
            categories[category['name']].append(article)
            all_news.append(article)
        
        # 生成分类选项
        category_tabs = ""
        for i, (cat_name, articles) in enumerate(categories.items()):
            active_class = "active" if i == 0 else ""
            category_tabs += f'''
            <button class="tab-button {active_class}" data-category="{cat_name}">
                <span class="tab-icon">{articles[0]['category']['icon']}</span>
                <span class="tab-text">{cat_name}</span>
                <span class="tab-count">{len(articles)}</span>
            </button>'''
        
        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>AI科技日报 - {self.today.strftime('%Y年%m月%d日')}</title>
    <link href="https://fonts.googleapis.com/css2?family=-apple-system,BlinkMacSystemFont,SF+Pro+Display:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            /* 苹果设计系统颜色 - 浅色模式 */
            --color-primary: #007AFF;
            --color-secondary: #5856D6;
            --color-success: #34C759;
            --color-warning: #FF9500;
            --color-error: #FF3B30;
            --color-gray: #8E8E93;
            --color-gray2: #AEAEB2;
            --color-gray3: #C7C7CC;
            --color-gray4: #D1D1D6;
            --color-gray5: #E5E5EA;
            --color-gray6: #F2F2F7;
            
            /* 背景色 */
            --bg-primary: #FFFFFF;
            --bg-secondary: #F2F2F7;
            --bg-tertiary: #FFFFFF;
            --bg-grouped: #F2F2F7;
            
            /* 文字颜色 */
            --text-primary: #000000;
            --text-secondary: #3C3C43;
            --text-tertiary: #3C3C4399;
            --text-quaternary: #3C3C4326;
            
            /* 阴影 */
            --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.1);
            --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.15);
            --shadow-large: 0 8px 25px rgba(0, 0, 0, 0.15);
            
            /* 圆角 */
            --radius-small: 8px;
            --radius-medium: 12px;
            --radius-large: 16px;
            --radius-xl: 20px;
            
            /* 间距 */
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
        }}
        
        @media (prefers-color-scheme: dark) {{
            :root {{
                --color-primary: #0A84FF;
                --color-secondary: #5E5CE6;
                --color-success: #32D74B;
                --color-warning: #FF9F0A;
                --color-error: #FF453A;
                --color-gray: #8E8E93;
                --color-gray2: #636366;
                --color-gray3: #48484A;
                --color-gray4: #3A3A3C;
                --color-gray5: #2C2C2E;
                --color-gray6: #1C1C1E;
                
                --bg-primary: #000000;
                --bg-secondary: #1C1C1E;
                --bg-tertiary: #2C2C2E;
                --bg-grouped: #000000;
                
                --text-primary: #FFFFFF;
                --text-secondary: #EBEBF5;
                --text-tertiary: #EBEBF599;
                --text-quaternary: #EBEBF526;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: var(--bg-grouped);
            color: var(--text-primary);
            line-height: 1.47;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}
        
        /* 容器布局 */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 var(--spacing-md);
        }}
        
        /* 头部区域 */
        .header {{
            background-color: var(--bg-primary);
            padding: var(--spacing-lg) 0;
            text-align: center;
            border-bottom: 0.5px solid var(--color-gray5);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: var(--spacing-sm);
        }}
        
        .header .subtitle {{
            font-size: 1rem;
            color: var(--text-secondary);
            font-weight: 400;
        }}
        
        .update-time {{
            margin-top: var(--spacing-md);
            padding: var(--spacing-sm) var(--spacing-md);
            background-color: var(--bg-secondary);
            border-radius: var(--radius-large);
            display: inline-block;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
        
        /* 统计面板 */
        .stats {{
            display: flex;
            justify-content: center;
            gap: var(--spacing-md);
            padding: var(--spacing-lg) 0;
            margin-bottom: var(--spacing-md);
        }}
        
        .stat-item {{
            background-color: var(--bg-tertiary);
            padding: var(--spacing-md) var(--spacing-lg);
            border-radius: var(--radius-medium);
            text-align: center;
            min-width: 80px;
            box-shadow: var(--shadow-light);
        }}
        
        .stat-number {{
            font-size: 1.5rem;
            font-weight: 600;
            color: var(--color-primary);
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: var(--spacing-xs);
            font-weight: 500;
        }}
        
        /* 分类标签栏 */
        .tab-container {{
            background-color: var(--bg-primary);
            padding: var(--spacing-md) 0;
            border-bottom: 0.5px solid var(--color-gray5);
            position: sticky;
            top: 100px;
            z-index: 90;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        
        .tabs {{
            display: flex;
            gap: var(--spacing-sm);
            overflow-x: auto;
            padding: 0 var(--spacing-md);
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }}
        
        .tabs::-webkit-scrollbar {{
            display: none;
        }}
        
        .tab-button {{
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            padding: var(--spacing-sm) var(--spacing-md);
            background-color: var(--bg-secondary);
            border: none;
            border-radius: var(--radius-large);
            font-size: 0.875rem;
            color: var(--text-secondary);
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
            min-height: 36px;
        }}
        
        .tab-button.active {{
            background-color: var(--color-primary);
            color: white;
            font-weight: 600;
        }}
        
        .tab-button:hover {{
            background-color: var(--color-gray5);
        }}
        
        .tab-button.active:hover {{
            background-color: var(--color-primary);
        }}
        
        .tab-icon {{
            font-size: 1rem;
        }}
        
        .tab-count {{
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 0.75rem;
            font-weight: 600;
            min-width: 20px;
            text-align: center;
        }}
        
        .tab-button.active .tab-count {{
            background-color: rgba(255, 255, 255, 0.3);
        }}
        
        /* 新闻网格 */
        .content-area {{
            padding: var(--spacing-lg) 0;
        }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: var(--spacing-md);
        }}
        
        .news-card {{
            background-color: var(--bg-tertiary);
            border-radius: var(--radius-large);
            overflow: hidden;
            box-shadow: var(--shadow-light);
            transition: all 0.3s ease;
            border: 0.5px solid var(--color-gray5);
            position: relative;
        }}
        
        .news-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }}
        
        .news-card:active {{
            transform: translateY(0px);
            transition: all 0.1s ease;
        }}
        
        .card-header {{
            padding: var(--spacing-md);
        }}
        
        .category-badge {{
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-xs);
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--radius-small);
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: var(--spacing-sm);
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
        
        .source {{
            font-size: 0.8125rem;
            color: var(--text-tertiary);
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
        }}
        
        .read-more {{
            background-color: var(--color-primary);
            color: white;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--radius-medium);
            text-decoration: none;
            font-size: 0.8125rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        
        .read-more:hover {{
            background-color: var(--color-secondary);
            transform: scale(1.02);
        }}
        
        .read-more:active {{
            transform: scale(0.98);
        }}
        
        .importance-stars {{
            position: absolute;
            top: var(--spacing-md);
            right: var(--spacing-md);
            display: flex;
            gap: 2px;
        }}
        
        .star {{
            color: var(--color-warning);
            font-size: 0.75rem;
        }}
        
        /* 优先级指示器 */
        .priority-indicator {{
            width: 3px;
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
            border-top-left-radius: var(--radius-large);
            border-bottom-left-radius: var(--radius-large);
        }}
        
        .news-card.priority-high .priority-indicator {{
            background-color: var(--color-error);
        }}
        
        .news-card.priority-medium .priority-indicator {{
            background-color: var(--color-warning);
        }}
        
        .news-card.priority-low .priority-indicator {{
            background-color: var(--color-success);
        }}
        
        /* 底部 */
        .footer {{
            text-align: center;
            padding: var(--spacing-xl) 0;
            color: var(--text-tertiary);
            border-top: 0.5px solid var(--color-gray5);
            margin-top: var(--spacing-xl);
        }}
        
        .footer p {{
            font-size: 0.8125rem;
            margin-bottom: var(--spacing-xs);
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .container {{
                padding: 0 var(--spacing-md);
            }}
            
            .header {{
                padding: var(--spacing-md) 0;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stats {{
                gap: var(--spacing-sm);
                padding: var(--spacing-md) 0;
            }}
            
            .stat-item {{
                padding: var(--spacing-sm) var(--spacing-md);
                min-width: 70px;
            }}
            
            .stat-number {{
                font-size: 1.25rem;
            }}
            
            .tab-container {{
                top: 80px;
            }}
            
            .news-grid {{
                grid-template-columns: 1fr;
                gap: var(--spacing-md);
            }}
            
            .news-card {{
                margin: 0;
            }}
        }}
        
        @media (max-width: 480px) {{
            .container {{
                padding: 0 var(--spacing-sm);
            }}
            
            .header {{
                padding: var(--spacing-sm) 0;
            }}
            
            .header h1 {{
                font-size: 1.75rem;
            }}
            
            .stats {{
                flex-wrap: wrap;
                justify-content: center;
            }}
            
            .tabs {{
                padding: 0 var(--spacing-sm);
            }}
            
            .news-grid {{
                gap: var(--spacing-sm);
            }}
            
            .card-header, .card-footer {{
                padding: var(--spacing-sm);
            }}
            
            .card-footer {{
                padding-top: 0;
            }}
        }}
        
        /* 隐藏类 */
        .hidden {{
            display: none !important;
        }}
        
        /* 动画 */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .news-card {{
            animation: fadeInUp 0.6s ease forwards;
        }}
    </style>
</head>
<body>
    <!-- 头部 -->
    <header class="header">
        <div class="container">
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">{self.today.strftime('%Y年%m月%d日')} · 人工智能前沿资讯</p>
            <div class="update-time">
                <span>⏱ 更新时间：{self.today.strftime('%H:%M')}</span>
            </div>
        </div>
    </header>
    
    <!-- 统计面板 -->
    <div class="container">
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
                <span class="stat-number">{len(categories)}</span>
                <span class="stat-label">覆盖领域</span>
            </div>
        </div>
    </div>
    
    <!-- 分类标签栏 -->
    <div class="tab-container">
        <div class="container">
            <div class="tabs">
                <button class="tab-button active" data-category="all">
                    <span class="tab-icon">📱</span>
                    <span class="tab-text">全部</span>
                    <span class="tab-count">{len(all_news)}</span>
                </button>
                {category_tabs}
            </div>
        </div>
    </div>
    
    <!-- 内容区域 -->
    <div class="container">
        <div class="content-area">
            <div class="news-grid">'''
        
        # 添加新闻卡片
        for i, news in enumerate(all_news):
            priority_class = 'priority-high' if news['importance'] >= 4 else 'priority-medium' if news['importance'] >= 3 else 'priority-low'
            
            stars = ''.join(['<span class="star">★</span>' for _ in range(news['importance'])])
            
            # 设置分类颜色
            category_colors = {
                'OpenAI动态': 'background-color: var(--color-success); color: white;',
                '谷歌AI': 'background-color: var(--color-primary); color: white;',  
                '微软AI': 'background-color: var(--color-secondary); color: white;',
                'AI硬件': 'background-color: var(--color-warning); color: white;',
                '投资动态': 'background-color: var(--color-error); color: white;',
                'AI资讯': 'background-color: var(--color-gray); color: white;'
            }
            
            category_style = category_colors.get(news['category']['name'], 'background-color: var(--color-gray); color: white;')
            
            card_html = f'''
            <article class="news-card {priority_class}" data-category="{news['category']['name']}" style="animation-delay: {i * 0.05}s;">
                <div class="priority-indicator"></div>
                <div class="importance-stars">
                    {stars}
                </div>
                <div class="card-header">
                    <div class="category-badge" style="{category_style}">
                        <span>{news['category']['icon']}</span>
                        <span>{news['category']['name']}</span>
                    </div>
                    <h2 class="news-title">{news['title']}</h2>
                    <p class="news-description">{news['description']}</p>
                </div>
                <div class="card-footer">
                    <div class="source">
                        <span>📰</span>
                        <span>{news['source']}</span>
                    </div>
                    <a href="{news['url']}" target="_blank" class="read-more">
                        阅读原文
                    </a>
                </div>
            </article>'''
            
            html_template += card_html
        
        html_template += f'''
            </div>
        </div>
    </div>
    
    <!-- 底部 -->
    <footer class="footer">
        <div class="container">
            <p>🚀 由AI驱动的智能新闻聚合 · 每日8:00自动更新</p>
            <p>数据来源：GNews API · 生成时间：{self.today.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </footer>
    
    <script>
        // 分类筛选功能
        document.addEventListener('DOMContentLoaded', function() {{
            const tabButtons = document.querySelectorAll('.tab-button');
            const newsCards = document.querySelectorAll('.news-card');
            
            // 分类筛选
            tabButtons.forEach(button => {{
                button.addEventListener('click', function() {{
                    const category = this.dataset.category;
                    
                    // 更新活跃标签
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    // 筛选新闻卡片
                    newsCards.forEach((card, index) => {{
                        if (category === 'all' || card.dataset.category === category) {{
                            card.classList.remove('hidden');
                            card.style.animationDelay = (index * 0.05) + 's';
                        }} else {{
                            card.classList.add('hidden');
                        }}
                    }});
                }});
            }});
            
            // 卡片交互动画
            newsCards.forEach(card => {{
                card.addEventListener('click', function(e) {{
                    if (e.target.tagName !== 'A') {{
                        this.style.transform = 'translateY(0px) scale(0.98)';
                        setTimeout(() => {{
                            this.style.transform = '';
                        }}, 150);
                    }}
                }});
            }});
            
            // 平滑滚动
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                anchor.addEventListener('click', function (e) {{
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {{
                        target.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'start'
                        }});
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>'''
        
        return html_template


if __name__ == "__main__":
    # 测试用例
    test_articles = [
        {
            'title': 'OpenAI Announces GPT-5 Revolutionary Breakthrough',
            'description': 'OpenAI reveals the next generation of AI with unprecedented capabilities in reasoning and multimodal understanding.',
            'url': 'https://example.com/news1',
            'source': {'name': 'TechCrunch'},
            'publishedAt': '2024-01-20T08:00:00Z',
            'image': ''
        },
        {
            'title': 'Google Bard Gets Major Update with New Features', 
            'description': 'Google enhances Bard with improved conversational abilities and integration with more services.',
            'url': 'https://example.com/news2',
            'source': {'name': 'The Verge'},
            'publishedAt': '2024-01-20T07:30:00Z',
            'image': ''
        }
    ]
    
    generator = AppleStyleNewsGenerator()
    success = generator.generate_optimized_html(test_articles)
    
    if success:
        print("🎉 Apple风格页面生成测试完成！")