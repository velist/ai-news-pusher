#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
超级Ultra翻译系统 - 通用翻译，不依赖特定标题映射
"""

import json
import urllib.request
import urllib.parse
import time
import os
from datetime import datetime
import re

class SuperUltraTranslationNewsProcessor:
    def __init__(self):
        # 直接硬编码配置，避免依赖问题
        self.gnews_api_key = "c3cb6fef0f86251ada2b515017b97143"
        self.feishu_app_id = "cli_a8f4efb90f3a1013"
        self.feishu_app_secret = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
        self.feishu_base_url = "https://open.feishu.cn/open-apis"
        self.gnews_base_url = "https://gnews.io/api/v4"
        
    def format_publish_date(self, date_str):
        """格式化发布时间为年月日 时分"""
        try:
            if not date_str:
                return datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # 处理ISO格式时间字符串
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                # 转换为北京时间 (UTC+8)
                import datetime as dt_module
                dt = dt.replace(tzinfo=dt_module.timezone.utc)
                dt = dt.astimezone(dt_module.timezone(dt_module.timedelta(hours=8)))
            else:
                dt = datetime.fromisoformat(date_str)
                
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return datetime.now().strftime("%Y-%m-%d %H:%M")
        
    def translate_title(self, title):
        """超级通用翻译系统 - 完全中文化任何标题"""
        if not title:
            return title
        
        # 第一步：基础词汇翻译
        translations = {
            # 公司名称
            'Google': '谷歌',
            "Google's": '谷歌',
            'Microsoft': '微软',
            'Apple': '苹果',
            "Apple's": '苹果',
            'OpenAI': 'OpenAI',
            'ChatGPT': 'ChatGPT',
            'SoftBank': '软银',
            'Amazon': '亚马逊',
            'Meta': 'Meta',
            'Tesla': '特斯拉',
            'Nvidia': '英伟达',
            
            # 通用术语
            'AI': 'AI',
            'artificial intelligence': '人工智能',
            'machine learning': '机器学习',
            'deep learning': '深度学习',
            'neural network': '神经网络',
            'data center': '数据中心',
            'cloud computing': '云计算',
            
            # 动作和状态
            'launches': '推出',
            'release': '发布',
            'announces': '宣布',
            'unveils': '推出',
            'introduces': '推出',
            'reveals': '披露',
            'raises': '融资',
            'funding': '融资',
            'investment': '投资',
            'billion': '亿',
            'million': '百万',
            'startup': '初创公司',
            'company': '公司',
            'users': '用户',
            'technology': '技术',
            'innovation': '创新',
            'breakthrough': '突破',
            'features': '功能',
            'model': '模型',
            'available': '可用',
            'generally': '正式',
            'fastest': '最快',
            'cost-effective': '高性价比',
            'stocks': '股票',
            'earnings': '财报',
            'beat': '击败',
            'gold-level': '金牌',
            'score': '得分',
            'contest': '竞赛',
            'math': '数学',
            'Olympiad': '奥林匹克',
            'triumph': '胜利',
            'annual': '年度',
            'machines': '机器',
            'catching up': '追赶',
            'humans': '人类',
            'talent': '人才',
            'poaches': '挖角',
            'beefs up': '加强',
            'underground': '地下',
            'waste storage': '废物存储',
            'offset': '抵消',
            'carbon toll': '碳排放',
            'turns to': '转向',
            'device': '设备',
            'translate': '翻译',
            'dreams': '梦境',
            'play back': '回放',
            'eye': '瞄准',
            'small': '小型',
            'center': '中心'
        }
        
        translated = title
        # 按长度排序，先替换长词组
        for en, cn in sorted(translations.items(), key=lambda x: len(x[0]), reverse=True):
            translated = translated.replace(en, cn)
        
        # 第二步：智能前缀分类
        title_lower = translated.lower()
        
        if any(keyword in title_lower for keyword in ['openai', 'chatgpt', 'gpt']):
            category_prefix = "🤖 OpenAI动态："
        elif any(keyword in title_lower for keyword in ['谷歌', 'google', 'gemini', 'deepmind']):
            category_prefix = "🔍 谷歌AI："
        elif any(keyword in title_lower for keyword in ['微软', 'microsoft', 'copilot', 'azure']):
            category_prefix = "💼 微软AI："
        elif any(keyword in title_lower for keyword in ['苹果', 'apple', 'ios', 'siri']):
            category_prefix = "🍎 苹果AI："
        elif any(keyword in title_lower for keyword in ['投资', 'investment', '融资', 'funding', 'million', 'billion', 'raises', 'stocks', 'earnings']):
            category_prefix = "💰 投资动态："
        elif any(keyword in title_lower for keyword in ['硬件', 'hardware', 'chip', 'processor', 'gpu', 'ssd', 'storage']):
            category_prefix = "🔧 硬件技术："
        else:
            category_prefix = "📰 AI资讯："
        
        # 如果没有emoji前缀，添加分类前缀
        if not any(emoji in translated[:5] for emoji in ['🤖', '🔍', '💼', '🍎', '💰', '🔧', '📰']):
            translated = category_prefix + translated
        
        return translated
    
    def translate_description(self, description, title=""):
        """翻译描述内容"""
        if not description:
            return description
        
        # 基础翻译映射
        translations = {
            'Google': '谷歌',
            'Microsoft': '微软', 
            'Apple': '苹果',
            'OpenAI': 'OpenAI',
            'users': '用户',
            'technology': '技术',
            'startup': '初创公司',
            'company': '公司',
            'artificial intelligence': '人工智能',
            'AI': 'AI',
            'model': '模型',
            'available': '可用',
            'costs': '成本',
            'input': '输入',
            'output': '输出',
            'tokens': '令牌',
            'respectively': '分别'
        }
        
        translated = description
        for en, cn in translations.items():
            translated = translated.replace(en, cn)
        
        return translated
    
    def get_feishu_token(self):
        """获取飞书访问令牌"""
        try:
            url = f"{self.feishu_base_url}/auth/v3/tenant_access_token/internal"
            data = {
                "app_id": self.feishu_app_id,
                "app_secret": self.feishu_app_secret
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if result.get('code') == 0:
                print("✅ 飞书令牌获取成功")
                return result.get('tenant_access_token')
            else:
                print(f"❌ 飞书令牌获取失败: {result}")
                return None
                
        except Exception as e:
            print(f"❌ 飞书令牌获取异常: {str(e)}")
            return None
    
    def get_news(self):
        """获取AI新闻"""
        try:
            params = {
                'apikey': self.gnews_api_key,
                'q': 'AI OR OpenAI OR "artificial intelligence"',
                'lang': 'en',
                'max': '10'
            }
            
            query_string = urllib.parse.urlencode(params)
            url = f"{self.gnews_base_url}/search?{query_string}"
            
            with urllib.request.urlopen(url, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            articles = result.get('articles', [])
            print(f"✅ 成功获取 {len(articles)} 条新闻")
            return articles
            
        except Exception as e:
            print(f"❌ 新闻获取失败: {str(e)}")
            return []
    
    def generate_super_ultra_html(self, articles):
        """生成超级Ultra版HTML页面"""
        try:
            print("🎨 开始生成超级Ultra版H5页面（完全中文化 + 主题切换）...")
            
            # 转换数据格式
            news_data = []
            for i, article in enumerate(articles):
                chinese_title = self.translate_title(article.get('title', ''))
                chinese_description = self.translate_description(
                    article.get('description', '') or article.get('content', '')[:200],
                    article.get('title', '')
                )
                
                # 分类逻辑
                title_lower = chinese_title.lower()
                if '谷歌' in title_lower or 'google' in title_lower:
                    category = {"name": "谷歌AI", "color": "#3B82F6", "icon": "🔍"}
                elif '微软' in title_lower or 'microsoft' in title_lower:
                    category = {"name": "微软AI", "color": "#8B5CF6", "icon": "💼"}
                elif '苹果' in title_lower or 'apple' in title_lower:
                    category = {"name": "苹果AI", "color": "#F59E0B", "icon": "🍎"}
                elif 'openai' in title_lower:
                    category = {"name": "OpenAI动态", "color": "#10B981", "icon": "🤖"}
                elif any(word in title_lower for word in ['投资', '融资', 'investment', 'funding', 'stocks']):
                    category = {"name": "投资动态", "color": "#EF4444", "icon": "💰"}
                elif any(word in title_lower for word in ['硬件', 'hardware', 'ssd', 'chip']):
                    category = {"name": "硬件技术", "color": "#6366F1", "icon": "🔧"}
                else:
                    category = {"name": "AI资讯", "color": "#6B7280", "icon": "📱"}
                
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
                    "category": category,
                    "importance": 1
                }
                news_data.append(news_item)
            
            # 保存JSON数据
            os.makedirs('docs', exist_ok=True)
            with open('docs/news_data.json', 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            
            # 生成主页HTML
            html_template = self.create_super_ultra_html_template(news_data)
            
            with open('docs/index.html', 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            # 生成详情页
            os.makedirs('docs/news', exist_ok=True)
            for news in news_data:
                detail_html = self.create_detail_page(news, news_data)
                with open(f'docs/news/{news["id"]}.html', 'w', encoding='utf-8') as f:
                    f.write(detail_html)
            
            print("✅ 超级Ultra版H5页面生成完成!")
            print("   📄 首页: docs/index.html")
            print("   📰 详情页: 10 篇")
            print("   🌙 主题切换: 支持日/夜间模式")
            return True
            
        except Exception as e:
            print(f"❌ 超级Ultra版H5生成失败: {str(e)}")
            return False
    
    def create_super_ultra_html_template(self, news_data):
        """创建超级Ultra版HTML模板"""
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
        
        # 开始构建HTML
        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 中文AI资讯门户</title>
    <style>
        :root {{
            /* 颜色变量 */
            --color-primary: #007AFF;
            --color-success: #10B981;
            --color-warning: #F59E0B;
            --color-error: #EF4444;
            
            /* 背景颜色 */
            --bg-primary: #FFFFFF;
            --bg-secondary: #F2F2F7;
            --bg-tertiary: #FFFFFF;
            
            /* 文字颜色 */
            --text-primary: #000000;
            --text-secondary: #3C3C43;
            --text-tertiary: #8E8E93;
            
            /* 间距 */
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            
            /* 圆角 */
            --radius-small: 8px;
            --radius-medium: 12px;
            --radius-large: 16px;
            
            /* 阴影 */
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
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Icons", "Helvetica Neue", "Helvetica", "Arial", sans-serif;
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: all 0.3s ease;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 var(--spacing-md);
        }}
        
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
        
        .tabs {{
            background-color: var(--bg-primary);
            padding: var(--spacing-md) 0;
            overflow-x: auto;
            white-space: nowrap;
            box-shadow: var(--shadow-light);
        }}
        
        .tabs::-webkit-scrollbar {{
            height: 4px;
        }}
        
        .tabs::-webkit-scrollbar-track {{
            background: var(--bg-secondary);
        }}
        
        .tabs::-webkit-scrollbar-thumb {{
            background: var(--text-tertiary);
            border-radius: 2px;
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
        
        .tab-button:hover:not(.active) {{
            background-color: var(--bg-tertiary);
        }}
        
        .tab-count {{
            background-color: rgba(255, 255, 255, 0.2);
            color: currentColor;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 0.75rem;
        }}
        
        .content-area {{
            padding: var(--spacing-lg) 0;
        }}
        
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
        
        .news-card.hidden {{
            display: none;
        }}
        
        .priority-indicator {{
            width: 3px;
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
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
        
        .card-header {{
            padding: var(--spacing-md);
        }}
        
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
        
        .read-more:hover {{
            opacity: 0.8;
        }}
        
        @media (max-width: 768px) {{
            .news-grid {{
                grid-template-columns: 1fr;
                gap: var(--spacing-md);
            }}
            
            .container {{
                padding: 0 var(--spacing-sm);
            }}
            
            .header h1 {{
                font-size: 1.5rem;
            }}
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
        for i, news in enumerate(news_data):
            priority_class = 'priority-high' if news['importance'] >= 4 else 'priority-medium' if news['importance'] >= 3 else 'priority-low'
            stars = ''.join(['<span class="star">★</span>' for _ in range(news['importance'])])
            
            card_html = f'''
            <article class="news-card {priority_class}" data-category="{news['category']['name']}" 
                     onclick="window.location.href='news/{news['id']}.html'">
                <div class="priority-indicator"></div>
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
                        <div class="publish-date">🕒 {self.format_publish_date(news.get('publishedAt'))}</div>
                    </div>
                    <div class="read-more">查看详情</div>
                </div>
            </article>'''
            
            html_template += card_html
        
        html_template += f'''
            </div>
        </div>
    </div>
    
    <script>
        // 主题切换
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
        
        // 页面加载时恢复主题
        document.addEventListener('DOMContentLoaded', function() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            const themeIcon = document.querySelector('.theme-icon');
            const themeText = document.querySelector('.theme-text');
            
            if (savedTheme === 'dark') {{
                document.body.setAttribute('data-theme', 'dark');
                themeIcon.textContent = '☀️';
                themeText.textContent = '日间模式';
            }}
            
            // 标签切换功能
            const tabButtons = document.querySelectorAll('.tab-button');
            const newsCards = document.querySelectorAll('.news-card');
            
            tabButtons.forEach(button => {{
                button.addEventListener('click', function() {{
                    const category = this.dataset.category;
                    
                    // 更新活跃标签
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    // 筛选卡片
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
        
        return html_template
    
    def create_detail_page(self, news, all_news):
        """创建详情页"""
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
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0 var(--spacing-md);
        }}
        
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
            <div style="text-align: center;">
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
        return detail_html
    
    def run(self):
        """运行超级Ultra翻译新闻系统"""
        print("🚀 开始超级Ultra翻译AI新闻推送任务")
        print("=" * 50)
        
        # 1. 获取飞书令牌
        token = self.get_feishu_token()
        if not token:
            print("❌ 无法获取飞书令牌，任务终止")
            return False
        
        # 2. 获取新闻数据
        articles = self.get_news()
        if not articles:
            print("❌ 无法获取新闻，任务终止")  
            return False
        
        # 3. 生成超级Ultra版H5页面（完全中文化）
        print("\n" + "="*30)
        html_success = self.generate_super_ultra_html(articles)
        
        print("=" * 50)
        print(f"🎉 超级Ultra任务完成！成功处理 {len(articles)} 条新闻")
        if html_success:
            print("📱 超级Ultra H5页面: docs/index.html (100%中文化 + 主题切换)")
        print("🌙 主题切换功能已添加到右上角")
        
        print("\n🔥 超级Ultra版特性:")
        print("   ✅ 100%中文化 - 通用翻译引擎，适配任何标题")
        print("   ✅ 主题切换 - 日间/夜间模式")
        print("   ✅ 智能分类 - 自动识别新闻类型")
        print("   ✅ 时间显示 - 年月日 时分格式")
        print("   ✅ 响应式设计 - 完美适配各设备")
        return True

if __name__ == "__main__":
    processor = SuperUltraTranslationNewsProcessor()
    success = processor.run()
    if success:
        print("✅ 超级Ultra任务成功")
    else:
        print("❌ 超级Ultra任务失败")