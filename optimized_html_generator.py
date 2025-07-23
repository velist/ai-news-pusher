#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的H5新闻页面生成器 - 简中用户友好版本
专门针对中国用户习惯和需求优化
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
        """增强的中文翻译 - 适合简中用户"""
        replacements = [
            # 公司名称
            ('OpenAI', 'OpenAI'), ('Google', '谷歌'), ('Microsoft', '微软'),
            ('Apple', '苹果'), ('NVIDIA', '英伟达'), ('Meta', 'Meta'),
            ('Amazon', '亚马逊'), ('Tesla', '特斯拉'), ('Anthropic', 'Anthropic'),
            
            # 技术术语
            ('Artificial Intelligence', '人工智能'), ('AI', 'AI'),
            ('Machine Learning', '机器学习'), ('Deep Learning', '深度学习'),
            ('Neural Network', '神经网络'), ('Large Language Model', '大语言模型'),
            ('ChatGPT', 'ChatGPT'), ('GPT', 'GPT'), ('Bard', 'Bard'),
            ('Claude', 'Claude'), ('LLM', '大模型'),
            
            # 技术动作
            ('breakthrough', '突破性进展'), ('launch', '正式发布'), 
            ('release', '推出'), ('announce', '宣布'), ('unveil', '揭晓'),
            ('investment', '投资'), ('funding', '融资'), ('acquisition', '收购'),
            ('partnership', '合作'), ('collaboration', '协作'),
            
            # 技术概念
            ('model', '模型'), ('algorithm', '算法'), ('data', '数据'),
            ('training', '训练'), ('inference', '推理'), ('fine-tuning', '微调'),
            ('multimodal', '多模态'), ('vision', '视觉'), ('language', '语言'),
            ('robotics', '机器人'), ('autonomous', '自动驾驶'),
            
            # 商业术语
            ('startup', '初创公司'), ('unicorn', '独角兽'), 
            ('valuation', '估值'), ('IPO', '上市'), ('Series', '轮'),
            ('revenue', '营收'), ('profit', '利润'), ('market', '市场'),
        ]
        
        chinese_title = title
        for en, zh in replacements:
            chinese_title = chinese_title.replace(en, zh)
        
        # 智能前缀识别
        title_lower = title.lower()
        if any(word in title_lower for word in ['breakthrough', 'revolutionary', 'game-changing']):
            return f"🚀 重大突破：{chinese_title}"
        elif any(word in title_lower for word in ['launch', 'release', 'unveil']):
            return f"🔥 最新发布：{chinese_title}"
        elif any(word in title_lower for word in ['investment', 'funding', 'acquisition']):
            return f"💰 投资动态：{chinese_title}"
        elif any(word in title_lower for word in ['partnership', 'collaboration']):
            return f"🤝 合作消息：{chinese_title}"
        else:
            return f"📰 AI资讯：{chinese_title}"
    
    def translate_description(self, description, title=""):
        """翻译和优化描述内容"""
        if not description:
            return "暂无详细描述，点击查看完整分析。"
        
        # 基础翻译
        replacements = [
            ('OpenAI', 'OpenAI'), ('Google', '谷歌'), ('Microsoft', '微软'),
            ('Apple', '苹果'), ('NVIDIA', '英伟达'),
            ('artificial intelligence', '人工智能'), ('AI', 'AI'),
            ('machine learning', '机器学习'), ('deep learning', '深度学习'),
            ('breakthrough', '突破性进展'), ('launch', '发布'),
            ('release', '推出'), ('announce', '宣布'),
            ('the company', '该公司'), ('users', '用户'),
            ('technology', '技术'), ('platform', '平台'),
            ('feature', '功能'), ('update', '更新'),
            ('model', '模型'), ('system', '系统'),
        ]
        
        chinese_desc = description
        for en, zh in replacements:
            chinese_desc = chinese_desc.replace(en, zh)
        
        # 确保长度合适
        if len(chinese_desc) > 150:
            chinese_desc = chinese_desc[:147] + "..."
        
        return chinese_desc
    
    def generate_china_analysis(self, title, description):
        """生成中国影响分析"""
        title_lower = title.lower()
        
        # 技术影响分析
        tech_impact = ""
        if any(word in title_lower for word in ['openai', 'gpt']):
            tech_impact = "对国内大模型厂商形成竞争压力，推动技术创新升级。"
        elif any(word in title_lower for word in ['google', 'bard']):
            tech_impact = "加速国内搜索和AI助手产品迭代，影响百度、阿里等公司战略。"
        elif any(word in title_lower for word in ['nvidia', 'chip']):
            tech_impact = "影响国内AI芯片产业发展，相关概念股值得关注。"
        else:
            tech_impact = "推动国内AI产业整体发展，促进技术进步和应用落地。"
        
        # 市场机遇分析
        market_opportunity = ""
        if any(word in title_lower for word in ['investment', 'funding']):
            market_opportunity = "为国内相关领域投资提供参考，关注产业链投资机会。"
        elif any(word in title_lower for word in ['partnership']):
            market_opportunity = "可能带来合作机遇，国内企业应积极寻求对接。"
        else:
            market_opportunity = "为国内企业提供发展思路，关注技术应用和商业模式创新。"
        
        return f"**技术影响：** {tech_impact}\\n\\n**市场机遇：** {market_opportunity}"
    
    def generate_investment_insight(self, title):
        """生成投资洞察"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['openai', 'chatgpt']):
            return "**相关概念股：** 科大讯飞、汉王科技、海天瑞声等AI概念股可能受益。"
        elif any(word in title_lower for word in ['nvidia', 'chip']):
            return "**相关概念股：** 寒武纪、景嘉微、紫光国微等AI芯片股值得关注。"
        elif any(word in title_lower for word in ['robot']):
            return "**相关概念股：** 机器人、埃斯顿、新时达等机器人产业链股票。"
        else:
            return "**投资建议：** 关注AI产业链相关标的，长期看好技术进步带来的投资机遇。"
    
    def generate_optimized_html(self, articles):
        """生成简中用户友好的HTML页面"""
        try:
            print("🎨 开始生成简中用户友好页面...")
            
            # 处理新闻数据 - 全面中文化
            processed_news = []
            for i, article in enumerate(articles):
                original_title = article.get('title', '')
                original_description = article.get('description', '')
                
                processed_article = {
                    'id': f"news_{i}",  # 为详情页添加唯一ID
                    'title': self.translate_title(original_title),
                    'original_title': original_title,
                    'description': self.translate_description(original_description, original_title),
                    'original_description': original_description,
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', '未知来源'),
                    'publishedAt': article.get('publishedAt', ''),
                    'image': article.get('image', ''),
                    'category': self.categorize_news(original_title),
                    'importance': self.get_importance_score(original_title),
                    # 新增中国本土化内容
                    'china_analysis': self.generate_china_analysis(original_title, original_description),
                    'investment_insight': self.generate_investment_insight(original_title)
                }
                processed_news.append(processed_article)
            
            # 按重要性排序
            processed_news.sort(key=lambda x: x['importance'], reverse=True)
            
            # 生成首页和详情页HTML内容
            homepage_content = self.create_homepage_template(processed_news)
            
            # 创建目录
            os.makedirs('docs', exist_ok=True)
            os.makedirs('docs/news', exist_ok=True)
            
            # 写入首页
            with open('docs/index.html', 'w', encoding='utf-8') as f:
                f.write(homepage_content)
            
            # 生成每条新闻的详情页
            for news in processed_news:
                detail_content = self.create_detail_template(news, processed_news)
                with open(f'docs/news/{news["id"]}.html', 'w', encoding='utf-8') as f:
                    f.write(detail_content)
            
            # 生成新闻数据JSON（供JavaScript使用）
            with open('docs/news_data.json', 'w', encoding='utf-8') as f:
                import json
                json.dump(processed_news, f, ensure_ascii=False, indent=2)
            
            print("✅ 简中用户友好页面生成完成:")
            print("   📄 首页: docs/index.html") 
            print(f"   📰 详情页: docs/news/ ({len(processed_news)} 篇)")
            print("   📊 数据文件: docs/news_data.json")
            return True
            
        except Exception as e:
            print(f"❌ H5页面生成失败: {str(e)}")
            return False
    
    def create_homepage_template(self, news_data):
        """创建简中用户友好的首页模板"""
        
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
            /* 苹果设计系统颜色 */
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
        
        [data-theme="dark"] {{
            --color-primary: #0A84FF;
            --color-secondary: #5E5CE6;
            --color-success: #32D74B;
            --color-warning: #FF9F0A;
            --color-error: #FF453A;
            
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --bg-tertiary: #2C2C2E;
            --bg-grouped: #000000;
            
            --text-primary: #FFFFFF;
            --text-secondary: #EBEBF5;
            --text-tertiary: #EBEBF599;
            --text-quaternary: #EBEBF526;
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
            transition: all 0.3s ease;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 var(--spacing-md);
        }}
        
        /* 主题切换按钮 */
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
        
        /* 头部区域 - 简化版 */
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
        
        .personal-info {{
            background-color: var(--bg-secondary);
            border-radius: var(--radius-medium);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-md);
            text-align: center;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}
        
        .ai-group-info {{
            margin-top: var(--spacing-sm);
            font-weight: 500;
            color: var(--color-primary);
        }}
        
        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: var(--spacing-sm);
        }}
        
        .header .subtitle {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            font-weight: 400;
        }}
        
        /* 分类标签栏 */
        .tab-container {{
            background-color: var(--bg-primary);
            padding: var(--spacing-md) 0;
            border-bottom: 0.5px solid var(--color-gray5);
            position: sticky;
            top: 72px;
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
            cursor: pointer;
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
            pointer-events: none; /* 防止事件冒泡 */
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
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .container {{
                padding: 0 var(--spacing-md);
            }}
            
            .header {{
                padding: var(--spacing-md) 0;
            }}
            
            .header h1 {{
                font-size: 1.75rem;
            }}
            
            .tab-container {{
                top: 68px;
            }}
            
            .news-grid {{
                grid-template-columns: 1fr;
                gap: var(--spacing-md);
            }}
            
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
        
        @media (max-width: 480px) {{
            .container {{
                padding: 0 var(--spacing-sm);
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
    <!-- 主题切换按钮 -->
    <button class="theme-toggle" onclick="toggleTheme()">
        <span class="theme-icon">🌙</span>
        <span class="theme-text">夜间模式</span>
    </button>
    
    <!-- 头部 - 简化版 -->
    <header class="header">
        <div class="container">
            <div class="personal-info">
                <div>👨‍💻 个人AI资讯整理 | 专注前沿技术分析</div>
                <div class="ai-group-info">💬 AI交流群 · 欢迎加入：forxy9</div>
            </div>
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">{self.today.strftime('%Y年%m月%d日')} · 人工智能前沿资讯</p>
        </div>
    </header>
    
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
        
        # 添加新闻卡片 - 点击跳转详情页
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
            <article class="news-card {priority_class}" data-category="{news['category']['name']}" 
                     onclick="window.location.href='news/{news['id']}.html'" 
                     style="animation-delay: {i * 0.05}s;">
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
                    <div class="read-more">
                        查看详情
                    </div>
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
            
            // 分类筛选功能
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
        }});
    </script>
</body>
</html>'''
        
        return html_template
    
    def create_detail_template(self, news, all_news):
        """创建新闻详情页模板"""
        
        # 找到上一条和下一条新闻
        current_index = next((i for i, n in enumerate(all_news) if n['id'] == news['id']), 0)
        prev_news = all_news[current_index - 1] if current_index > 0 else None
        next_news = all_news[current_index + 1] if current_index < len(all_news) - 1 else None
        
        detail_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{news['title']} - AI科技日报</title>
    <style>
        :root {{
            --color-primary: #007AFF;
            --color-secondary: #5856D6;
            --color-success: #34C759;
            --color-warning: #FF9500;
            --color-error: #FF3B30;
            --color-gray: #8E8E93;
            --color-gray5: #E5E5EA;
            
            --bg-primary: #FFFFFF;
            --bg-secondary: #F2F2F7;
            --bg-tertiary: #FFFFFF;
            --bg-grouped: #F2F2F7;
            
            --text-primary: #000000;
            --text-secondary: #3C3C43;
            --text-tertiary: #3C3C4399;
            
            --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.1);
            --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.15);
            
            --radius-small: 8px;
            --radius-medium: 12px;
            --radius-large: 16px;
            
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
        }}
        
        [data-theme="dark"] {{
            --color-primary: #0A84FF;
            --color-secondary: #5E5CE6;
            --color-success: #32D74B;
            --color-warning: #FF9F0A;
            --color-error: #FF453A;
            
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --bg-tertiary: #2C2C2E;
            --bg-grouped: #000000;
            
            --text-primary: #FFFFFF;
            --text-secondary: #EBEBF5;
            --text-tertiary: #EBEBF599;
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
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            transition: all 0.3s ease;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 0 var(--spacing-md);
        }}
        
        /* 主题切换按钮 */
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
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: var(--shadow-light);
        }}
        
        /* 导航栏 */
        .navbar {{
            background-color: var(--bg-primary);
            border-bottom: 0.5px solid var(--color-gray5);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        
        .nav-content {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--spacing-md) 0;
            min-height: 56px;
        }}
        
        .back-button {{
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
            color: var(--color-primary);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            padding: var(--spacing-xs) 0;
        }}
        
        .back-button:hover {{
            opacity: 0.7;
        }}
        
        .nav-title {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-primary);
        }}
        
        .share-button {{
            color: var(--color-primary);
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            padding: var(--spacing-xs) 0;
        }}
        
        .share-button:hover {{
            opacity: 0.7;
        }}
        
        /* 文章内容 */
        .article {{
            background-color: var(--bg-tertiary);
            border-radius: var(--radius-large);
            margin: var(--spacing-lg) 0;
            overflow: hidden;
            box-shadow: var(--shadow-light);
        }}
        
        .article-header {{
            padding: var(--spacing-lg);
            border-bottom: 0.5px solid var(--color-gray5);
        }}
        
        .article-meta {{
            display: flex;
            align-items: center;
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }}
        
        .category-badge {{
            display: inline-flex;
            align-items: center;
            gap: var(--spacing-xs);
            padding: var(--spacing-xs) var(--spacing-sm);
            border-radius: var(--radius-small);
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .importance-stars {{
            display: flex;
            gap: 2px;
        }}
        
        .star {{
            color: var(--color-warning);
            font-size: 0.75rem;
        }}
        
        .article-title {{
            font-size: 1.75rem;
            font-weight: 700;
            line-height: 1.3;
            margin-bottom: var(--spacing-md);
            color: var(--text-primary);
        }}
        
        .article-description {{
            font-size: 1.125rem;
            color: var(--text-secondary);
            line-height: 1.5;
            margin-bottom: var(--spacing-lg);
        }}
        
        .source-info {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.875rem;
            color: var(--text-tertiary);
        }}
        
        .source {{
            display: flex;
            align-items: center;
            gap: var(--spacing-xs);
        }}
        
        /* 分析内容 */
        .analysis-section {{
            padding: var(--spacing-lg);
        }}
        
        .analysis-title {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: var(--spacing-md);
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
        }}
        
        .analysis-content {{
            font-size: 1rem;
            line-height: 1.6;
            color: var(--text-secondary);
            margin-bottom: var(--spacing-lg);
        }}
        
        .analysis-content strong {{
            color: var(--text-primary);
            font-weight: 600;
        }}
        
        .section-divider {{
            border: none;
            height: 0.5px;
            background-color: var(--color-gray5);
            margin: var(--spacing-lg) 0;
        }}
        
        /* 操作按钮 */
        .action-buttons {{
            display: flex;
            gap: var(--spacing-md);
            padding: var(--spacing-lg);
            border-top: 0.5px solid var(--color-gray5);
        }}
        
        .action-button {{
            flex: 1;
            padding: var(--spacing-md);
            border-radius: var(--radius-medium);
            text-decoration: none;
            text-align: center;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        
        .primary-button {{
            background-color: var(--color-primary);
            color: white;
        }}
        
        .primary-button:hover {{
            background-color: var(--color-secondary);
            transform: scale(1.02);
        }}
        
        .secondary-button {{
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            border: 0.5px solid var(--color-gray5);
        }}
        
        .secondary-button:hover {{
            background-color: var(--color-gray5);
        }}
        
        /* 导航 */
        .navigation {{
            display: flex;
            gap: var(--spacing-md);
            margin: var(--spacing-lg) 0;
        }}
        
        .nav-card {{
            flex: 1;
            background-color: var(--bg-tertiary);
            border-radius: var(--radius-medium);
            padding: var(--spacing-md);
            text-decoration: none;
            color: var(--text-primary);
            box-shadow: var(--shadow-light);
            transition: all 0.2s ease;
        }}
        
        .nav-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
        }}
        
        .nav-card.disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
        }}
        
        .nav-label {{
            font-size: 0.75rem;
            color: var(--text-tertiary);
            margin-bottom: var(--spacing-xs);
        }}
        
        .nav-title {{
            font-size: 0.875rem;
            font-weight: 500;
            line-height: 1.3;
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .container {{
                padding: 0 var(--spacing-md);
            }}
            
            .article-title {{
                font-size: 1.5rem;
            }}
            
            .article-description {{
                font-size: 1rem;
            }}
            
            .action-buttons {{
                flex-direction: column;
            }}
            
            .navigation {{
                flex-direction: column;
            }}
            
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
        
        @media (max-width: 480px) {{
            .container {{
                padding: 0 var(--spacing-sm);
            }}
            
            .article {{
                margin: var(--spacing-md) 0;
            }}
            
            .article-header, .analysis-section, .action-buttons {{
                padding: var(--spacing-md);
            }}
            
            .article-title {{
                font-size: 1.25rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 主题切换按钮 -->
    <button class="theme-toggle" onclick="toggleTheme()">
        <span class="theme-icon">🌙</span>
        <span class="theme-text">夜间模式</span>
    </button>
    
    <!-- 导航栏 -->
    <nav class="navbar">
        <div class="container">
            <div class="nav-content">
                <a href="../index.html" class="back-button">
                    <span>‹</span>
                    <span>返回首页</span>
                </a>
                <div class="nav-title">AI科技日报</div>
                <div class="share-button" onclick="shareArticle()">分享</div>
            </div>
        </div>
    </nav>
    
    <!-- 文章内容 -->
    <div class="container">
        <article class="article">
            <header class="article-header">
                <div class="article-meta">
                    <div class="category-badge" style="background-color: {news['category']['color']}; color: white;">
                        <span>{news['category']['icon']}</span>
                        <span>{news['category']['name']}</span>
                    </div>
                    <div class="importance-stars">
                        {''.join(['<span class="star">★</span>' for _ in range(news['importance'])])}
                    </div>
                </div>
                
                <h1 class="article-title">{news['title']}</h1>
                <p class="article-description">{news['description']}</p>
                
                <div class="source-info">
                    <div class="source">
                        <span>📰</span>
                        <span>{news['source']}</span>
                    </div>
                    <div class="publish-time">
                        {self.today.strftime('%Y年%m月%d日')}
                    </div>
                </div>
            </header>
            
            <section class="analysis-section">
                <h2 class="analysis-title">
                    <span>🇨🇳</span>
                    <span>中国影响分析</span>
                </h2>
                <div class="analysis-content">
                    {news['china_analysis'].replace('\\n\\n', '<br><br>')}
                </div>
                
                <hr class="section-divider">
                
                <h2 class="analysis-title">
                    <span>💰</span>
                    <span>投资视角</span>
                </h2>
                <div class="analysis-content">
                    {news['investment_insight']}
                </div>
                
                <hr class="section-divider">
                
                <h2 class="analysis-title">
                    <span>🤖</span>
                    <span>AI观点</span>
                </h2>
                <div class="analysis-content">
                    基于当前技术发展趋势，该新闻反映出AI领域的重要变化。从技术角度看，这一发展将推动相关技术栈的进步，影响整个行业生态。建议关注其对现有产品和服务的潜在冲击，以及可能带来的新机遇。
                </div>
                
                <hr class="section-divider">
                
                <h2 class="analysis-title">
                    <span>📈</span>
                    <span>投资方向</span>
                </h2>
                <div class="analysis-content">
                    <strong>短期关注：</strong>相关概念股可能出现波动，建议关注市场反应和资金流向。<br><br>
                    <strong>中长期布局：</strong>重点关注技术落地应用、产业化进程和市场接受度。建议关注产业链上下游企业，特别是具备核心技术优势和商业化能力的公司。
                </div>
                
                <hr class="section-divider">
                
                <h2 class="analysis-title">
                    <span>📄</span>
                    <span>原文摘要</span>
                </h2>
                <div class="analysis-content">
                    <strong>英文标题：</strong>{news['original_title']}<br><br>
                    <strong>内容摘要：</strong>{news['original_description'] or '暂无详细描述'}
                </div>
            </section>
            
            <div class="action-buttons">
                <a href="{news['url']}" target="_blank" class="action-button primary-button">
                    阅读原文
                </a>
                <a href="../index.html" class="action-button secondary-button">
                    返回首页
                </a>
            </div>
        </article>
        
        <!-- 导航到上一篇/下一篇 -->
        <div class="navigation">'''
        
        if prev_news:
            detail_html += f'''
            <a href="{prev_news['id']}.html" class="nav-card">
                <div class="nav-label">上一篇</div>
                <div class="nav-title">{prev_news['title']}</div>
            </a>'''
        else:
            detail_html += '''
            <div class="nav-card disabled">
                <div class="nav-label">上一篇</div>
                <div class="nav-title">已是第一篇</div>
            </div>'''
        
        if next_news:
            detail_html += f'''
            <a href="{next_news['id']}.html" class="nav-card">
                <div class="nav-label">下一篇</div>
                <div class="nav-title">{next_news['title']}</div>
            </a>'''
        else:
            detail_html += '''
            <div class="nav-card disabled">
                <div class="nav-label">下一篇</div>
                <div class="nav-title">已是最后一篇</div>
            </div>'''
            
        detail_html += f'''
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
                if (themeText) themeText.textContent = '夜间模式';
                localStorage.setItem('theme', 'light');
            }} else {{
                body.setAttribute('data-theme', 'dark');
                themeIcon.textContent = '☀️';
                if (themeText) themeText.textContent = '日间模式';
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
                if (themeText) themeText.textContent = '日间模式';
            }}
        }});
        
        // 分享功能
        function shareArticle() {{
            if (navigator.share) {{
                navigator.share({{
                    title: '{news['title']}',
                    text: '{news['description'][:100]}...',
                    url: window.location.href
                }}).then(() => {{
                    console.log('分享成功');
                }}).catch((error) => {{
                    console.log('分享失败:', error);
                    fallbackShare();
                }});
            }} else {{
                fallbackShare();
            }}
        }}
        
        function fallbackShare() {{
            const url = window.location.href;
            const title = '{news['title']}';
            
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(url).then(() => {{
                    alert('链接已复制到剪贴板');
                }}).catch(() => {{
                    showShareOptions(url, title);
                }});
            }} else {{
                showShareOptions(url, title);
            }}
        }}
        
        function showShareOptions(url, title) {{
            const shareText = `${{title}} - ${{url}}`;
            prompt('复制链接分享:', shareText);
        }}
    </script>
</body>
</html>'''
        
        return detail_html


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
        print("🎉 简中用户友好页面生成测试完成！")