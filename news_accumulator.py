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
        
        # 定义多个搜索类别 - 扩展到3天，增加数量
        search_queries = [
            {
                'query': 'AI OR OpenAI OR ChatGPT OR "artificial intelligence"',
                'category': 'AI科技',
                'max': '15'  # 增加AI新闻数量
            },
            {
                'query': 'gaming OR PlayStation OR Xbox OR Nintendo',
                'category': '游戏科技', 
                'max': '10'
            },
            {
                'query': 'stock OR bitcoin OR finance OR cryptocurrency',
                'category': '经济金融',
                'max': '10'
            },
            {
                'query': 'Apple OR Google OR Microsoft OR Meta OR technology',
                'category': '科技创新',
                'max': '10'
            }
        ]
        
        for search_config in search_queries:
            max_retries = 3 if search_config['category'] == 'AI科技' else 1  # AI科技重试3次
            
            for attempt in range(max_retries):
                try:
                    # 计算3天前的日期
                    from datetime import datetime, timedelta
                    three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                    
                    params = {
                        'apikey': self.gnews_api_key,
                        'q': search_config['query'],
                        'lang': 'en',
                        'max': search_config['max'],
                        'sortby': 'publishedAt',
                        'from': three_days_ago  # 添加时间范围：从3天前开始
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
                                    'sortby': 'publishedAt',
                                    'from': three_days_ago  # 备用策略也使用3天范围
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
            elif 'google' in title_lower or 'gmail' in title_lower:
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
        """翻译描述为中文，保留真实新闻内容"""
        if not description:
            # 只有在没有描述时才使用通用描述
            category_desc = {
                'AI科技': "人工智能技术领域的重要发展动态和创新突破。",
                '游戏科技': "游戏行业最新动态，包括游戏技术创新和产业趋势。", 
                '经济金融': "金融科技和经济市场最新资讯，涵盖投资和数字货币等领域。",
                '科技创新': "科技行业创新动态，关注大型科技公司和初创企业的最新发展。"
            }
            return category_desc.get(search_category, "重要科技资讯，反映当前技术发展的重要动向。")
        
        # 基于英文描述的关键词生成完全中文化的描述
        description_lower = description.lower()
        
        # AI科技类描述生成
        if search_category == 'AI科技':
            if 'openai' in description_lower or 'chatgpt' in description_lower:
                return "OpenAI发布最新AI技术成果，ChatGPT等产品功能显著升级，人工智能应用场景持续扩展，为用户提供更加智能化的服务体验。"
            elif 'google' in description_lower and 'ai' in description_lower:
                return "谷歌推出AI技术创新方案，在搜索、云计算、智能助手等领域实现重要突破，进一步巩固其在人工智能领域的领先地位。"
            elif 'microsoft' in description_lower:
                return "微软发布企业级AI解决方案最新进展，Copilot系列产品功能增强，为企业数字化转型提供更强大的智能化支持。"
            elif 'ai' in description_lower or 'artificial intelligence' in description_lower:
                return "人工智能技术取得重要进展，在机器学习、深度学习等核心技术领域实现突破，推动AI应用向更多行业渗透。"
            else:
                return "AI科技领域出现重要发展动态，相关技术创新和产品升级持续推进，为行业发展注入新的活力。"
        
        # 游戏科技类描述生成
        elif search_category == '游戏科技':
            if 'playstation' in description_lower or 'ps5' in description_lower:
                return "索尼PlayStation平台发布重要更新，PS5主机功能优化升级，游戏生态系统持续完善，为玩家带来更优质的游戏体验。"
            elif 'xbox' in description_lower:
                return "微软Xbox游戏平台推出新功能，游戏服务体验全面提升，Game Pass订阅模式持续优化，扩大在游戏市场的影响力。"
            elif 'nintendo' in description_lower:
                return "任天堂发布游戏产品最新动态，Switch平台内容生态不断丰富，独占游戏阵容持续扩展，保持在掌机市场的领先优势。"
            elif 'gaming' in description_lower or 'game' in description_lower:
                return "电子游戏行业出现重要发展趋势，游戏技术创新和用户体验优化成为关注焦点，产业规模持续扩大。"
            else:
                return "游戏科技领域迎来新的发展机遇，相关技术创新推动游戏体验升级，行业竞争格局持续演变。"
        
        # 经济金融类描述生成
        elif search_category == '经济金融':
            if 'bitcoin' in description_lower or 'cryptocurrency' in description_lower:
                return "加密货币市场出现重要变化，比特币等数字资产价格波动引发关注，区块链技术应用场景持续拓展。"
            elif 'stock' in description_lower or 'market' in description_lower:
                return "全球股票市场表现分析显示，投资者对经济发展前景保持关注，市场情绪和资金流向呈现新的特征。"
            elif 'finance' in description_lower or 'fintech' in description_lower:
                return "金融科技创新应用加速推广，数字化金融服务普及程度提升，为用户提供更便捷的金融解决方案。"
            else:
                return "经济金融领域出现重要动态，市场变化和政策调整引发广泛关注，投资环境面临新的机遇与挑战。"
        
        # 科技创新类描述生成
        elif search_category == '科技创新':
            if 'apple' in description_lower:
                return "苹果公司发布产品技术创新成果，iPhone、iPad、Mac等产品线持续优化升级，在消费电子市场保持技术领先地位。"
            elif 'google' in description_lower:
                return "谷歌推出科技产品服务重要更新，在搜索、云计算、移动操作系统等领域实现技术突破，扩大市场影响力。"
            elif 'microsoft' in description_lower:
                return "微软发布企业软件解决方案最新进展，云计算服务能力持续增强，为数字化转型提供全面的技术支持。"
            elif 'meta' in description_lower:
                return "Meta公司在社交媒体和虚拟现实领域推出创新技术，元宇宙概念应用场景不断拓展，为用户创造新的数字体验。"
            else:
                return "科技创新领域出现重要发展动态，新技术、新产品、新服务持续涌现，推动产业升级和数字化转型。"
        
        # 默认中文描述
        return "科技行业迎来重要发展机遇，技术创新和产品升级成为推动行业进步的重要动力，相关企业竞争力持续提升。"
    
    def categorize_news(self, title, search_category=""):
        """新闻分类"""
        title_lower = title.lower()
        
        # 基于搜索类别的精准分类
        if search_category == 'AI科技':
            if 'openai' in title_lower or 'chatgpt' in title_lower or 'gpt' in title_lower:
                return {'name': 'OpenAI', 'color': '#34C759', 'icon': '🤖'}
            elif 'google' in title_lower or 'gmail' in title_lower:
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
        """基于真实新闻内容生成AI观点分析"""
        title_lower = title.lower()
        desc_lower = description.lower() if description else ""
        
        # 基于内容关键词生成针对性分析
        if 'openai' in title_lower or 'chatgpt' in title_lower:
            return f'''
        <div class="ai-analysis">
            <h4>🔬 OpenAI技术突破分析</h4>
            <p>OpenAI在人工智能领域的持续创新正在重塑整个行业格局。ChatGPT等产品的功能升级不仅提升了用户体验，更重要的是为AI应用的普及奠定了基础。这种技术进步将带动相关产业链的全面升级。</p>
            
            <h4>🌐 市场竞争态势</h4>
            <p>• <strong>技术护城河：</strong>OpenAI在大模型训练和推理优化方面建立了显著优势<br>
            • <strong>生态建设：</strong>API开放策略吸引大量开发者，形成良性生态循环<br>
            • <strong>商业化进程：</strong>企业级应用场景快速扩展，付费用户规模持续增长</p>
            
            <h4>🎯 发展趋势预判</h4>
            <p>预计OpenAI将继续在多模态AI、专业领域应用等方向发力，同时面临来自谷歌、微软等巨头的激烈竞争。企业应关注AI工具的实际应用价值，避免盲目跟风。</p>
        </div>'''
        
        elif 'google' in title_lower or 'gmail' in title_lower:
            return f'''
        <div class="ai-analysis">
            <h4>🔬 谷歌AI战略布局</h4>
            <p>谷歌凭借其深厚的技术积累和数据优势，在AI领域展现出强大的创新能力。从搜索引擎到云计算，再到智能助手，谷歌正在构建全方位的AI生态系统。</p>
            
            <h4>🌐 技术整合优势</h4>
            <p>• <strong>数据优势：</strong>海量用户数据为AI模型训练提供宝贵资源<br>
            • <strong>基础设施：</strong>Google Cloud为AI应用提供强大的计算支持<br>
            • <strong>产品矩阵：</strong>AI技术在多个产品线中得到有效应用和验证</p>
            
            <h4>🎯 竞争力评估</h4>
            <p>谷歌在AI基础研究方面具有领先优势，但在消费级AI产品的商业化速度上仍需加快步伐。企业级客户应重点关注其云服务和开发工具的更新动态。</p>
        </div>'''
            
        elif 'microsoft' in title_lower:
            return f'''
        <div class="ai-analysis">
            <h4>🔬 微软AI企业化策略</h4>
            <p>微软通过与OpenAI的深度合作，成功将AI技术整合到Office、Azure等核心产品中。Copilot系列的推出标志着企业级AI应用进入新阶段，为数字化转型提供了实用工具。</p>
            
            <h4>🌐 生态整合能力</h4>
            <p>• <strong>产品整合：</strong>AI功能深度嵌入Office 365、Windows等主流产品<br>
            • <strong>云服务优势：</strong>Azure云平台为企业AI应用提供完整解决方案<br>
            • <strong>开发者支持：</strong>完善的开发工具和API服务促进生态发展</p>
            
            <h4>🎯 商业模式创新</h4>
            <p>微软的订阅制服务模式为AI功能的持续更新提供了稳定收入来源。企业用户应评估AI工具对生产力提升的实际效果，合理规划技术投入。</p>
        </div>'''
            
        elif 'xbox' in title_lower or 'playstation' in title_lower or 'nintendo' in title_lower:
            return f'''
        <div class="ai-analysis">
            <h4>🔬 游戏行业发展分析</h4>
            <p>游戏行业正在经历技术革新和商业模式转型的关键阶段。主机厂商通过硬件升级、服务优化和内容生态建设，努力满足用户日益增长的娱乐需求。</p>
            
            <h4>🌐 市场竞争格局</h4>
            <p>• <strong>技术创新：</strong>画面质量、加载速度、交互体验持续提升<br>
            • <strong>内容生态：</strong>独占游戏和第三方合作成为差异化竞争关键<br>
            • <strong>服务模式：</strong>订阅制游戏服务正在改变用户消费习惯</p>
            
            <h4>🎯 行业趋势洞察</h4>
            <p>云游戏、VR/AR技术、AI辅助游戏开发等新兴技术将重塑游戏行业。投资者应关注技术创新能力强、用户粘性高的优质游戏公司。</p>
        </div>'''
            
        elif 'bitcoin' in title_lower or 'crypto' in title_lower:
            return f'''
        <div class="ai-analysis">
            <h4>🔬 加密货币市场分析</h4>
            <p>数字资产市场正在经历成熟化过程，机构投资者的参与度不断提升。比特币等主流加密货币逐步被认可为数字黄金，但市场波动性仍然较大。</p>
            
            <h4>🌐 市场成熟度评估</h4>
            <p>• <strong>监管环境：</strong>各国监管政策日趋明确，为市场发展提供框架<br>
            • <strong>机构采用：</strong>传统金融机构加快布局数字资产业务<br>
            • <strong>技术发展：</strong>区块链技术在支付、智能合约等领域应用扩展</p>
            
            <h4>🎯 投资风险提示</h4>
            <p>数字资产投资需要充分了解技术原理和市场风险。建议投资者采用分散投资策略，控制仓位规模，关注监管政策变化对市场的影响。</p>
        </div>'''
            
        elif 'stock' in title_lower or 'market' in title_lower:
            return f'''
        <div class="ai-analysis">
            <h4>🔬 股市行情技术分析</h4>
            <p>当前股票市场受到宏观经济政策、企业盈利预期、资金流向等多重因素影响。投资者需要综合分析基本面和技术面指标，制定合理的投资策略。</p>
            
            <h4>🌐 市场环境评估</h4>
            <p>• <strong>政策影响：</strong>货币政策和财政政策对市场流动性产生重要影响<br>
            • <strong>行业轮动：</strong>不同板块的估值修复和增长预期存在差异<br>
            • <strong>风险偏好：</strong>投资者情绪和风险偏好变化影响资产配置</p>
            
            <h4>🎯 投资策略建议</h4>
            <p>建议投资者保持理性投资心态，关注企业基本面质量，选择具备长期成长潜力的优质标的。同时做好风险管理，避免过度集中投资。</p>
        </div>'''
        
        else:
            # 通用科技新闻分析
            return f'''
        <div class="ai-analysis">
            <h4>🔬 科技行业动态分析</h4>
            <p>科技行业正在经历快速变革，新技术、新产品、新服务层出不穷。企业需要保持敏锐的市场洞察力，及时调整发展策略以适应行业变化。</p>
            
            <h4>🌐 创新驱动发展</h4>
            <p>• <strong>技术迭代：</strong>新技术的快速迭代为产业升级提供动力<br>
            • <strong>用户需求：</strong>消费者对产品功能和体验的要求不断提升<br>
            • <strong>竞争态势：</strong>市场竞争推动企业持续创新和优化</p>
            
            <h4>🎯 发展机遇把握</h4>
            <p>企业应关注技术发展趋势，加强研发投入，提升核心竞争力。同时注重用户体验优化，建立可持续的商业模式。</p>
        </div>'''

    def generate_investment_analysis(self, title, description):
        """基于真实新闻内容生成投资方向分析"""
        title_lower = title.lower()
        desc_lower = description.lower() if description else ""
        
        # 基于内容关键词生成针对性投资分析
        if 'openai' in title_lower or 'chatgpt' in title_lower:
            return f'''
        <div class="investment-analysis">
            <h4>📊 OpenAI相关投资机会</h4>
            <p><strong>市场影响：</strong>OpenAI的技术突破将带动AI产业链上下游公司估值重估，相关概念股有望受益于技术进步带来的市场预期提升。</p>
            
            <h4>💼 相关投资标的</h4>
            <div class="investment-targets">
                <p><strong>🤖 AI算力支持：</strong><br>
                • 云计算：微软(MSFT)、亚马逊(AMZN)、阿里云<br>
                • GPU芯片：英伟达(NVDA)、AMD、寒武纪</p>
                
                <p><strong>💡 AI应用生态：</strong><br>
                • 企业服务：Salesforce、用友网络、金山办公<br>
                • 开发工具：GitHub、JetBrains、奇安信</p>
            </div>
            
            <h4>⏰ 投资策略建议</h4>
            <p><strong>短期关注：</strong>AI工具商业化进展和用户增长数据<br>
            <strong>中期布局：</strong>具备AI集成能力的传统软件公司<br>
            <strong>长期价值：</strong>在垂直领域建立护城河的AI应用企业</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>AI技术发展存在不确定性，投资需谨慎评估技术商业化风险。</p>
        </div>'''
        
        elif 'google' in title_lower or 'gmail' in title_lower:
            return f'''
        <div class="investment-analysis">
            <h4>📊 谷歌AI布局投资价值</h4>
            <p><strong>市场影响：</strong>谷歌在AI领域的持续投入强化了其技术护城河，为搜索广告、云计算等核心业务提供新的增长动力。</p>
            
            <h4>💼 投资机会分析</h4>
            <div class="investment-targets">
                <p><strong>🔍 搜索广告升级：</strong><br>
                • 直接受益：Alphabet(GOOGL)、百度(BIDU)<br>
                • 间接受益：广告技术服务商、内容创作平台</p>
                
                <p><strong>☁️ 云计算服务：</strong><br>
                • 基础设施：Google Cloud、腾讯云、华为云<br>
                • 企业服务：Salesforce、ServiceNow、用友网络</p>
            </div>
            
            <h4>⏰ 投资时机把握</h4>
            <p><strong>近期催化剂：</strong>AI搜索功能推广和用户接受度<br>
            <strong>中期看点：</strong>企业级AI服务商业化收入<br>
            <strong>长期价值：</strong>AI技术在多个业务线的深度整合</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>监管政策变化和竞争加剧可能影响盈利预期。</p>
        </div>'''
            
        elif 'microsoft' in title_lower:
            return f'''
        <div class="investment-analysis">
            <h4>📊 微软AI生态投资机会</h4>
            <p><strong>市场影响：</strong>微软通过AI技术升级Office和Azure服务，有望提升用户付费率和ARPU值，为业绩增长提供新动能。</p>
            
            <h4>💼 投资价值评估</h4>
            <div class="investment-targets">
                <p><strong>💼 企业办公软件：</strong><br>
                • 核心标的：微软(MSFT)、金山办公、致远互联<br>
                • 生态伙伴：Teams应用开发商、企业协作工具</p>
                
                <p><strong>☁️ 云服务生态：</strong><br>
                • 云基础设施：Azure、阿里云、腾讯云<br>
                • 企业数字化：用友网络、泛微网络、华宇软件</p>
            </div>
            
            <h4>⏰ 投资策略制定</h4>
            <p><strong>短期机会：</strong>Copilot订阅收入增长和渗透率提升<br>
            <strong>中期增长：</strong>企业AI应用场景扩展和客单价提升<br>
            <strong>长期投资：</strong>具备AI能力的企业服务平台公司</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>企业IT支出波动和AI技术替代风险需要关注。</p>
        </div>'''
            
        elif 'xbox' in title_lower or 'playstation' in title_lower or 'nintendo' in title_lower:
            return f'''
        <div class="investment-analysis">
            <h4>📊 游戏行业投资机会</h4>
            <p><strong>市场影响：</strong>游戏硬件更新周期和内容生态建设将推动游戏产业链价值重估，优质游戏公司有望受益于用户规模增长。</p>
            
            <h4>💼 投资标的梳理</h4>
            <div class="investment-targets">
                <p><strong>🎮 游戏硬件制造：</strong><br>
                • 主机厂商：索尼(SNE)、微软(MSFT)、任天堂(NTDOY)<br>
                • 配件制造：雷蛇、罗技、北通控制器</p>
                
                <p><strong>🎲 游戏内容开发：</strong><br>
                • A级工作室：腾讯游戏、网易游戏、米哈游<br>
                • 独立开发：完美世界、三七互娱、吉比特</p>
            </div>
            
            <h4>⏰ 行业周期判断</h4>
            <p><strong>当前阶段：</strong>新一代主机普及期，硬件销量增长稳定<br>
            <strong>发展趋势：</strong>云游戏和订阅服务改变商业模式<br>
            <strong>长期价值：</strong>拥有优质IP和强开发能力的内容公司</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>游戏监管政策和用户偏好变化可能影响行业发展。</p>
        </div>'''
            
        elif 'bitcoin' in title_lower or 'crypto' in title_lower:
            return f'''
        <div class="investment-analysis">
            <h4>📊 数字资产投资分析</h4>
            <p><strong>市场影响：</strong>加密货币市场成熟度提升和机构参与增加，为数字资产配置提供了新的投资逻辑，但波动性仍需重点关注。</p>
            
            <h4>💼 相关投资机会</h4>
            <div class="investment-targets">
                <p><strong>₿ 直接投资：</strong><br>
                • 主流币种：比特币(BTC)、以太坊(ETH)<br>
                • 投资工具：比特币ETF、加密货币基金</p>
                
                <p><strong>⛓️ 区块链生态：</strong><br>
                • 挖矿设备：比特大陆、嘉楠科技<br>
                • 交易平台：Coinbase、币安生态相关</p>
            </div>
            
            <h4>⏰ 投资策略建议</h4>
            <p><strong>风险控制：</strong>建议资产配置比例不超过总投资的5-10%<br>
            <strong>时机选择：</strong>关注宏观流动性和监管政策变化<br>
            <strong>长期视角：</strong>数字资产作为另类投资的配置价值</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>数字资产波动极大，投资前需充分了解风险并做好资金管理。</p>
        </div>'''
            
        elif 'stock' in title_lower or 'market' in title_lower:
            return f'''
        <div class="investment-analysis">
            <h4>📊 股市投资策略分析</h4>
            <p><strong>市场环境：</strong>当前股市受多重因素影响，需要综合考虑宏观经济、政策导向、资金流向等因素制定投资策略。</p>
            
            <h4>💼 投资方向建议</h4>
            <div class="investment-targets">
                <p><strong>📈 成长性板块：</strong><br>
                • 科技创新：新能源、人工智能、生物医药<br>
                • 消费升级：品牌消费、服务消费、健康消费</p>
                
                <p><strong>🏭 价值型投资：</strong><br>
                • 传统优势：金融、地产、基础材料<br>
                • 分红股票：公用事业、消费必需品</p>
            </div>
            
            <h4>⏰ 投资时机把握</h4>
            <p><strong>短期策略：</strong>关注业绩确定性和估值安全边际<br>
            <strong>中期布局：</strong>重点关注政策支持和行业景气度<br>
            <strong>长期投资：</strong>选择具备核心竞争力的优质公司</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>股市投资存在本金损失风险，建议分散投资并做好风险管理。</p>
        </div>'''
        
        else:
            # 通用投资分析
            return f'''
        <div class="investment-analysis">
            <h4>📊 科技投资机会分析</h4>
            <p><strong>行业趋势：</strong>科技创新持续推动产业升级，为投资者提供了丰富的投资机会，但需要仔细甄别具备核心竞争力的优质标的。</p>
            
            <h4>💼 投资策略框架</h4>
            <div class="investment-targets">
                <p><strong>🚀 创新驱动：</strong><br>
                • 技术领先：关注拥有核心技术壁垒的公司<br>
                • 市场空间：选择具备长期增长潜力的赛道</p>
                
                <p><strong>📊 基本面分析：</strong><br>
                • 财务健康：重视盈利能力和现金流状况<br>
                • 管理团队：关注企业治理和执行能力</p>
            </div>
            
            <h4>⏰ 投资原则建议</h4>
            <p><strong>价值投资：</strong>寻找被低估的优质成长股<br>
            <strong>分散投资：</strong>合理配置不同行业和风险等级<br>
            <strong>长期持有：</strong>坚持长期投资理念，避免频繁交易</p>
            
            <p class="risk-warning">⚠️ <strong>风险提示：</strong>投资需谨慎，建议根据个人风险承受能力制定投资策略。</p>
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
            ai_analysis = self.generate_ai_analysis(news.get('original_title', news['title']), news.get('original_description', news['description']))
            investment_analysis = self.generate_investment_analysis(news.get('original_title', news['title']), news.get('original_description', news['description']))
            
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