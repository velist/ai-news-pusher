#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版主程序 - 专注核心功能，确保翻译生效
"""

import json
import urllib.request
import urllib.parse
import time
import os
from datetime import datetime

class SimpleNewsProcessor:
    def __init__(self):
        # 直接硬编码配置，避免依赖问题
        self.gnews_api_key = "c3cb6fef0f86251ada2b515017b97143"
        self.feishu_app_id = "cli_a8f4efb90f3a1013"
        self.feishu_app_secret = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
        self.feishu_base_url = "https://open.feishu.cn/open-apis"
        self.gnews_base_url = "https://gnews.io/api/v4"
        
    def translate_title(self, title):
        """简化但有效的中文翻译"""
        if not title:
            return title
            
        # 核心翻译映射
        replacements = [
            ('OpenAI', 'OpenAI'),
            ('Google', '谷歌'),
            ('Microsoft', '微软'),
            ('Apple', '苹果'),
            ('NVIDIA', '英伟达'),
            ('Artificial Intelligence', '人工智能'),
            ('AI', 'AI'),
            ('Machine Learning', '机器学习'),
            ('ChatGPT', 'ChatGPT'),
            ('GPT-4', 'GPT-4'),
            ('GPT-5', 'GPT-5'),
            ('Launches', '发布'),
            ('Releases', '发布'),
            ('Announces', '宣布'),
            ('Introduces', '推出'),
            ('Updates', '更新'),
            ('New', '全新'),
            ('Latest', '最新'),
            ('Advanced', '先进的'),
            ('Revolutionary', '革命性'),
            ('Breakthrough', '突破性'),
        ]
        
        chinese_title = title
        
        # 简单字符串替换
        for english, chinese in replacements:
            chinese_title = chinese_title.replace(english, chinese)
            chinese_title = chinese_title.replace(english.lower(), chinese)
        
        # 计算英文字符比例
        english_chars = sum(1 for c in chinese_title if c.isalpha() and ord(c) < 128)
        total_chars = len(chinese_title)
        
        # 如果英文字符超过50%，添加中文前缀
        if total_chars > 0 and english_chars / total_chars > 0.5:
            if any(word in title.lower() for word in ['launch', 'release', 'announce']):
                chinese_title = f"🚀 最新发布：{chinese_title}"
            elif any(word in title.lower() for word in ['breakthrough', 'innovation']):
                chinese_title = f"💡 技术突破：{chinese_title}"
            elif any(word in title.lower() for word in ['update', 'improve']):
                chinese_title = f"🔄 重大更新：{chinese_title}"
            else:
                chinese_title = f"📰 AI资讯：{chinese_title}"
        
        return chinese_title
    
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
    
    def get_max_timestamp(self, token):
        """获取表格最大时间戳"""
        try:
            app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
            table_id = "tblyPOJ4k9DxJuKc"
            
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            max_timestamp = int(time.time() * 1000)
            
            if result.get('code') == 0:
                records = result.get('data', {}).get('items', [])
                for record in records:
                    update_date = record.get('fields', {}).get('更新日期', 0)
                    if isinstance(update_date, (int, float)) and update_date > max_timestamp:
                        max_timestamp = int(update_date)
            
            print(f"📅 当前最大时间戳: {max_timestamp}")
            return max_timestamp
            
        except Exception as e:
            print(f"❌ 获取时间戳失败: {str(e)}")
            return int(time.time() * 1000)
    
    def push_news(self, articles, token, base_timestamp):
        """推送新闻到飞书表格"""
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        success_count = 0
        
        for i, article in enumerate(articles):
            try:
                # 翻译标题
                chinese_title = self.translate_title(article.get('title', ''))
                
                # 生成递增时间戳，确保最新的在顶部
                timestamp = base_timestamp + (len(articles) - i) * 60000  # 每条间隔1分钟
                
                # 构建记录数据
                record_data = {
                    "fields": {
                        "标题": chinese_title,
                        "摘要": (article.get('description', '') or article.get('content', ''))[:300],
                        "AI观点": "该AI技术发展值得关注，体现了人工智能领域的持续创新进展。",
                        "中国影响分析": "技术发展：推动国内AI产业升级\n市场机遇：为企业提供新发展方向\n竞争态势：需关注对现有格局的影响",
                        "更新日期": timestamp,
                        "来源": {
                            "link": article.get('url', ''),
                            "text": article.get('source', {}).get('name', '新闻源')
                        }
                    }
                }
                
                # 发送请求
                url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
                req = urllib.request.Request(
                    url,
                    data=json.dumps(record_data).encode('utf-8'),
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))
                
                if result.get('code') == 0:
                    success_count += 1
                    print(f"✅ 推送成功 ({i+1}/{len(articles)}): {chinese_title[:50]}...")
                else:
                    print(f"❌ 推送失败 ({i+1}): {result}")
                
                time.sleep(0.5)  # 避免频率限制
                
            except Exception as e:
                print(f"❌ 推送异常 ({i+1}): {str(e)}")
        
        return success_count
    
    def generate_html_page(self, articles):
        """生成H5新闻页面"""
        try:
            print("🎨 开始生成H5新闻页面...")
            
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
            html_content = self.create_html_template(processed_news)
            
            # 创建目录
            os.makedirs('docs', exist_ok=True)
            
            # 写入文件
            with open('docs/index.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 创建GitHub Pages配置
            with open('docs/_config.yml', 'w', encoding='utf-8') as f:
                f.write('# GitHub Pages配置\\ntheme: jekyll-theme-minimal\\n')
            
            print("✅ H5新闻页面生成完成: docs/index.html")
            return True
            
        except Exception as e:
            print(f"❌ H5页面生成失败: {str(e)}")
            return False
    
    def create_html_template(self, news_data):
        """创建HTML模板"""
        today = datetime.now()
        
        html_template = f'''<!DOCTYPE html>
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
        
        <div class="news-grid">'''
        
        # 添加新闻卡片
        for i, news in enumerate(news_data):
            priority_class = 'priority-high' if news['importance'] >= 4 else 'priority-medium' if news['importance'] >= 3 else 'priority-low'
            
            stars = ''.join(['<i class="fas fa-star star"></i>' for _ in range(news['importance'])])
            
            card_html = f'''
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
            </article>'''
            
            html_template += card_html
        
        html_template += f'''
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
</html>'''
        
        return html_template
    
    def run(self):
        """执行完整流程"""
        print("🚀 开始AI新闻推送任务")
        print("=" * 50)
        
        # 1. 获取飞书令牌
        token = self.get_feishu_token()
        if not token:
            print("❌ 无法获取飞书令牌，任务终止")
            return False
        
        # 2. 获取新闻
        articles = self.get_news()
        if not articles:
            print("❌ 无法获取新闻，任务终止")  
            return False
        
        # 3. 获取基准时间戳
        base_timestamp = self.get_max_timestamp(token)
        
        # 4. 推送新闻
        success_count = self.push_news(articles, token, base_timestamp)
        
        # 5. 生成H5新闻页面
        print("\n" + "="*30)
        html_success = self.generate_html_page(articles)
        if html_success:
            print("🎉 H5新闻页面已生成")
        
        # 6. 美化表格（每周一次）
        if datetime.now().weekday() == 0:  # 周一
            print("🎨 执行每周表格美化...")
            self.enhance_table(token)
        
        print("=" * 50)
        print(f"🎉 任务完成！成功推送 {success_count}/{len(articles)} 条新闻")
        print("📊 飞书表格: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        if html_success:
            print("📱 H5新闻页面: docs/index.html (已生成，可部署到GitHub Pages)")
        print("\n💡 个性化展示选项:")
        print("   ✅ 飞书多维表格 - 传统表格展示")
        print("   ✅ H5响应式页面 - 卡片式个性化展示")
        print("   📦 飞书卡片消息 - feishu_cards.py")
        print("   📰 微信公众号 - wechat_push.py")
        
        return success_count > 0
    
    def enhance_table(self, token):
        """表格美化功能"""
        try:
            # 添加今日亮点卡片
            self.add_highlight_card(token)
        except Exception as e:
            print(f"⚠️ 表格美化失败: {str(e)}")
    
    def add_highlight_card(self, token):
        """添加今日亮点卡片"""
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        
        try:
            # 获取最新3条记录
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=3"
            req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') != 0:
                return
            
            records = result.get('data', {}).get('items', [])
            if not records:
                return
            
            # 创建亮点汇总
            highlight_titles = []
            for record in records[:3]:
                title = record.get('fields', {}).get('标题', '')
                if title and not title.startswith('🌟'):  # 避免包含之前的亮点卡片
                    clean_title = title.replace('📰 AI资讯：', '').replace('🚀 最新发布：', '')
                    highlight_titles.append(clean_title[:60])
            
            if not highlight_titles:
                return
            
            today = datetime.now().strftime('%Y年%m月%d日')
            highlight_content = f"""🌟 【{today} AI科技亮点】

