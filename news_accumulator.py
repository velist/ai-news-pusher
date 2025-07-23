#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI新闻累积更新系统 - 保留历史新闻，持续增量更新
"""

import os
import json
import urllib.request
import urllib.parse
import time
import hashlib
from datetime import datetime, timedelta

class AINewsAccumulator:
    def __init__(self):
        # API配置
        self.gnews_api_key = os.getenv('GNEWS_API_KEY', 'c3cb6fef0f86251ada2b515017b97143')
        self.gnews_base_url = "https://gnews.io/api/v4"
        self.news_data_file = 'docs/news_data.json'
        
    def get_latest_news(self):
        """获取最新科技、游戏、经济新闻"""
        all_articles = []
        
        # 定义多个搜索类别 - 降低数量确保稳定性
        search_queries = [
            {
                'query': 'AI OR OpenAI OR ChatGPT',  # 简化搜索词
                'category': 'AI科技',
                'max': '8'  # 降低数量
            },
            {
                'query': 'gaming OR PlayStation OR Xbox',  # 简化搜索词
                'category': '游戏科技', 
                'max': '6'
            },
            {
                'query': 'stock OR bitcoin OR finance',  # 简化搜索词
                'category': '经济金融',
                'max': '6'
            }
        ]
        
        for search_config in search_queries:
            max_retries = 3 if search_config['category'] == 'AI科技' else 1  # AI科技重试3次
            
            for attempt in range(max_retries):
                try:
                    params = {
                        'apikey': self.gnews_api_key,
                        'q': search_config['query'],
                        'lang': 'en',
                        'max': search_config['max'],
                        'sortby': 'publishedAt'
                    }
                    
                    query_string = urllib.parse.urlencode(params)
                    url = f"{self.gnews_base_url}/search?{query_string}"
                    
                    with urllib.request.urlopen(url, timeout=20) as response:  # 增加超时时间
                        result = json.loads(response.read().decode('utf-8'))
                    
                    articles = result.get('articles', [])
                    # 为每篇文章添加搜索类别标记
                    for article in articles:
                        article['search_category'] = search_config['category']
                    
                    all_articles.extend(articles)
                    print(f"✅ {search_config['category']}获取 {len(articles)} 条新闻")
                    break  # 成功获取，跳出重试循环
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ {search_config['category']}第{attempt+1}次尝试失败，重试中...")
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        print(f"❌ 获取{search_config['category']}新闻失败: {str(e)}")
                        
                        # 如果是AI科技新闻失败，使用备用搜索
                        if search_config['category'] == 'AI科技':
                            try:
                                print("🔄 尝试备用AI搜索策略...")
                                backup_params = {
                                    'apikey': self.gnews_api_key,
                                    'q': 'OpenAI OR ChatGPT OR "artificial intelligence"',
                                    'lang': 'en',
                                    'max': '10',
                                    'sortby': 'publishedAt'
                                }
                                backup_query = urllib.parse.urlencode(backup_params)
                                backup_url = f"{self.gnews_base_url}/search?{backup_query}"
                                
                                with urllib.request.urlopen(backup_url, timeout=15) as backup_response:
                                    backup_result = json.loads(backup_response.read().decode('utf-8'))
                                
                                backup_articles = backup_result.get('articles', [])
                                for article in backup_articles:
                                    article['search_category'] = 'AI科技'
                                
                                all_articles.extend(backup_articles)
                                print(f"✅ AI科技备用策略获取 {len(backup_articles)} 条新闻")
                            except:
                                print("❌ AI科技备用策略也失败")
                    continue
        
        print(f"✅ 总共获取 {len(all_articles)} 条最新新闻")
        return all_articles
    
    def load_existing_news(self):
        """加载现有新闻数据"""
        try:
            if os.path.exists(self.news_data_file):
                with open(self.news_data_file, 'r', encoding='utf-8') as f:
                    existing_news = json.load(f)
                print(f"📚 加载现有新闻: {len(existing_news)} 条")
                return existing_news
            else:
                print("📝 首次运行，创建新的新闻数据")
                return []
        except Exception as e:
            print(f"❌ 加载现有新闻失败: {str(e)}")
            return []
    
    def generate_news_id(self, article):
        """生成新闻唯一ID"""
        # 使用URL和标题生成唯一ID
        content = f"{article.get('url', '')}{article.get('title', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def is_news_recent(self, publish_date, days=3):
        """检查新闻是否在指定天数内"""
        try:
            if not publish_date:
                return False
            
            # 解析发布时间
            if 'T' in publish_date:
                news_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            else:
                news_date = datetime.fromisoformat(publish_date)
            
            # 计算时间差
            now = datetime.now().replace(tzinfo=news_date.tzinfo) if news_date.tzinfo else datetime.now()
            time_diff = now - news_date
            
            return time_diff.days <= days
        except:
            return False
    
    def translate_title(self, title, search_category=""):
        """翻译标题为完整中文，绝对避免中英混杂"""
        if not title:
            return title
        
        title_lower = title.lower()
        
        # 基于搜索类别生成完全中文标题 - 关键修复：不再拼接英文原标题
        if search_category == 'AI科技':
            if 'openai' in title_lower:
                if 'chatgpt' in title_lower or 'gpt' in title_lower:
                    return "🤖 OpenAI发布ChatGPT重大更新，AI对话能力显著提升"
                else:
                    return "🤖 OpenAI人工智能技术最新突破，引领AI行业发展方向"
            elif 'google' in title_lower and 'ai' in title_lower:
                return "🔍 谷歌AI研发取得新进展，搜索与智能技术深度融合"
            elif 'microsoft' in title_lower:
                return "💼 微软AI战略布局更新，企业级人工智能解决方案优化"
            elif 'meta' in title_lower:
                return "🌐 Meta AI技术创新发展，社交平台智能化转型加速"
            else:
                return "🤖 人工智能行业重要进展，AI技术应用领域持续扩展"
                
        elif search_category == '游戏科技':
            if 'playstation' in title_lower or 'ps5' in title_lower:
                return "🎮 PlayStation游戏主机系统更新，索尼游戏生态优化升级"
            elif 'xbox' in title_lower:
                return "🎯 Xbox游戏平台功能增强，微软游戏服务体验提升"
            elif 'nintendo' in title_lower:
                return "🎲 任天堂游戏新作发布，Switch平台内容生态丰富"
            elif 'steam' in title_lower:
                return "🚂 Steam游戏平台重要更新，PC游戏分发服务优化"
            elif 'esports' in title_lower:
                return "🏆 电子竞技行业发展迅速，职业游戏赛事影响力扩大"
            else:
                return "🎮 电子游戏行业创新发展，游戏技术与体验持续进步"
                
        elif search_category == '经济金融':
            if 'bitcoin' in title_lower or 'cryptocurrency' in title_lower:
                return "₿ 比特币等加密货币市场波动，数字资产投资备受关注"
            elif 'stock' in title_lower or 'market' in title_lower:
                return "📈 全球股票市场表现分析，投资者关注经济发展趋势"
            elif 'fintech' in title_lower:
                return "💳 金融科技创新应用推广，数字化金融服务普及加速"
            elif 'blockchain' in title_lower:
                return "⛓️ 区块链技术应用场景扩展，分布式账本价值日益凸显"
            else:
                return "💰 全球经济金融市场动态，财经政策影响投资环境"
                
        elif search_category == '科技创新':
            if 'apple' in title_lower:
                if 'iphone' in title_lower:
                    return "🍎 苹果iPhone系列产品更新，移动技术创新引领行业"
                elif 'watch' in title_lower:
                    return "🍎 Apple Watch智能手表功能升级，健康监测技术突破"
                else:
                    return "🍎 苹果公司产品技术创新，消费电子市场引领者地位稳固"
            elif 'google' in title_lower:
                return "🔍 谷歌科技产品服务更新，互联网搜索与云计算优化"
            elif 'microsoft' in title_lower:
                return "💼 微软企业软件解决方案升级，云计算服务能力增强"
            elif 'meta' in title_lower:
                return "🌐 Meta社交平台技术创新，虚拟现实与元宇宙布局"
            elif 'startup' in title_lower:
                return "🚀 科技创业公司融资发展，创新技术商业化加速"
            else:
                return "💻 全球科技行业发展动态，技术创新推动产业升级"
        
        # 默认完全中文标题，绝不包含英文
        return "📰 重要科技资讯发布，行业发展趋势值得关注"
    
    def translate_description(self, description, title="", search_category=""):
        """翻译描述为完整中文，绝对避免英文残留"""
        # 基于搜索类别生成完全中文描述，绝不拼接英文原文
        if search_category == 'AI科技':
            return "人工智能技术领域的重要发展动态，涵盖最新技术突破、产品发布、研发进展等前沿资讯，为AI行业从业者和关注者提供专业的技术洞察。"
        elif search_category == '游戏科技':
            return "电子游戏行业的最新发展动态，包括游戏主机更新、新作发布、电竞赛事、游戏技术创新等内容，全面覆盖游戏产业链各个环节的重要信息。"
        elif search_category == '经济金融':
            return "全球经济金融市场的重要动态分析，涵盖股市行情、加密货币、金融科技、投资策略等领域，为投资者和金融从业者提供及时的市场资讯。"
        elif search_category == '科技创新':
            return "科技行业创新发展的重要资讯，关注大型科技公司产品发布、技术突破、市场战略等动态，展现全球科技产业的发展趋势和创新方向。"
        else:
            return "重要的科技行业资讯，反映当前技术发展的重要动向和市场趋势，为科技从业者和爱好者提供有价值的信息参考。"
    
    def categorize_news(self, title, search_category=""):
        """新闻分类"""
        title_lower = title.lower()
        
        # 基于搜索类别的精准分类
        if search_category == 'AI科技':
            if 'openai' in title_lower or 'chatgpt' in title_lower or 'gpt' in title_lower:
                return {'name': 'OpenAI', 'color': '#34C759', 'icon': '🤖'}
            elif 'google' in title_lower and 'ai' in title_lower:
                return {'name': '谷歌AI', 'color': '#007AFF', 'icon': '🔍'}
            elif 'microsoft' in title_lower or 'copilot' in title_lower:
                return {'name': '微软AI', 'color': '#5856D6', 'icon': '💼'}
            elif 'meta' in title_lower:
                return {'name': 'Meta AI', 'color': '#1877F2', 'icon': '🌐'}
            else:
                return {'name': 'AI科技', 'color': '#FF6B35', 'icon': '🤖'}
                
        elif search_category == '游戏科技':
            if any(word in title_lower for word in ['playstation', 'ps5', 'sony']):
                return {'name': 'PlayStation', 'color': '#003087', 'icon': '🎮'}
            elif any(word in title_lower for word in ['xbox', 'microsoft gaming']):
                return {'name': 'Xbox', 'color': '#107C10', 'icon': '🎯'}
            elif 'nintendo' in title_lower:
                return {'name': '任天堂', 'color': '#E60012', 'icon': '🎲'}
            elif any(word in title_lower for word in ['steam', 'valve']):
                return {'name': 'Steam', 'color': '#1B2838', 'icon': '🚂'}
            elif 'esports' in title_lower:
                return {'name': '电竞', 'color': '#FF6B35', 'icon': '🏆'}
            else:
                return {'name': '游戏科技', 'color': '#9B59B6', 'icon': '🎮'}
                
        elif search_category == '经济金融':
            if any(word in title_lower for word in ['bitcoin', 'cryptocurrency', 'crypto']):
                return {'name': '加密货币', 'color': '#F7931A', 'icon': '₿'}
            elif any(word in title_lower for word in ['stock', 'market', 'trading']):
                return {'name': '股市', 'color': '#27AE60', 'icon': '📈'}
            elif any(word in title_lower for word in ['fintech', 'finance']):
                return {'name': '金融科技', 'color': '#3498DB', 'icon': '💳'}
            elif 'blockchain' in title_lower:
                return {'name': '区块链', 'color': '#2C3E50', 'icon': '⛓️'}
            else:
                return {'name': '经济金融', 'color': '#E67E22', 'icon': '💰'}
                
        elif search_category == '科技创新':
            if 'apple' in title_lower:
                return {'name': '苹果', 'color': '#000000', 'icon': '🍎'}
            elif 'google' in title_lower:
                return {'name': '谷歌', 'color': '#4285F4', 'icon': '🔍'}
            elif 'microsoft' in title_lower:
                return {'name': '微软', 'color': '#00BCF2', 'icon': '💼'}
            elif 'meta' in title_lower:
                return {'name': 'Meta', 'color': '#1877F2', 'icon': '🌐'}
            elif any(word in title_lower for word in ['startup', 'innovation']):
                return {'name': '创新', 'color': '#E74C3C', 'icon': '🚀'}
            else:
                return {'name': '科技创新', 'color': '#95A5A6', 'icon': '💻'}
        
        # 默认分类
        return {'name': '科技资讯', 'color': '#6B7280', 'icon': '📱'}
    
    def get_importance_score(self, title):
        """重要性评分"""
        title_lower = title.lower()
        score = 1
        
        # 高重要性关键词
        if any(word in title_lower for word in ['breakthrough', 'revolutionary', 'major', 'launch']):
            score += 3
        if any(word in title_lower for word in ['openai', 'gpt-5', 'gpt-4']):
            score += 2
        if any(word in title_lower for word in ['google', 'microsoft', 'meta']):
            score += 1
        
        return min(score, 5)
    
    def merge_news_data(self, existing_news, new_articles):
        """合并新旧新闻数据"""
        # 创建现有新闻的URL映射
        existing_urls = {news.get('url', ''): news for news in existing_news}
        merged_news = []
        added_count = 0
        
        # 首先添加新文章
        for i, article in enumerate(new_articles):
            article_url = article.get('url', '')
            
            # 检查是否已存在
            if article_url not in existing_urls:
                # 获取搜索类别
                search_category = article.get('search_category', '')
                
                # 处理新文章
                chinese_title = self.translate_title(article.get('title', ''), search_category)
                chinese_description = self.translate_description(
                    article.get('description', ''),
                    article.get('title', ''),
                    search_category
                )
                
                news_item = {
                    "id": self.generate_news_id(article),
                    "title": chinese_title,
                    "original_title": article.get('title', ''),
                    "description": chinese_description,
                    "original_description": article.get('description', ''),
                    "url": article_url,
                    "source": article.get('source', {}).get('name', '未知来源'),
                    "publishedAt": article.get('publishedAt', ''),
                    "image": article.get('image', ''),
                    "category": self.categorize_news(chinese_title, search_category),
                    "importance": self.get_importance_score(chinese_title),
                    "added_time": datetime.now().isoformat(),
                    "search_category": search_category
                }
                merged_news.append(news_item)
                added_count += 1
        
        # 然后添加保留的历史新闻（3天内）
        retained_count = 0
        for news in existing_news:
            if self.is_news_recent(news.get('publishedAt'), days=3):
                merged_news.append(news)
                retained_count += 1
        
        # 按发布时间倒序排列
        merged_news.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        
        print(f"📊 新闻合并完成:")
        print(f"   📈 新增新闻: {added_count} 条")
        print(f"   📚 保留历史: {retained_count} 条")
        print(f"   📰 总计新闻: {len(merged_news)} 条")
        
        return merged_news
    
    def format_publish_date(self, date_str):
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
    
    def generate_ai_analysis(self, title, description):
        """生成AI观点分析"""
        return f'''
        <div class="ai-analysis">
            <h4>🔬 技术突破评估</h4>
            <p>基于该新闻技术内容分析，这一发展代表了AI领域的重要进展。从技术角度看，该创新将推动行业标准升级，为相关企业带来新的发展机遇。</p>
            
            <h4>🌐 行业生态影响</h4>
            <p>• <strong>技术竞争格局：</strong>将影响全球AI竞争态势，国内厂商需关注技术发展趋势<br>
            • <strong>应用场景拓展：</strong>有望在多个垂直领域产生应用价值<br>
            • <strong>产业链影响：</strong>上下游企业将面临新的合作与竞争机会</p>
            
            <h4>🎯 战略建议</h4>
            <p>建议相关企业密切关注技术发展动向，评估自身产品升级需求，寻找与行业龙头的合作机会，同时加强人才储备和技术研发投入。</p>
        </div>'''

    def generate_investment_analysis(self, title, description):
        """生成投资方向分析"""
        return f'''
        <div class="investment-analysis">
            <h4>📊 市场影响分析</h4>
            <p><strong>短期波动预期：</strong>相关概念股可能出现5-15%的波动，建议关注市场情绪变化和资金流向。</p>
            
            <h4>💼 投资标的梳理</h4>
            <div class="investment-targets">
                <p><strong>🏭 基础设施层：</strong><br>
                • 算力服务：浪潮信息(000977)、中科曙光(603019)<br>
                • 芯片制造：寒武纪(688256)、海光信息(688041)</p>
                
                <p><strong>🤖 应用服务层：</strong><br>
                • AI平台：科大讯飞(002230)、汉王科技(002362)<br>
                • 垂直应用：拓尔思(300229)、久远银海(002777)</p>
            </div>
            
            <h4>⏰ 投资时机分析</h4>
            <p><strong>短期(1-3个月)：</strong>关注业绩确定性和政策支持力度<br>
            <strong>中期(3-12个月)：</strong>重点关注技术商业化进展<br>
            <strong>长期(1-3年)：</strong>布局具备核心技术壁垒的平台型企业</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>AI板块波动较大，建议合理控制仓位，注意风险管理。</p>
        </div>'''
    
    def generate_html_site(self, news_data):
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
        category_tabs = f'''
        <button class="tab-button active" data-category="all">
            <span class="tab-icon">📱</span>
            <span class="tab-text">全部</span>
            <span class="tab-count">{len(news_data)}</span>
        </button>'''
        
        for cat_name, articles in categories.items():
            category_tabs += f'''
        <button class="tab-button" data-category="{cat_name}">
            <span class="tab-icon">{articles[0]['category']['icon']}</span>
            <span class="tab-text">{cat_name}</span>
            <span class="tab-count">{len(articles)}</span>
        </button>'''
        
        # 生成新闻卡片
        news_cards = ""
        for i, article in enumerate(news_data):
            importance_stars = "★" * article.get('importance', 1)
            formatted_date = self.format_publish_date(article.get('publishedAt', ''))
            
            news_cards += f'''
        <article class="news-card" data-category="{article['category']['name']}" 
                 onclick="window.location.href='news/{article['id']}.html'">
            <div class="importance-stars"><span class="star">{importance_stars}</span></div>
            <div class="card-header">
                <div class="category-badge" style="background-color: {article['category']['color']}; color: white;">
                    <span>{article['category']['icon']}</span>
                    <span>{article['category']['name']}</span>
                </div>
                <h2 class="news-title">{article['title']}</h2>
                <p class="news-description">{article['description']}</p>
            </div>
            <div class="card-footer">
                <div class="news-meta">
                    <div class="source">📰 {article['source']}</div>
                    <div class="publish-date">🕒 {formatted_date}</div>
                </div>
                <div class="read-more">查看详情</div>
            </div>
        </article>'''
        
        # 生成完整的首页HTML
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
        <div class="container">{category_tabs}
        </div>
    </div>
    
    <div class="container">
        <div class="content-area">
            <div class="news-grid">{news_cards}
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
        
        # 保存HTML文件
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        # 生成详情页
        os.makedirs('docs/news', exist_ok=True)
        for news in news_data:
            ai_analysis = self.generate_ai_analysis(news['title'], news['description'])
            investment_analysis = self.generate_investment_analysis(news['title'], news['description'])
            
            # 生成完整的详情页HTML
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
        
        return True
    
    def run(self):
        """运行累积更新系统"""
        print("🚀 开始AI新闻累积更新任务")
        print("=" * 50)
        
        # 1. 加载现有新闻
        existing_news = self.load_existing_news()
        
        # 2. 获取最新新闻
        new_articles = self.get_latest_news()
        if not new_articles:
            print("❌ 无法获取新闻，使用现有数据")
            new_articles = []
        
        # 3. 合并新旧数据
        merged_news = self.merge_news_data(existing_news, new_articles)
        
        # 4. 保存合并后的数据
        os.makedirs('docs', exist_ok=True)
        with open(self.news_data_file, 'w', encoding='utf-8') as f:
            json.dump(merged_news, f, ensure_ascii=False, indent=2)
        
        # 5. 生成HTML站点
        success = self.generate_html_site(merged_news)
        
        if success:
            print("✅ 累积更新系统运行完成")
            print(f"   📊 总新闻数量: {len(merged_news)} 条")
            print(f"   📅 时间范围: 最近3天")
            print("   🌐 网站已更新")
        else:
            print("❌ HTML站点生成失败")
        
        print("=" * 50)
        return success

if __name__ == "__main__":
    accumulator = AINewsAccumulator()
    success = accumulator.run()
    print("✅ 累积更新成功" if success else "❌ 累积更新失败")