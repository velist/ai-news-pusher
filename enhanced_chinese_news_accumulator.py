#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文用户体验增强版AI新闻累积系统
集成时区转换、中文本地化、新鲜度管理和AI点评功能
"""

import os
import json
import urllib.request
import urllib.parse
import time
import hashlib
from datetime import datetime, timedelta
from translation.services.siliconflow_translator import SiliconFlowTranslator
from localization.timezone_converter import TimezoneConverter
from localization.chinese_localizer import ChineseLocalizer
from localization.news_freshness_manager import NewsFreshnessManager
from localization.ai_commentary import AICommentary

class EnhancedChineseNewsAccumulator:
    def __init__(self):
        # API配置
        self.gnews_api_key = os.getenv('GNEWS_API_KEY', 'c3cb6fef0f86251ada2b515017b97143')
        self.gnews_base_url = "https://gnews.io/api/v4"
        self.news_data_file = 'docs/enhanced_chinese_news_data.json'
        
        # 初始化各个组件
        self.siliconflow_api_key = "sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa"
        self.translator = None
        self.timezone_converter = TimezoneConverter()
        self.chinese_localizer = ChineseLocalizer()
        self.freshness_manager = NewsFreshnessManager()
        self.ai_commentary = AICommentary(self.siliconflow_api_key)
        
        self._init_translator()
        
    def _init_translator(self):
        """初始化翻译器"""
        try:
            self.translator = SiliconFlowTranslator(
                api_key=self.siliconflow_api_key,
                model="Qwen/Qwen2.5-7B-Instruct"
            )
            print("✅ 硅基流动翻译器初始化成功")
        except Exception as e:
            print(f"⚠️ 翻译器初始化失败: {e}")
            self.translator = None
    
    def get_latest_news(self):
        """获取最新科技、游戏、经济新闻"""
        all_articles = []
        
        # 定义多个搜索类别
        search_queries = [
            {
                'query': 'AI OR OpenAI OR ChatGPT OR "artificial intelligence"',
                'category': 'technology',
                'category_chinese': 'AI科技',
                'max': '15'
            },
            {
                'query': 'gaming OR PlayStation OR Xbox OR Nintendo',
                'category': 'gaming', 
                'category_chinese': '游戏资讯',
                'max': '10'
            },
            {
                'query': 'stock OR bitcoin OR finance OR cryptocurrency',
                'category': 'business',
                'category_chinese': '经济新闻',
                'max': '10'
            },
            {
                'query': 'Apple OR Google OR Microsoft OR Meta OR technology',
                'category': 'technology',
                'category_chinese': '科技创新',
                'max': '10'
            }
        ]
        
        for search_config in search_queries:
            max_retries = 3 if search_config['category'] == 'technology' else 1
            
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
                    
                    # 为每篇文章添加分类信息
                    for article in articles:
                        article['category'] = search_config['category']
                        article['category_chinese'] = search_config['category_chinese']
                    
                    all_articles.extend(articles)
                    print(f"✅ {search_config['category_chinese']}获取 {len(articles)} 条新闻")
                    break
                    
                except Exception as e:
                    print(f"⚠️ 获取{search_config['category_chinese']}新闻失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
        
        return all_articles
    
    def process_news_with_localization(self, articles):
        """处理新闻并添加本地化信息"""
        processed_articles = []
        
        print(f"🔄 开始处理 {len(articles)} 条新闻...")
        
        for i, article in enumerate(articles, 1):
            try:
                print(f"📰 处理第 {i}/{len(articles)} 条新闻: {article.get('title', '无标题')[:50]}...")
                
                # 1. 时区转换和时间本地化
                published_time = article.get('publishedAt')
                if published_time:
                    time_info = self.timezone_converter.format_news_time(published_time)
                    article['time_info'] = time_info
                    article['beijing_time'] = time_info['beijing_time'].isoformat() if time_info['beijing_time'] else None
                
                # 2. 翻译处理
                if self.translator:
                    translation_result = self._translate_article(article)
                    if translation_result:
                        article['ai_translation'] = translation_result
                
                # 3. 中文本地化处理
                localized_summary = self.chinese_localizer.format_news_summary(article)
                article['localized_summary'] = localized_summary
                
                # 4. 新鲜度评分
                freshness_score = self.freshness_manager.calculate_freshness_score(article)
                article['freshness_score'] = freshness_score
                
                # 5. 生成AI点评（仅对新鲜新闻）
                if freshness_score > 0.7:  # 只对新鲜度高的新闻生成点评
                    commentary_result = self.ai_commentary.generate_commentary(
                        article.get('title', ''),
                        article.get('content', ''),
                        article.get('description', '')
                    )
                    article['ai_commentary'] = commentary_result
                
                # 6. 生成唯一ID
                article['id'] = self._generate_article_id(article)
                
                processed_articles.append(article)
                
            except Exception as e:
                print(f"❌ 处理新闻失败: {e}")
                continue
        
        return processed_articles
    
    def _translate_article(self, article):
        """翻译文章内容"""
        try:
            title = article.get('title', '')
            description = article.get('description', '')
            
            if not title:
                return None
            
            # 翻译标题
            title_result = self.translator.translate_text(title, 'en', 'zh')
            if title_result.error_message:
                print(f"⚠️ 标题翻译失败: {title_result.error_message}")
                return None
            
            translation_info = {
                'translated_title': title_result.translated_text,
                'translation_service': f"siliconflow_{self.translator.model}",
                'translation_confidence': {
                    'title': title_result.confidence_score
                }
            }
            
            # 翻译描述（如果存在）
            if description:
                desc_result = self.translator.translate_text(description, 'en', 'zh')
                if not desc_result.error_message:
                    translation_info['translated_description'] = desc_result.translated_text
                    translation_info['translation_confidence']['description'] = desc_result.confidence_score
            
            return translation_info
            
        except Exception as e:
            print(f"⚠️ 翻译处理失败: {e}")
            return None
    
    def _generate_article_id(self, article):
        """生成文章唯一ID"""
        content = f"{article.get('title', '')}{article.get('url', '')}{article.get('publishedAt', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
    
    def filter_and_sort_news(self, articles):
        """过滤和排序新闻"""
        print("🔄 过滤和排序新闻...")
        
        # 1. 过滤新鲜新闻（72小时内）
        fresh_articles = self.freshness_manager.filter_fresh_news(articles, hours=72)
        print(f"📊 过滤后新鲜新闻: {len(fresh_articles)} 条")
        
        # 2. 按新鲜度排序
        sorted_articles = self.freshness_manager.sort_by_freshness(fresh_articles)
        print(f"📊 排序完成，最高评分: {sorted_articles[0]['freshness_score']:.3f}" if sorted_articles else "📊 无新闻可排序")
        
        # 3. 限制数量（保留前50条）
        final_articles = sorted_articles[:50]
        
        return final_articles
    
    def generate_html_page(self, articles):
        """生成HTML页面"""
        print("🌐 生成HTML页面...")
        
        # 获取更新状态
        update_status = self.freshness_manager.get_update_status()
        
        # 按新鲜度分类新闻
        categorized_news = self.freshness_manager.categorize_by_freshness(articles)
        
        # 生成HTML内容
        html_content = self._generate_html_template(articles, update_status, categorized_news)
        
        # 写入HTML文件
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML页面已生成: docs/index.html")
    
    def _generate_html_template(self, articles, update_status, categorized_news):
        """生成HTML模板"""
        # 这里是简化版本，实际应该使用完整的HTML模板
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 中文智能新闻</title>
    <style>
        body {{
            font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #007AFF;
            padding-bottom: 20px;
        }}
        .update-time {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        .news-item {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: #fafafa;
        }}
        .news-title {{
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        .news-meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .news-description {{
            color: #555;
            margin-bottom: 15px;
        }}
        .ai-commentary {{
            background: #e8f4fd;
            border-left: 4px solid #007AFF;
            padding: 15px;
            margin-top: 15px;
            border-radius: 4px;
        }}
        .freshness-score {{
            display: inline-block;
            background: #10B981;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p>智能翻译 · 中文本地化 · 实时更新</p>
            <div class="update-time">{update_status['update_text']}</div>
        </div>
        
        <div class="news-list">
"""
        
        # 添加新闻项
        for article in articles[:20]:  # 只显示前20条
            title = article.get('ai_translation', {}).get('translated_title', article.get('title', '无标题'))
            description = article.get('ai_translation', {}).get('translated_description', article.get('description', '无描述'))
            
            time_info = article.get('time_info', {})
            relative_time = time_info.get('relative', '时间未知')
            
            category_chinese = article.get('category_chinese', '未分类')
            freshness_score = article.get('freshness_score', 0)
            
            # AI点评
            commentary = article.get('ai_commentary', {})
            commentary_html = ""
            if commentary.get('success') and commentary.get('commentary'):
                commentary_html = f"""
                <div class="ai-commentary">
                    <strong>🤖 AI点评：</strong>{commentary['commentary']}
                </div>
                """
            
            html_template += f"""
            <div class="news-item">
                <div class="news-title">{title}</div>
                <div class="news-meta">
                    <span class="freshness-score">新鲜度: {freshness_score:.2f}</span>
                    {category_chinese} · {relative_time}
                </div>
                <div class="news-description">{description}</div>
                {commentary_html}
            </div>
            """
        
        html_template += """
        </div>
    </div>
</body>
</html>
"""
        
        return html_template
    
    def save_news_data(self, articles):
        """保存新闻数据"""
        print("💾 保存新闻数据...")
        
        # 添加元数据
        news_data = {
            'last_updated': self.timezone_converter.get_current_beijing_time().isoformat(),
            'total_count': len(articles),
            'freshness_summary': self.freshness_manager.get_freshness_summary(articles),
            'articles': articles
        }
        
        # 保存到JSON文件
        with open(self.news_data_file, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 新闻数据已保存: {self.news_data_file}")
    
    def run(self):
        """运行主流程"""
        print("🚀 启动中文用户体验增强版AI新闻累积系统")
        print("=" * 60)
        
        try:
            # 1. 获取最新新闻
            articles = self.get_latest_news()
            if not articles:
                print("❌ 未获取到新闻数据")
                return
            
            print(f"📊 获取到 {len(articles)} 条原始新闻")
            
            # 2. 处理新闻并添加本地化信息
            processed_articles = self.process_news_with_localization(articles)
            print(f"📊 成功处理 {len(processed_articles)} 条新闻")
            
            # 3. 过滤和排序
            final_articles = self.filter_and_sort_news(processed_articles)
            print(f"📊 最终保留 {len(final_articles)} 条新闻")
            
            # 4. 生成HTML页面
            self.generate_html_page(final_articles)
            
            # 5. 保存数据
            self.save_news_data(final_articles)
            
            print("\n🎉 中文用户体验增强版新闻系统运行完成！")
            print("🌐 访问 docs/index.html 查看结果")
            
        except Exception as e:
            print(f"❌ 系统运行失败: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    accumulator = EnhancedChineseNewsAccumulator()
    accumulator.run()

if __name__ == "__main__":
    main()