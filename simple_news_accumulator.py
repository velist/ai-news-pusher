#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版AI新闻累积更新系统 - 仅依赖标准库
用于GitHub Actions部署，避免复杂依赖问题
"""

import os
import json
import urllib.request
import urllib.parse
import time
import hashlib
from datetime import datetime, timedelta

class SimpleAINewsAccumulator:
    def __init__(self):
        # API配置 - 从环境变量获取
        self.gnews_api_key = os.getenv('GNEWS_API_KEY')
        if not self.gnews_api_key:
            raise ValueError("GNEWS_API_KEY环境变量未设置")
        
        self.gnews_base_url = "https://gnews.io/api/v4"
        self.news_data_file = 'docs/enhanced_news_data.json'
        
        print("✅ 简化版新闻累积器初始化成功")
    
    def get_latest_news(self):
        """获取最新AI相关新闻"""
        all_articles = []
        
        # 定义AI相关搜索类别
        search_queries = [
            {
                "query": "AI artificial intelligence machine learning",
                "category": "AI技术",
                "description": "AI技术和机器学习"
            },
            {
                "query": "GPT OpenAI ChatGPT Claude",
                "category": "AI模型", 
                "description": "AI模型和语言模型"
            },
            {
                "query": "AI tools software applications",
                "category": "AI工具",
                "description": "AI工具和应用软件"
            },
            {
                "query": "AI industry business technology",
                "category": "AI产业",
                "description": "AI产业和商业应用"
            },
            {
                "query": "AI policy regulation government",
                "category": "AI政策",
                "description": "AI政策和监管"
            }
        ]
        
        for query_info in search_queries:
            print(f"📡 获取{query_info['description']}新闻...")
            articles = self._fetch_news(query_info["query"], query_info["category"])
            all_articles.extend(articles)
            time.sleep(1)  # 避免API限制
        
        return all_articles
    
    def _fetch_news(self, query, category):
        """获取特定查询的新闻"""
        try:
            url = f"{self.gnews_base_url}/search"
            params = {
                "q": query,
                "lang": "en",
                "country": "us",
                "max": 10,
                "apikey": self.gnews_api_key
            }
            
            query_string = urllib.parse.urlencode(params)
            full_url = f"{url}?{query_string}"
            
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            articles = []
            if data.get("articles"):
                for article in data["articles"]:
                    processed_article = self._process_article(article, category)
                    if processed_article:
                        articles.append(processed_article)
            
            print(f"✅ 获取到 {len(articles)} 条{category}新闻")
            return articles
            
        except Exception as e:
            print(f"❌ 获取{category}新闻失败: {e}")
            return []
    
    def _process_article(self, article, category):
        """处理单个新闻文章"""
        try:
            # 生成唯一ID
            article_id = hashlib.md5(
                (article.get('title', '') + article.get('url', '')).encode()
            ).hexdigest()[:12]
            
            # 简单的中文翻译映射（基础版本）
            title = article.get('title', '')
            description = article.get('description', '')
            
            # 基础的关键词替换翻译（简化版）
            translation_map = {
                'artificial intelligence': '人工智能',
                'machine learning': '机器学习',
                'ChatGPT': 'ChatGPT',
                'OpenAI': 'OpenAI',
                'technology': '科技',
                'software': '软件',
                'application': '应用',
                'development': '开发',
                'innovation': '创新'
            }
            
            # 简单替换（实际项目中应使用专业翻译API）
            for en, cn in translation_map.items():
                title = title.replace(en, cn)
                description = description.replace(en, cn)
            
            processed_article = {
                "id": article_id,
                "title": title,
                "summary": description,
                "original_title": article.get('title', ''),
                "original_summary": article.get('description', ''),
                "source": article.get('source', {}).get('name', '未知来源'),
                "url": article.get('url', ''),
                "published_at": article.get('publishedAt', ''),
                "category": category,
                "image_url": article.get('image', ''),
                "freshness": self._calculate_freshness(article.get('publishedAt', '')),
                "crawl_time": datetime.now().isoformat()
            }
            
            return processed_article
            
        except Exception as e:
            print(f"⚠️ 处理文章失败: {e}")
            return None
    
    def _calculate_freshness(self, published_at):
        """计算新闻新鲜度"""
        try:
            if not published_at:
                return "old"
            
            # 解析发布时间
            pub_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now(pub_time.tzinfo)
            
            hours_diff = (now - pub_time).total_seconds() / 3600
            
            if hours_diff <= 3:
                return "fresh"
            elif hours_diff <= 12:
                return "recent"
            else:
                return "old"
                
        except Exception:
            return "old"
    
    def load_existing_news(self):
        """加载现有新闻数据"""
        try:
            if os.path.exists(self.news_data_file):
                with open(self.news_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('articles', [])
        except Exception as e:
            print(f"⚠️ 加载现有新闻失败: {e}")
        return []
    
    def accumulate_news(self, new_articles, existing_articles):
        """累积新闻（去重并保留3天内容）"""
        # 创建现有文章ID集合
        existing_ids = {article['id'] for article in existing_articles}
        
        # 添加新文章（去重）
        added_count = 0
        for article in new_articles:
            if article['id'] not in existing_ids:
                existing_articles.append(article)
                added_count += 1
        
        # 按发布时间排序
        existing_articles.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        
        # 只保留3天内的新闻
        three_days_ago = datetime.now() - timedelta(days=3)
        filtered_articles = []
        
        for article in existing_articles:
            try:
                pub_time = datetime.fromisoformat(
                    article.get('published_at', '').replace('Z', '+00:00')
                )
                if pub_time.replace(tzinfo=None) > three_days_ago:
                    filtered_articles.append(article)
            except Exception:
                # 如果时间解析失败，保留文章
                filtered_articles.append(article)
        
        print(f"📊 累积统计: 新增{added_count}条，总计{len(filtered_articles)}条，保留3天内容")
        return filtered_articles
    
    def save_news_data(self, articles):
        """保存新闻数据"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.news_data_file), exist_ok=True)
            
            news_data = {
                "last_updated": datetime.now().isoformat(),
                "total_articles": len(articles),
                "articles": articles
            }
            
            with open(self.news_data_file, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 新闻数据已保存到 {self.news_data_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存新闻数据失败: {e}")
            return False
    
    def generate_html(self, articles):
        """生成HTML页面"""
        try:
            # 按分类组织文章
            categories = {
                "全部": articles,
                "AI模型": [a for a in articles if a.get('category') == 'AI模型'],
                "AI工具": [a for a in articles if a.get('category') == 'AI工具'],
                "AI技术": [a for a in articles if a.get('category') == 'AI技术'],
                "AI产业": [a for a in articles if a.get('category') == 'AI产业'],
                "AI政策": [a for a in articles if a.get('category') == 'AI政策']
            }
            
            html_content = self._generate_html_template(categories)
            
            html_file = 'docs/index.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML页面已生成: {html_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成HTML失败: {e}")
            return False
    
    def _generate_html_template(self, categories):
        """生成HTML模板"""
        # 使用现有的HTML模板结构
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 智能新闻推送</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: #1d1d1f;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: -0.02em;
        }}
        
        .header p {{
            font-size: 1.1em;
            color: #86868b;
            font-weight: 400;
        }}
        
        .update-time {{
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-size: 0.9em;
            color: #1d1d1f;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        
        .disclaimer {{
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            color: #856404;
            padding: 12px 20px;
            border-radius: 12px;
            margin-top: 15px;
            font-size: 0.9em;
            font-weight: 500;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            text-align: center;
        }}
        
        .tabs {{
            display: flex;
            margin-bottom: 30px;
            overflow-x: auto;
            overflow-y: hidden;
            padding: 0 20px 10px 20px;
            gap: 12px;
            scrollbar-width: none;
            -ms-overflow-style: none;
            scroll-behavior: smooth;
        }}
        
        .tabs::-webkit-scrollbar {{
            display: none;
        }}
        
        .tab {{
            background: rgba(255,255,255,0.7);
            color: #1d1d1f;
            border: 1px solid rgba(0,0,0,0.1);
            padding: 12px 24px;
            border-radius: 22px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            flex-shrink: 0;
            white-space: nowrap;
        }}
        
        .tab:hover {{
            background: rgba(255,255,255,0.9);
            transform: translateY(-1px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .tab.active {{
            background: #007aff;
            color: white;
            border: 1px solid #007aff;
            box-shadow: 0 4px 20px rgba(0,122,255,0.3);
        }}
        
        .news-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .news-card {{
            background: rgba(255,255,255,0.8);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }}
        
        .news-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            background: rgba(255,255,255,0.9);
        }}
        
        .news-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #007aff, #5856d6);
        }}
        
        .news-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            margin-right: 80px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .news-summary {{
            color: #666;
            font-size: 0.95em;
            margin-bottom: 20px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .news-meta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85em;
            color: #888;
            border-top: 1px solid #eee;
            padding-top: 15px;
        }}
        
        .news-source {{
            font-weight: 500;
            color: #007aff;
        }}
        
        .news-time {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .category-tag {{
            position: absolute;
            top: 15px;
            right: 15px;
            background: linear-gradient(45deg, #007aff, #5856d6);
            color: white;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.8em;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}
        
        .freshness-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 5px;
        }}
        
        .fresh {{
            background: #10B981;
        }}
        
        .recent {{
            background: #F59E0B;
        }}
        
        .old {{
            background: #EF4444;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .no-news {{
            text-align: center;
            color: #1d1d1f;
            font-size: 1.2em;
            padding: 40px;
            background: rgba(255,255,255,0.7);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 16px;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .tabs {{
                padding: 0 15px 10px 15px;
                gap: 8px;
            }}
            
            .tab {{
                padding: 10px 18px;
                font-size: 14px;
                border-radius: 18px;
                min-width: auto;
            }}
            
            .news-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .news-card {{
                padding: 20px;
                border-radius: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <div class="update-time">最后更新: {update_time}</div>
            <div class="disclaimer">⚠️ 声明：本站所有新闻均为海外媒体转推，使用权威GNews API实时同步，非本站原创内容 | AI交流群：<span id="groupId" onclick="copyGroupId()" style="cursor: pointer; color: #007AFF; text-decoration: underline;">forxy9</span></div>
        </div>
        
        <div class="tabs">
'''
        
        # 添加tab按钮
        for i, category in enumerate(categories.keys()):
            active_class = " active" if i == 0 else ""
            html += f'            <button class="tab{active_class}" onclick="showCategory(\'{category}\')">{category}</button>\n'
        
        html += '        </div>\n\n'
        
        # 添加每个分类的内容
        for i, (category, articles) in enumerate(categories.items()):
            active_class = " active" if i == 0 else ""
            html += f'        <div id="category-{category}" class="tab-content{active_class}">\n'
            
            if articles:
                html += '<div class="news-grid">\n'
                for article in articles[:20]:  # 限制每个分类最多20条
                    html += self._generate_article_html(article)
                html += '</div>'
            else:
                html += '<div class="no-news">暂无相关新闻</div>'
            
            html += '</div>\n\n'
        
        # 添加JavaScript
        html += '''    </div>
    
    <script>
        function showCategory(category) {
            // 隐藏所有tab内容
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // 移除所有tab的active状态
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // 显示选中的分类
            document.getElementById('category-' + category).classList.add('active');
            
            // 激活选中的tab
            event.target.classList.add('active');
        }
        
        function openDetail(articleId) {
            window.open('news/' + articleId + '.html', '_blank');
        }
        
        function copyGroupId() {
            const groupId = 'forxy9';
            navigator.clipboard.writeText(groupId).then(function() {
                // 创建临时提示
                const span = document.getElementById('groupId');
                const originalText = span.textContent;
                span.textContent = '复制成功，去微信搜索';
                span.style.color = '#34C759';
                
                // 2秒后恢复原文本
                setTimeout(function() {
                    span.textContent = originalText;
                    span.style.color = '#007AFF';
                }, 2000);
            }).catch(function(err) {
                console.error('复制失败: ', err);
                alert('复制失败，请手动复制: forxy9');
            });
        }
        
        // 添加卡片点击事件
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.news-card');
            cards.forEach(card => {
                card.addEventListener('click', function() {
                    const url = this.dataset.url;
                    if (url) {
                        window.open(url, '_blank');
                    }
                });
            });
        });
    </script>
</body>
</html>'''
        
        return html
    
    def _generate_article_html(self, article):
        """生成单个文章的HTML"""
        # 计算发布时间
        try:
            pub_time = datetime.fromisoformat(article.get('published_at', '').replace('Z', '+00:00'))
            now = datetime.now(pub_time.tzinfo)
            hours_diff = (now - pub_time).total_seconds() / 3600
            
            if hours_diff < 1:
                time_str = "刚刚"
            elif hours_diff < 24:
                time_str = f"{int(hours_diff)}小时前"
            else:
                time_str = f"{int(hours_diff/24)}天前"
        except Exception:
            time_str = "未知时间"
        
        freshness_class = article.get('freshness', 'old')
        
        return f'''            <div class="news-card" data-url="{article.get('url', '')}">
                <div class="category-tag">{article.get('category', '未分类')}</div>
                <div class="news-title">{article.get('title', '无标题')}</div>
                <div class="news-summary">{article.get('summary', '无摘要')}</div>
                <div class="news-meta">
                    <span class="news-source">{article.get('source', '未知来源')}</span>
                    <span class="news-time">
                        <span class="freshness-indicator {freshness_class}"></span>
                        {time_str}
                    </span>
                </div>
            </div>
        
'''
    
    def run(self):
        """运行新闻累积更新"""
        try:
            print("🚀 启动简化版AI新闻累积更新系统...")
            
            # 1. 获取最新新闻
            print("\n📡 获取最新新闻...")
            new_articles = self.get_latest_news()
            
            if not new_articles:
                print("⚠️ 未获取到新文章")
                return False
            
            # 2. 加载现有新闻
            print("\n📚 加载现有新闻数据...")
            existing_articles = self.load_existing_news()
            
            # 3. 累积新闻（去重和时间过滤）
            print("\n🔄 累积更新新闻...")
            all_articles = self.accumulate_news(new_articles, existing_articles)
            
            # 4. 保存数据
            print("\n💾 保存新闻数据...")
            if not self.save_news_data(all_articles):
                return False
            
            # 5. 生成HTML
            print("\n🌐 生成HTML页面...")
            if not self.generate_html(all_articles):
                return False
            
            print(f"\n✅ 累积更新完成！总计 {len(all_articles)} 条新闻")
            return True
            
        except Exception as e:
            print(f"❌ 运行失败: {e}")
            return False

if __name__ == "__main__":
    try:
        accumulator = SimpleAINewsAccumulator()
        success = accumulator.run()
        if success:
            print("\n🎉 新闻更新任务完成！")
        else:
            print("\n❌ 新闻更新任务失败！")
            exit(1)
    except Exception as e:
        print(f"❌ 程序启动失败: {e}")
        exit(1)