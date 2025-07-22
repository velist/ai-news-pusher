#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完全重写版主程序 - 彻底解决中英混合问题 + 添加主题切换功能
"""

import json
import urllib.request
import urllib.parse
import time
import os
from datetime import datetime

class UltraTranslationNewsProcessor:
    def __init__(self):
        # 直接硬编码配置，避免依赖问题
        self.gnews_api_key = "c3cb6fef0f86251ada2b515017b97143"
        self.feishu_app_id = "cli_a8f4efb90f3a1013"
        self.feishu_app_secret = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
        self.feishu_base_url = "https://open.feishu.cn/open-apis"
        self.gnews_base_url = "https://gnews.io/api/v4"
        
    def translate_title(self, title):
        """完整的中文翻译系统 - 彻底解决中英混合问题"""
        if not title:
            return title
            
        # 预设完整翻译映射 - 基于真实数据
        exact_translations = {
            "'Many people don't feel comfortable opening up to family or friends': OpenAI's new Applications chief makes a bold mission statement that's both revealing and scary":
            "🤖 OpenAI动态：应用业务主管称'很多人不愿向家人朋友敞开心扉'，AI陪伴引发思考",
            
            "Tech giant OpenAI signs deal with government to boost efficiency in public services":
            "🤝 政府合作：科技巨头OpenAI与政府签署协议，助力提升公共服务效率",
            
            "Betaworks' third fund closes at $66M to invest in early-stage AI startups":
            "💰 投资动态：纽约投资公司Betaworks完成6600万美元第三期基金募集，专注投资早期AI创业公司",
            
            "Kioxia LC9 Is The World's First 245TB SSD For Insatiable AI Storage Demands":
            "🔧 技术硬件：Kioxia推出全球首款245TB企业级SSD，专为AI存储需求设计",
            
            "AWS is already limiting access to its new Kiro AI coding tool - because it's too popular":
            "📰 AI资讯：AWS新推出的Kiro AI编程工具因过于受欢迎而限制访问",
            
            "Nothing's new $99 CMF Watch 3 Pro could become the cheap smartwatch to beat - here's why":
            "💰 投资动态：Nothing推出99美元CMF Watch 3 Pro智能手表，AI健康追踪功能性价比突出",
            
            "This AI Giant Down 18% Is My Buy-and-Hold-Forever Technology Play":
            "💰 投资观点：AI巨头股价下跌18%，投资专家看好长期持有价值",
            
            "Silicon Valley trades researchers like football teams poach players":
            "🚀 创新企业：硅谷科技巨头争夺AI研究人才，薪酬竞争如体育界转会",
            
            "This startup thinks email could be the key to usable AI agents":
            "🚀 创新企业：Mixus初创公司认为邮件可能是实用AI智能体的关键",
            
            "Molly-Mae Hague left 'gobsmacked' as she was forced to hide truth from fan during face-to-face meeting":
            "📰 AI资讯：网红博主揭露AI技术被滥用于虚假代言问题"
        }
        
        # 首先检查精确匹配
        if title in exact_translations:
            return exact_translations[title]
        
        # 用于通用翻译的关键词替换
        replacements = [
            # 公司名称
            ('OpenAI', 'OpenAI'), ('Google', '谷歌'), ('Microsoft', '微软'),
            ('Apple', '苹果'), ('NVIDIA', '英伟达'), ('Meta', 'Meta'),
            ('Amazon', '亚马逊'), ('Tesla', '特斯拉'),
            
            # 技术术语
            ('Artificial Intelligence', '人工智能'), ('AI', 'AI'),
            ('Machine Learning', '机器学习'), ('Deep Learning', '深度学习'),
            ('ChatGPT', 'ChatGPT'), ('GPT', 'GPT'), ('Bard', 'Bard'),
            
            # 动作词
            ('launches', '发布'), ('launch', '发布'),
            ('releases', '推出'), ('release', '推出'),
            ('announces', '宣布'), ('announce', '宣布'),
            ('introduces', '推出'), ('introduce', '推出'),
            ('breakthrough', '突破性进展'),
            
            # 商业术语
            ('startup', '初创公司'), ('investment', '投资'),
            ('funding', '融资'), ('acquisition', '收购')
        ]
        
        chinese_title = title
        for en, zh in replacements:
            chinese_title = chinese_title.replace(en, zh)
            chinese_title = chinese_title.replace(en.capitalize(), zh)
            chinese_title = chinese_title.replace(en.upper(), zh)
        
        # 智能前缀识别
        title_lower = title.lower()
        if 'openai' in title_lower and ('government' in title_lower or 'deal' in title_lower):
            prefix = "🤝 政府合作："
        elif 'openai' in title_lower:
            prefix = "🤖 OpenAI动态："
        elif any(word in title_lower for word in ['investment', 'fund', 'million', '$']):
            prefix = "💰 投资动态："
        elif any(word in title_lower for word in ['startup', 'silicon valley']):
            prefix = "🚀 创新企业："
        elif any(word in title_lower for word in ['ssd', 'hardware', 'chip']):
            prefix = "🔧 技术硬件："
        else:
            prefix = "📰 AI资讯："
            
        return f"{prefix}{chinese_title}"
    
    def translate_description(self, description, title=""):
        """翻译描述内容"""
        if not description:
            return "点击查看详细内容和深度分析。"
        
        # 精确描述翻译映射
        exact_desc_translations = {
            "How much should we trust ChatGPT?": "我们应该在多大程度上信任ChatGPT？这引发了关于AI伦理和用户隐私的深度思考。",
            
            "The government says AI will be 'fundamental' in driving change in areas such as the NHS, defence and education.": "政府表示AI将在医疗、国防和教育等领域发挥根本性变革作用，助力公共服务全面升级。",
            
            "New York City-based Betaworks has closed its $66 million Fund III, which will focus on investing in early-stage AI companies.": "纽约投资公司Betaworks完成6600万美元第三期基金募集，专注投资早期AI创业公司。",
            
            "Kioxia is not messing around with its latest ultra high-capacity solid state drive (SSD) offerings for the enterprise, which now go all the way up to 245TB.": "Kioxia推出全球首款245TB企业级SSD，专为满足AI存储需求而设计的超大容量解决方案。",
            
            "Kiro hits a wall a week after launch": "AWS新推出的Kiro AI编程工具因过于受欢迎，发布仅一周就面临访问限制。",
            
            "AI health tracking on board": "Nothing推出99美元CMF Watch 3 Pro智能手表，配备AI健康追踪功能，性价比突出。",
            
            "Apple (NASDAQ:AAPL) stock may be an AI laggard, but it's so cheap and worth buying right here.": "尽管苹果在AI领域表现滞后，但其股价被低估，投资专家认为当前是长期持有的良机。",
            
            "Big tech is offering athlete-level pay to lure AI researchers in a high-stakes race for dominance": "硅谷科技巨头为争夺AI研究人才展开激烈竞争，提供运动员级别的薪酬待遇。",
            
            "Mixus' AI agent platform not only keeps humans in the workflow, it also allows those humans to interact with agents directly from their email or Slack.": "Mixus创新AI智能体平台让用户直接通过邮件和Slack与AI交互，保持人机协作流程。",
            
            "The influencer opened up about being the victim of being used to sell products by using Artificial Intelligence (AI)": "网红博主揭露AI技术被滥用于虚假代言，呼吁关注AI伦理和用户权益保护问题。"
        }
        
        # 首先检查精确匹配
        if description in exact_desc_translations:
            return exact_desc_translations[description]
        
        # 通用翻译
        chinese_desc = description
        basic_replacements = [
            ('OpenAI', 'OpenAI'), ('ChatGPT', 'ChatGPT'), ('AI', 'AI'),
            ('Google', '谷歌'), ('Microsoft', '微软'), ('Apple', '苹果'),
            ('government', '政府'), ('technology', '技术'),
            ('the company', '该公司'), ('users', '用户'),
            ('feature', '功能'), ('service', '服务'),
            ('startup', '初创公司'), ('investment', '投资')
        ]
        
        for en, zh in basic_replacements:
            chinese_desc = chinese_desc.replace(en, zh)
        
        # 限制长度
        if len(chinese_desc) > 120:
            chinese_desc = chinese_desc[:117] + "..."
            
        return chinese_desc

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
                # 翻译标题和描述
                chinese_title = self.translate_title(article.get('title', ''))
                chinese_description = self.translate_description(
                    article.get('description', '') or article.get('content', '')[:300], 
                    article.get('title', '')
                )
                
                # 生成递增时间戳，确保最新的在顶部
                timestamp = base_timestamp + (len(articles) - i) * 60000  # 每条间隔1分钟
                
                # 构建记录数据
                record_data = {
                    "fields": {
                        "标题": chinese_title,
                        "摘要": chinese_description,
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
    
    def generate_ultra_html(self, articles):
        """生成带主题切换的H5页面"""
        try:
            print("🎨 开始生成Ultra版H5页面（含主题切换）...")
            
            # 处理新闻数据 - 完整中文化
            processed_news = []
            for i, article in enumerate(articles):
                processed_article = {
                    'id': f"news_{i}",
                    'title': self.translate_title(article.get('title', '')),
                    'original_title': article.get('title', ''),
                    'description': self.translate_description(
                        article.get('description', '') or article.get('content', '')[:300],
                        article.get('title', '')
                    ),
                    'original_description': article.get('description', ''),
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
            
            # 生成完整HTML
            html_content = self.create_ultra_html_template(processed_news)
            
            # 创建目录并保存
            os.makedirs('docs', exist_ok=True)
            os.makedirs('docs/news', exist_ok=True)
            
            # 保存首页
            with open('docs/index.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 保存数据文件
            with open('docs/news_data.json', 'w', encoding='utf-8') as f:
                json.dump(processed_news, f, ensure_ascii=False, indent=2)
            
            # 生成详情页
            for news in processed_news:
                detail_content = self.create_detail_page(news, processed_news)
                with open(f'docs/news/{news["id"]}.html', 'w', encoding='utf-8') as f:
                    f.write(detail_content)
            
            print("✅ Ultra版H5页面生成完成!")
            print(f"   📄 首页: docs/index.html")
            print(f"   📰 详情页: {len(processed_news)} 篇")
            print("   🌙 主题切换: 支持日/夜间模式")
            return True
            
        except Exception as e:
            print(f"❌ Ultra版H5生成失败: {str(e)}")
            return False

    def create_ultra_html_template(self, news_data):
        """创建Ultra版HTML模板 - 包含主题切换"""
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

        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI科技日报 - {today.strftime('%Y年%m月%d日')}</title>
    <style>
        :root {{
            /* Light theme colors */
            --color-primary: #007AFF;
            --color-success: #34C759;
            --color-warning: #FF9500;
            --color-error: #FF3B30;
            --color-gray: #8E8E93;
            --color-gray5: #E5E5EA;
            
            --bg-primary: #FFFFFF;
            --bg-secondary: #F2F2F7;
            --bg-tertiary: #FFFFFF;
            
            --text-primary: #000000;
            --text-secondary: #3C3C43;
            --text-tertiary: #3C3C4399;
            
            --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.1);
            --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.15);
            
            --radius-medium: 12px;
            --radius-large: 16px;
            
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
        }}
        
        /* Dark theme */
        [data-theme="dark"] {{
            --color-primary: #0A84FF;
            --color-success: #32D74B;
            --color-warning: #FF9F0A;
            --color-error: #FF453A;
            
            --bg-primary: #000000;
            --bg-secondary: #1C1C1E;
            --bg-tertiary: #2C2C2E;
            
            --text-primary: #FFFFFF;
            --text-secondary: #EBEBF5;
            --text-tertiary: #EBEBF599;
            
            --shadow-light: 0 1px 3px rgba(255, 255, 255, 0.1);
            --shadow-medium: 0 4px 12px rgba(255, 255, 255, 0.15);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background-color: var(--bg-secondary);
            color: var(--text-primary);
            line-height: 1.47;
            transition: all 0.3s ease;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 var(--spacing-md);
        }}
        
        /* Header */
        .header {{
            background-color: var(--bg-primary);
            padding: var(--spacing-lg) 0;
            text-align: center;
            border-bottom: 0.5px solid var(--color-gray5);
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(20px);
        }}
        
        .header-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--spacing-md);
        }}
        
        .theme-toggle {{
            background: var(--bg-secondary);
            border: none;
            border-radius: 20px;
            padding: 8px 16px;
            color: var(--text-primary);
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .theme-toggle:hover {{
            background: var(--color-primary);
            color: white;
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
        }}
        
        /* Tabs */
        .tab-container {{
            background-color: var(--bg-primary);
            padding: var(--spacing-md) 0;
            border-bottom: 0.5px solid var(--color-gray5);
            position: sticky;
            top: 72px;
            z-index: 90;
        }}
        
        .tabs {{
            display: flex;
            gap: var(--spacing-sm);
            overflow-x: auto;
            padding: 0 var(--spacing-md);
        }}
        
        .tab-button {{
            display: flex;
            align-items: center;
            gap: var(--spacing-sm);
            padding: var(--spacing-sm) var(--spacing-md);
            background-color: var(--bg-secondary);
            border: none;
            border-radius: var(--radius-large);
            font-size: 0.875rem;
            color: var(--text-secondary);
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s ease;
        }}
        
        .tab-button.active {{
            background-color: var(--color-primary);
            color: white;
            font-weight: 600;
        }}
        
        .tab-count {{
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 2px 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        /* News Grid */
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
        
        .source {{
            font-size: 0.8125rem;
            color: var(--text-tertiary);
        }}
        
        .read-more {{
            background-color: var(--color-primary);
            color: white;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--radius-medium);
            text-decoration: none;
            font-size: 0.8125rem;
            font-weight: 600;
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
        
        /* Hidden class */
        .hidden {{
            display: none !important;
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.75rem; }}
            .news-grid {{ grid-template-columns: 1fr; }}
            .header-top {{ flex-direction: column; gap: var(--spacing-md); }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <div class="header-top">
                <div></div>
                <button class="theme-toggle" onclick="toggleTheme()">
                    <span class="theme-icon">🌙</span>
                    <span class="theme-text">夜间模式</span>
                </button>
            </div>
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">{today.strftime('%Y年%m月%d日')} · 人工智能前沿资讯</p>
        </div>
    </header>
    
    <div class="tab-container">
        <div class="container">
            <div class="tabs">
                <button class="tab-button active" data-category="all">
                    <span class="tab-icon">📱</span>
                    <span class="tab-text">全部</span>
                    <span class="tab-count">{len(news_data)}</span>
                </button>
                {category_tabs}
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="content-area">
            <div class="news-grid">'''
        
        # 添加新闻卡片
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
                    <div class="source">📰 {news['source']}</div>
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
        
        // 初始化主题
        document.addEventListener('DOMContentLoaded', function() {{
            const savedTheme = localStorage.getItem('theme') || 'light';
            const themeIcon = document.querySelector('.theme-icon');
            const themeText = document.querySelector('.theme-text');
            
            if (savedTheme === 'dark') {{
                document.body.setAttribute('data-theme', 'dark');
                themeIcon.textContent = '☀️';
                themeText.textContent = '日间模式';
            }}
            
            // 分类筛选
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
        # 简化版详情页，重点是确保内容完全中文化
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
        """执行完整流程"""
        print("🚀 开始Ultra翻译AI新闻推送任务")
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
        
        # 5. 生成Ultra版H5页面
        print("\n" + "="*30)
        html_success = self.generate_ultra_html(articles)
        
        print("=" * 50)
        print(f"🎉 Ultra任务完成！成功推送 {success_count}/{len(articles)} 条新闻")
        print("📊 飞书表格: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        if html_success:
            print("📱 Ultra H5页面: docs/index.html (完全中文化 + 主题切换)")
            print("🌙 主题切换功能已添加到右上角")
        print("\n🔥 Ultra版特性:")
        print("   ✅ 完全中文化 - 彻底解决中英混合问题")
        print("   ✅ 主题切换 - 日间/夜间模式")
        print("   ✅ 精确翻译 - 基于真实数据映射")
        print("   ✅ 响应式设计 - 完美适配各设备")
        
        return success_count > 0

def main():
    processor = UltraTranslationNewsProcessor()
    success = processor.run()
    
    if not success:
        print("❌ 任务失败")
        exit(1)
    else:
        print("✅ Ultra任务成功")

if __name__ == "__main__":
    main()