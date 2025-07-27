#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版AI新闻累积更新系统 - 集成硅基流动智能翻译
"""

import os
import json
import urllib.request
import urllib.parse
import time
import hashlib
from datetime import datetime, timedelta

# 尝试导入dotenv，如果失败则继续（GitHub Actions中环境变量已设置）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv未安装，使用系统环境变量")

# 导入翻译服务
try:
    from translation.services.siliconflow_translator import SiliconFlowTranslator
except ImportError:
    print("翻译服务模块未找到，将使用基础功能")
    SiliconFlowTranslator = None

class EnhancedAINewsAccumulator:
    def __init__(self):
        # API配置 - 从环境变量获取
        self.gnews_api_key = os.getenv('GNEWS_API_KEY')
        if not self.gnews_api_key:
            raise ValueError("GNEWS_API_KEY环境变量未设置")
        
        self.gnews_base_url = "https://gnews.io/api/v4"
        self.news_data_file = 'docs/enhanced_news_data.json'
        
        # 初始化硅基流动翻译器
        self.siliconflow_api_key = os.getenv('SILICONFLOW_API_KEY')
        self.translator = None
        self._init_translator()
        
    def _init_translator(self):
        """初始化翻译器"""
        if SiliconFlowTranslator and self.siliconflow_api_key:
            try:
                self.translator = SiliconFlowTranslator(
                    api_key=self.siliconflow_api_key,
                    model="Qwen/Qwen2.5-7B-Instruct"  # 使用性价比最高的模型
                )
                print("✅ 硅基流动翻译器初始化成功")
            except Exception as e:
                print(f"⚠️ 翻译器初始化失败: {e}")
                self.translator = None
        else:
            print("⚠️ 翻译服务不可用，将使用原始新闻内容")
    
    
    def get_latest_news(self):
        """获取最新科技、游戏、经济新闻"""
        all_articles = []
        
        # 定义多个搜索类别
        search_queries = [
            {
                'query': 'AI OR OpenAI OR ChatGPT OR "artificial intelligence"',
                'category': 'AI科技',
                'max': '15'
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
            max_retries = 3 if search_config['category'] == 'AI科技' else 1
            
            for attempt in range(max_retries):
                try:
                    # 计算3天前的日期
                    three_days_ago = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
                    
                    params = {
                        'apikey': self.gnews_api_key,
                        'q': search_config['query'],
                        'lang': 'en',
                        'max': search_config['max'],
                        'sortby': 'publishedAt',
                        'from': three_days_ago
                    }
                    
                    query_string = urllib.parse.urlencode(params)
                    url = f"{self.gnews_base_url}/search?{query_string}"
                    
                    with urllib.request.urlopen(url, timeout=20) as response:
                        result = json.loads(response.read().decode('utf-8'))
                    
                    articles = result.get('articles', [])
                    # 为每篇文章添加搜索类别标记
                    for article in articles:
                        article['search_category'] = search_config['category']
                    
                    all_articles.extend(articles)
                    print(f"✅ {search_config['category']}获取 {len(articles)} 条新闻")
                    break
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ {search_config['category']}第{attempt+1}次尝试失败，重试中...")
                        time.sleep(2)
                        continue
                    else:
                        print(f"❌ 获取{search_config['category']}新闻失败: {str(e)}")
        
        print(f"✅ 总共获取 {len(all_articles)} 条最新新闻")
        return all_articles
    
    def translate_article(self, article):
        """翻译单篇文章"""
        if not self.translator:
            return article
        
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            
            # 翻译标题
            translated_title = ""
            title_confidence = 0.0
            if title:
                title_result = self.translator.translate_text(title, "en", "zh")
                if not title_result.error_message:
                    translated_title = title_result.translated_text
                    title_confidence = title_result.confidence_score
                else:
                    print(f"⚠️ 标题翻译失败: {title_result.error_message}")
            
            # 翻译描述
            translated_description = ""
            desc_confidence = 0.0
            if description:
                desc_result = self.translator.translate_text(description, "en", "zh")
                if not desc_result.error_message:
                    translated_description = desc_result.translated_text
                    desc_confidence = desc_result.confidence_score
                else:
                    print(f"⚠️ 描述翻译失败: {desc_result.error_message}")
            
            # 添加翻译信息到文章
            article['ai_translation'] = {
                'translated_title': translated_title,
                'translated_description': translated_description,
                'translation_confidence': {
                    'title': title_confidence,
                    'description': desc_confidence
                },
                'translation_service': self.translator.get_service_name(),
                'translation_time': datetime.now().isoformat(),
                'original_title': title,
                'original_description': description
            }
            
            return article
            
        except Exception as e:
            print(f"❌ 文章翻译异常: {str(e)}")
            return article
    
    def translate_articles_batch(self, articles):
        """批量翻译文章"""
        if not self.translator or not articles:
            return articles
        
        print(f"🔄 开始批量翻译 {len(articles)} 篇文章...")
        
        try:
            # 提取标题和描述
            titles = [article.get('title', '') for article in articles]
            descriptions = [article.get('description', '') for article in articles]
            
            # 过滤空内容
            valid_titles = [t for t in titles if t.strip()]
            valid_descriptions = [d for d in descriptions if d.strip()]
            
            translated_titles = []
            translated_descriptions = []
            
            # 批量翻译标题
            if valid_titles:
                print("📝 翻译标题中...")
                title_results = self.translator.translate_batch(valid_titles, "en", "zh")
                translated_titles = title_results
            
            # 批量翻译描述
            if valid_descriptions:
                print("📄 翻译描述中...")
                desc_results = self.translator.translate_batch(valid_descriptions, "en", "zh")
                translated_descriptions = desc_results
            
            # 将翻译结果添加到文章中
            title_idx = 0
            desc_idx = 0
            
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                
                # 处理标题翻译
                translated_title = ""
                title_confidence = 0.0
                if title.strip() and title_idx < len(translated_titles):
                    title_result = translated_titles[title_idx]
                    if not title_result.error_message:
                        translated_title = title_result.translated_text
                        title_confidence = title_result.confidence_score
                    title_idx += 1
                
                # 处理描述翻译
                translated_description = ""
                desc_confidence = 0.0
                if description.strip() and desc_idx < len(translated_descriptions):
                    desc_result = translated_descriptions[desc_idx]
                    if not desc_result.error_message:
                        translated_description = desc_result.translated_text
                        desc_confidence = desc_result.confidence_score
                    desc_idx += 1
                
                # 添加翻译信息
                article['ai_translation'] = {
                    'translated_title': translated_title,
                    'translated_description': translated_description,
                    'translation_confidence': {
                        'title': title_confidence,
                        'description': desc_confidence
                    },
                    'translation_service': self.translator.get_service_name(),
                    'translation_time': datetime.now().isoformat(),
                    'original_title': title,
                    'original_description': description
                }
            
            print(f"✅ 批量翻译完成")
            return articles
            
        except Exception as e:
            print(f"❌ 批量翻译失败，回退到单个翻译: {str(e)}")
            # 回退到单个翻译
            return [self.translate_article(article) for article in articles]
    
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
        content = f"{article.get('url', '')}{article.get('title', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def is_news_recent(self, publish_date, days=3):
        """检查新闻是否在指定天数内"""
        try:
            if not publish_date:
                return False
            
            if 'T' in publish_date:
                news_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
            else:
                news_date = datetime.fromisoformat(publish_date)
            
            now = datetime.now().replace(tzinfo=news_date.tzinfo) if news_date.tzinfo else datetime.now()
            time_diff = now - news_date
            
            return time_diff.days <= days
        except:
            return False
    
    def categorize_news(self, title, search_category=""):
        """新闻分类"""
        title_lower = title.lower()
        
        if search_category == 'AI科技':
            if 'openai' in title_lower or 'chatgpt' in title_lower:
                return {'name': 'OpenAI', 'color': '#34C759', 'icon': '🤖'}
            elif 'google' in title_lower:
                return {'name': '谷歌AI', 'color': '#007AFF', 'icon': '🔍'}
            elif 'microsoft' in title_lower:
                return {'name': '微软AI', 'color': '#5856D6', 'icon': '💼'}
            else:
                return {'name': 'AI科技', 'color': '#FF6B35', 'icon': '🤖'}
        elif search_category == '游戏科技':
            return {'name': '游戏科技', 'color': '#9B59B6', 'icon': '🎮'}
        elif search_category == '经济金融':
            return {'name': '经济金融', 'color': '#E67E22', 'icon': '💰'}
        else:
            return {'name': '科技资讯', 'color': '#6B7280', 'icon': '📱'}
    
    def get_importance_score(self, title):
        """重要性评分"""
        title_lower = title.lower()
        score = 1
        
        if any(word in title_lower for word in ['breakthrough', 'revolutionary', 'major', 'launch']):
            score += 3
        if any(word in title_lower for word in ['openai', 'gpt-5', 'gpt-4']):
            score += 2
        if any(word in title_lower for word in ['google', 'microsoft', 'meta']):
            score += 1
        
        return min(score, 5)
    
    def merge_news_data(self, existing_news, new_articles):
        """合并新旧新闻数据"""
        existing_urls = {news.get('url', ''): news for news in existing_news}
        merged_news = []
        added_count = 0
        
        # 首先添加新文章（带翻译）
        for article in new_articles:
            article_url = article.get('url', '')
            
            if article_url not in existing_urls:
                search_category = article.get('search_category', '')
                
                # 使用AI翻译的标题和描述（如果有的话）
                ai_translation = article.get('ai_translation', {})
                chinese_title = ai_translation.get('translated_title', '') or article.get('title', '')
                chinese_description = ai_translation.get('translated_description', '') or article.get('description', '')
                
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
                    "search_category": search_category,
                    "ai_translation": ai_translation  # 保存完整的翻译信息
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
    
    def save_news_data(self, news_data):
        """保存新闻数据"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.news_data_file), exist_ok=True)
            
            with open(self.news_data_file, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 新闻数据已保存到: {self.news_data_file}")
            
        except Exception as e:
            print(f"❌ 保存新闻数据失败: {str(e)}")
    
    def run_update(self):
        """运行新闻更新流程"""
        print("🚀 启动增强版AI新闻累积更新系统")
        print("=" * 60)
        
        try:
            # 1. 获取最新新闻
            print("\n📡 获取最新新闻...")
            new_articles = self.get_latest_news()
            
            if not new_articles:
                print("⚠️ 没有获取到新闻，退出更新")
                return
            
            # 2. 批量翻译新闻
            print(f"\n🔤 开始翻译 {len(new_articles)} 条新闻...")
            if self.translator:
                translated_articles = self.translate_articles_batch(new_articles)
                
                # 统计翻译成功率
                success_count = sum(1 for article in translated_articles 
                                  if article.get('ai_translation', {}).get('translated_title'))
                print(f"✅ 翻译成功: {success_count}/{len(new_articles)} 条")
            else:
                print("⚠️ 翻译器不可用，跳过翻译步骤")
                translated_articles = new_articles
            
            # 3. 加载现有新闻
            print("\n📚 加载现有新闻数据...")
            existing_news = self.load_existing_news()
            
            # 4. 合并新闻数据
            print("\n🔄 合并新闻数据...")
            merged_news = self.merge_news_data(existing_news, translated_articles)
            
            # 5. 保存新闻数据
            print("\n💾 保存新闻数据...")
            self.save_news_data(merged_news)
            
            print(f"\n{'='*60}")
            print("🎉 新闻更新完成！")
            print(f"📊 最终统计: {len(merged_news)} 条新闻")
            
            # 显示翻译统计
            if self.translator:
                translated_count = sum(1 for news in merged_news 
                                     if news.get('ai_translation', {}).get('translated_title'))
                print(f"🔤 翻译覆盖: {translated_count} 条新闻包含AI翻译")
            
        except Exception as e:
            print(f"❌ 新闻更新失败: {str(e)}")


def main():
    """主函数"""
    accumulator = EnhancedAINewsAccumulator()
    accumulator.run_update()


if __name__ == "__main__":
    main()