📊 今日热门话题：
• {highlight_titles[0] if len(highlight_titles) > 0 else '暂无'}
• {highlight_titles[1] if len(highlight_titles) > 1 else '暂无'}
• {highlight_titles[2] if len(highlight_titles) > 2 else '暂无'}

💡 AI行业正快速发展，关注技术突破和商业应用进展"""
            
            # 创建亮点记录
            highlight_timestamp = int(time.time() * 1000) + 7200000  # 加2小时确保在最顶部
            
            highlight_record = {
                "fields": {
                    "标题": f"🌟 今日AI亮点 - {today}",
                    "摘要": highlight_content,
                    "AI观点": "每日亮点汇总帮助快速掌握AI行业关键动态和趋势。",
                    "中国影响分析": "信息聚合：提高AI资讯获取效率\n趋势识别：便于把握行业发展脉络",
                    "更新日期": highlight_timestamp,
                    "来源": {
                        "link": "https://example.com/highlights",
                        "text": "每日亮点"
                    }
                }
            }
            
            # 推送亮点卡片
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            req = urllib.request.Request(
                url,
                data=json.dumps(highlight_record).encode('utf-8'),
                headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') == 0:
                print("✨ 今日亮点卡片已添加")
                
        except Exception as e:
            print(f"⚠️ 亮点卡片添加失败: {str(e)}")

def main():
    processor = SimpleNewsProcessor()
    success = processor.run()
    
    if not success:
        print("❌ 任务失败")
        exit(1)
    else:
        print("✅ 任务成功")

if __name__ == "__main__":
    main()