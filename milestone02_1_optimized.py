#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
里程碑02.1优化版 - AI新闻推送系统
主要改进：
1. 添加"全部"Tab分类
2. 丰富详情页内容，增加关键新闻信息
3. 新增"模型"分类，包含国内外AI模型新闻
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta, timezone
import sys
import time
import hashlib
import re

def load_env_file():
    """加载环境变量"""
    env_path = '.env'
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            return True
        except Exception as e:
            print(f"环境变量加载失败: {e}")
            return False
    return False

def format_beijing_time(iso_time_str):
    """将ISO时间字符串转换为北京时间并格式化显示"""
    try:
        # 解析ISO时间字符串
        if iso_time_str.endswith('Z'):
            dt = datetime.fromisoformat(iso_time_str[:-1] + '+00:00')
        else:
            dt = datetime.fromisoformat(iso_time_str)
        
        # 转换为北京时间 (UTC+8)
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = dt.astimezone(beijing_tz)
        
        # 计算时间差
        now_beijing = datetime.now(beijing_tz)
        time_diff = now_beijing - beijing_time
        
        if time_diff.days > 0:
            return f"{time_diff.days}天前"
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"{hours}小时前"
        elif time_diff.seconds > 60:
            minutes = time_diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
            
    except Exception as e:
        print(f"时间格式化错误: {e}")
        return "未知时间"

def format_full_beijing_time(iso_time_str):
    """格式化完整的北京时间用于详情页"""
    try:
        if iso_time_str.endswith('Z'):
            dt = datetime.fromisoformat(iso_time_str[:-1] + '+00:00')
        else:
            dt = datetime.fromisoformat(iso_time_str)
        
        beijing_tz = timezone(timedelta(hours=8))
        beijing_time = dt.astimezone(beijing_tz)
        
        return beijing_time.strftime("%Y年%m月%d日 %H:%M (北京时间)")
    except:
        return "未知时间"

class SiliconFlowTranslator:
    """硅基流动翻译服务"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
    def translate_text(self, text, target_lang='zh'):
        """翻译文本"""
        if not text or not text.strip():
            return ""
            
        try:
            # 针对新闻标题优化的翻译提示
            if len(text) < 100:  # 短文本，可能是标题
                prompt = f"""请将以下英文新闻标题翻译成中文，要求：
1. 保持新闻的准确性和时效性
2. 使用符合中文表达习惯的语言
3. 突出关键信息，适合中文读者理解
4. 只返回翻译结果，不要解释

英文标题：{text}

中文翻译："""
            else:  # 长文本，可能是摘要
                prompt = f"""请将以下英文新闻摘要翻译成中文，要求：
1. 保持新闻的客观性和准确性
2. 使用流畅自然的中文表达
3. 保留重要的人名、地名和专业术语
4. 只返回翻译结果，不要解释

英文摘要：{text}

中文翻译："""
            
            payload = {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1024
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(self.base_url, data=data, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'choices' in result and result['choices']:
                translated = result['choices'][0]['message']['content'].strip()
                # 清理可能的格式问题
                if translated.startswith('中文翻译：'):
                    translated = translated[5:].strip()
                return translated
            
        except Exception as e:
            print(f"翻译失败: {e}")
            
        return text  # 翻译失败返回原文

    def generate_ai_commentary(self, title, summary, source):
        """生成AI点评"""
        try:
            prompt = f"""作为AI行业专家，请针对以下新闻提供专业点评，要求：

1. 分析这个新闻对AI行业的意义和影响
2. 解释对普通用户的价值和意义
3. 用通俗易懂的语言，避免过于技术性的表述
4. 控制在100-150字内
5. 语调客观、专业但友好

新闻标题：{title}
新闻摘要：{summary}
新闻来源：{source}

专业点评："""

            payload = {
                "model": "Qwen/Qwen2.5-7B-Instruct", 
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 300
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(self.base_url, data=data, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'choices' in result and result['choices']:
                commentary = result['choices'][0]['message']['content'].strip()
                if commentary.startswith('专业点评：'):
                    commentary = commentary[5:].strip()
                return commentary
                
        except Exception as e:
            print(f"AI点评生成失败: {e}")
            
        return "暂时无法生成点评，请稍后再试。"

    def generate_extended_content(self, title, summary, source):
        """为详情页生成扩展内容"""
        try:
            prompt = f"""基于以下新闻信息，请生成详细的新闻分析内容，要求：

1. 深入分析新闻背景和影响
2. 提供行业上下文和相关信息
3. 解释技术术语和概念
4. 分析对不同群体的影响
5. 控制在300-500字
6. 使用清晰的段落结构
7. 语言通俗易懂，专业但不艰涩

新闻标题：{title}
新闻摘要：{summary}
新闻来源：{source}

扩展分析："""

            payload = {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.6,
                "max_tokens": 800
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(self.base_url, data=data, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'choices' in result and result['choices']:
                content = result['choices'][0]['message']['content'].strip()
                if content.startswith('扩展分析：'):
                    content = content[5:].strip()
                return content
                
        except Exception as e:
            print(f"扩展内容生成失败: {e}")
            
        return ""

class MultiNewsAggregator:
    """多源新闻聚合器"""
    
    def __init__(self, gnews_key, newsapi_key=None, currents_key=None):
        self.gnews_key = gnews_key
        self.newsapi_key = newsapi_key
        self.currents_key = currents_key
        self.translator = None
        
        # 初始化翻译服务
        siliconflow_key = os.environ.get('SILICONFLOW_API_KEY')
        if siliconflow_key:
            self.translator = SiliconFlowTranslator(siliconflow_key)
    
    def get_gnews_articles(self, query="AI OR OpenAI OR ChatGPT", max_results=20):
        """从GNews获取新闻"""
        articles = []
        try:
            url = f"https://gnews.io/api/v4/search?q={urllib.parse.quote(query)}&lang=en&country=us&max={max_results}&apikey={self.gnews_key}"
            
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if 'articles' in data:
                for article in data['articles']:
                    articles.append({
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', '未知来源'),
                        'publishedAt': article.get('publishedAt', ''),
                        'image': article.get('image', ''),
                        'api_source': 'gnews'
                    })
                    
        except Exception as e:
            print(f"GNews API调用失败: {e}")
            
        return articles
    
    def get_newsapi_articles(self, query="AI OR artificial intelligence", max_results=20):
        """从NewsAPI获取新闻"""
        if not self.newsapi_key:
            return []
            
        articles = []
        try:
            url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(query)}&language=en&sortBy=publishedAt&pageSize={max_results}&apiKey={self.newsapi_key}"
            
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            if 'articles' in data:
                for article in data['articles']:
                    articles.append({
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', '未知来源'),
                        'publishedAt': article.get('publishedAt', ''),
                        'image': article.get('urlToImage', ''),
                        'api_source': 'newsapi'
                    })
                    
        except Exception as e:
            print(f"NewsAPI调用失败: {e}")
            
        return articles
    
    def categorize_article(self, title, summary):
        """智能分类文章 - 新增模型分类"""
        title_lower = title.lower()
        summary_lower = summary.lower()
        combined = (title_lower + " " + summary_lower)
        
        # 模型相关关键词 (新增分类)
        model_keywords = [
            'gpt', 'chatgpt', 'gemini', 'claude', 'llama', 'qwen', 'baichuan', 'chatglm',
            'model', 'llm', 'large language model', 'ai model', 'neural network',
            'transformer', 'bert', 'dall-e', 'midjourney', 'stable diffusion',
            '通义', '文心', '混元', '智谱', '百川', '讯飞', 'minimax'
        ]
        
        if any(word in combined for word in model_keywords):
            return '模型', '🤖'
        
        # 投资并购关键词
        elif any(word in combined for word in ['funding', 'investment', 'raise', 'billion', 'million', 'valuation', 'ipo', 'acquisition', 'merger']):
            return '投资并购', '💰'
        
        # 公司动态关键词
        elif any(word in combined for word in ['openai', 'google', 'microsoft', 'apple', 'meta', 'amazon', 'nvidia', 'anthropic', 'baidu', 'alibaba', 'tencent']):
            return '公司动态', '🏢'
        
        # 技术突破关键词
        elif any(word in combined for word in ['breakthrough', 'research', 'algorithm', 'technology', 'innovation', 'development', 'discovery']):
            return '技术突破', '🚀'
        
        # 政策监管关键词
        elif any(word in combined for word in ['regulation', 'policy', 'government', 'law', 'compliance', 'ethics', 'safety']):
            return '政策监管', '⚖️'
        
        # 行业应用关键词
        elif any(word in combined for word in ['application', 'healthcare', 'finance', 'education', 'automotive', 'industry']):
            return '行业应用', '🎯'
        
        # 默认为热门
        return '热门', '🔥'
    
    def aggregate_news(self, max_total=60):
        """聚合多源新闻"""
        print("🔄 开始聚合多源新闻...")
        all_articles = []
        
        # 从GNews获取新闻
        print("📡 正在获取GNews新闻...")
        gnews_articles = self.get_gnews_articles(max_results=30)
        all_articles.extend(gnews_articles)
        print(f"✅ GNews获取到 {len(gnews_articles)} 条新闻")
        
        # 从NewsAPI获取新闻
        print("📡 正在获取NewsAPI新闻...")
        newsapi_articles = self.get_newsapi_articles(max_results=30)
        all_articles.extend(newsapi_articles)
        print(f"✅ NewsAPI获取到 {len(newsapi_articles)} 条新闻")
        
        # 去重处理
        seen_titles = set()
        unique_articles = []
        
        for article in all_articles:
            title_hash = hashlib.md5(article['title'].encode()).hexdigest()[:8]
            if title_hash not in seen_titles:
                seen_titles.add(title_hash)
                article['id'] = title_hash
                unique_articles.append(article)
        
        print(f"🔄 去重后获得 {len(unique_articles)} 条独特新闻")
        
        # 限制数量
        if len(unique_articles) > max_total:
            unique_articles = unique_articles[:max_total]
            
        return unique_articles
    
    def process_articles(self, articles):
        """处理文章：翻译、分类、AI点评、扩展内容"""
        processed_articles = []
        
        for i, article in enumerate(articles):
            print(f"🔄 处理文章 {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            # 分类
            category, category_icon = self.categorize_article(article['title'], article['summary'])
            
            # 翻译
            translated_title = article['title']
            translated_summary = article['summary']
            ai_commentary = ""
            extended_content = ""
            
            if self.translator:
                translated_title = self.translator.translate_text(article['title'])
                translated_summary = self.translator.translate_text(article['summary'])
                ai_commentary = self.translator.generate_ai_commentary(
                    article['title'], article['summary'], article['source']
                )
                extended_content = self.translator.generate_extended_content(
                    article['title'], article['summary'], article['source']
                )
            
            # 格式化时间
            time_display = format_beijing_time(article['publishedAt'])
            full_time_display = format_full_beijing_time(article['publishedAt'])
            
            processed_article = {
                'id': article['id'],
                'title': article['title'],
                'summary': article['summary'],
                'source': article['source'],
                'url': article['url'],
                'category': category,
                'category_icon': category_icon,
                'publishedAt': article['publishedAt'],
                'image': article['image'],
                'time': time_display,
                'full_time': full_time_display,
                'translated_title': translated_title,
                'translated_summary': translated_summary,
                'ai_commentary': ai_commentary,
                'extended_content': extended_content,
                'api_source': article.get('api_source', 'unknown')
            }
            
            processed_articles.append(processed_article)
            
            # 避免API限制，添加小延迟
            time.sleep(0.5)
        
        return processed_articles

def generate_main_page(articles):
    """生成主页HTML（包含全部分类）"""
    
    # 按分类组织文章
    categories = {}
    for article in articles:
        cat = article['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(article)
    
    # 生成分类tabs - 添加"全部"分类
    category_tabs = []
    category_contents = []
    
    # 全部分类排在第一位
    all_categories = ['全部', '热门', '模型', '公司动态', '技术突破', '行业应用', '投资并购', '政策监管']
    
    for i, cat in enumerate(all_categories):
        if cat == '全部':
            # 全部分类显示所有文章
            cat_articles = articles
            icon = '📰'
        else:
            cat_articles = categories.get(cat, [])
            icon = cat_articles[0]['category_icon'] if cat_articles else '📰'
        
        if cat_articles:  # 只显示有文章的分类
            # Tab按钮
            active_class = 'active' if i == 0 else ''
            category_tabs.append(f'''
                <div class="tab {active_class}" data-category="{cat}">
                    {icon} {cat} ({len(cat_articles)})
                </div>
            ''')
            
            # Tab内容
            news_cards = []
            for article in cat_articles:
                display_title = article.get('translated_title', article['title'])
                display_summary = article.get('translated_summary', article['summary'])
                
                news_cards.append(f'''
                    <div class="news-card">
                        <div class="news-meta">
                            <span class="news-source">{article['source']}</span>
                            <span class="news-time">{article['time']}</span>
                            <span class="news-category">{article['category_icon']} {article['category']}</span>
                        </div>
                        <h3 class="news-title">
                            <a href="news/{article['id']}.html">{display_title}</a>
                        </h3>
                        <p class="news-summary">{display_summary}</p>
                        <div class="news-footer">
                            <a href="news/{article['id']}.html" class="read-more">阅读全文 →</a>
                        </div>
                    </div>
                ''')
            
            category_contents.append(f'''
                <div class="tab-content {active_class}" id="{cat}">
                    <div class="news-grid">
                        {''.join(news_cards)}
                    </div>
                </div>
            ''')
    
    # 获取北京时间
    beijing_tz = timezone(timedelta(hours=8))
    beijing_time = datetime.now(beijing_tz)
    formatted_time = beijing_time.strftime("%Y年%m月%d日 %H:%M")
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 专业AI资讯平台</title>
    <meta name="description" content="专注AI前沿资讯，提供OpenAI、ChatGPT等最新动态，智能翻译+专家点评，您的AI信息门户">
    <meta name="keywords" content="AI新闻,人工智能,OpenAI,ChatGPT,AI投资,AI技术,AI应用,AI模型">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🤖</text></svg>">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "SimSun", sans-serif;
            line-height: 1.6; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: #333;
        }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        
        .header {{ 
            text-align: center; background: rgba(255,255,255,0.95); 
            border-radius: 24px; padding: 40px 30px; margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1); backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .header h1 {{ 
            font-size: 3em; margin-bottom: 15px; font-weight: 800;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; letter-spacing: -1px;
        }}
        
        .header .subtitle {{ 
            color: #666; font-size: 1.2em; margin-bottom: 25px; font-weight: 400;
        }}
        
        .update-time {{ 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 12px 28px; border-radius: 30px; 
            display: inline-block; font-weight: 600; font-size: 1.1em;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        
        /* 横向滑动的Tab样式 */
        .tabs-container {{
            background: rgba(255,255,255,0.9); 
            border-radius: 20px; 
            margin-bottom: 40px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }}
        
        .tabs {{ 
            display: flex; 
            overflow-x: auto; 
            padding: 20px;
            gap: 15px;
            scrollbar-width: none; /* Firefox */
            -ms-overflow-style: none; /* IE 10+ */
        }}
        
        .tabs::-webkit-scrollbar {{ display: none; }} /* Chrome/Safari */
        
        .tab {{ 
            background: rgba(255,255,255,0.8); 
            color: #555; 
            border: 2px solid rgba(0,0,0,0.1);
            padding: 15px 25px; 
            border-radius: 25px; 
            cursor: pointer; 
            font-size: 1.1em; 
            font-weight: 600; 
            transition: all 0.3s ease;
            display: flex; 
            align-items: center; 
            gap: 8px; 
            white-space: nowrap;
            flex-shrink: 0; /* 防止Tab收缩 */
            min-width: fit-content;
        }}
        
        .tab:hover {{ 
            background: rgba(102, 126, 234, 0.1); 
            border-color: #667eea;
            transform: translateY(-2px); 
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }}
        
        .tab.active {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            border-color: transparent;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        .news-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); 
            gap: 30px; 
            margin-top: 20px;
        }}
        
        .news-card {{ 
            background: rgba(255,255,255,0.95); 
            border-radius: 20px; 
            padding: 30px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px); 
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease; 
            height: fit-content;
        }}
        
        .news-card:hover {{ 
            transform: translateY(-5px); 
            box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        }}
        
        .news-meta {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
            margin-bottom: 15px; 
            font-size: 0.9em; 
            color: #666;
            flex-wrap: wrap;
            gap: 8px;
        }}
        
        .news-source {{ 
            background: rgba(102, 126, 234, 0.1); 
            color: #667eea; 
            padding: 6px 12px; 
            border-radius: 15px; 
            font-weight: 600;
        }}
        
        .news-category {{
            background: rgba(118, 75, 162, 0.1);
            color: #764ba2;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .news-time {{ font-weight: 500; }}
        
        .news-title {{ 
            font-size: 1.4em; 
            margin-bottom: 15px; 
            font-weight: 700; 
            line-height: 1.3;
        }}
        
        .news-title a {{ 
            color: #333; 
            text-decoration: none; 
            transition: color 0.3s ease;
        }}
        
        .news-title a:hover {{ color: #667eea; }}
        
        .news-summary {{ 
            color: #666; 
            margin-bottom: 20px; 
            line-height: 1.6;
        }}
        
        .news-footer {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center;
        }}
        
        .read-more {{ 
            color: #667eea; 
            text-decoration: none; 
            font-weight: 600; 
            font-size: 1.1em;
            transition: all 0.3s ease;
        }}
        
        .read-more:hover {{ 
            color: #764ba2; 
            transform: translateX(5px);
        }}
        
        /* 移动端优化 */
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            
            .header {{ padding: 30px 20px; }}
            
            .header h1 {{ font-size: 2.2em; }}
            
            .tabs {{ padding: 15px; gap: 10px; }}
            
            .tab {{ 
                padding: 12px 20px; 
                font-size: 1em;
                min-width: 120px;
            }}
            
            .news-grid {{ 
                grid-template-columns: 1fr; 
                gap: 20px;
            }}
            
            .news-card {{ padding: 25px; }}
            
            .news-title {{ font-size: 1.2em; }}
            
            .news-meta {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}
        }}
        
        /* 超小屏幕优化 */
        @media (max-width: 480px) {{
            .header h1 {{ font-size: 1.8em; }}
            
            .header .subtitle {{ font-size: 1em; }}
            
            .update-time {{ 
                padding: 10px 20px; 
                font-size: 1em;
            }}
            
            .tab {{ 
                padding: 10px 16px; 
                min-width: 100px;
            }}
            
            .news-card {{ padding: 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">专注人工智能前沿资讯，每日精选优质内容</p>
            <div class="update-time">最后更新：{formatted_time}</div>
        </div>
        
        <div class="tabs-container">
            <div class="tabs">
                {''.join(category_tabs)}
            </div>
        </div>
        
        {''.join(category_contents)}
    </div>
    
    <script>
        // Tab切换功能
        document.addEventListener('DOMContentLoaded', function() {{
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {{
                tab.addEventListener('click', function() {{
                    const category = this.dataset.category;
                    
                    // 移除所有active类
                    tabs.forEach(t => t.classList.remove('active'));
                    contents.forEach(c => c.classList.remove('active'));
                    
                    // 添加active类到当前选中的
                    this.classList.add('active');
                    document.getElementById(category).classList.add('active');
                }});
            }});
        }});
    </script>
</body>
</html>'''

    return html

def generate_article_page(article):
    """生成文章详情页HTML（丰富内容版本）"""
    display_title = article.get('translated_title', article['title'])
    display_summary = article.get('translated_summary', article['summary'])
    extended_content = article.get('extended_content', '')
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} - AI科技日报</title>
    <meta name="description" content="{display_summary[:150]}...">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "SimSun", sans-serif;
            line-height: 1.8; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; margin: 0; padding: 20px; color: #333;
        }}
        
        .article-container {{
            max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.95);
            border-radius: 24px; padding: 50px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .back-link {{
            display: inline-block; color: #667eea; text-decoration: none; 
            font-weight: 600; margin-bottom: 30px; font-size: 1.1em;
            transition: all 0.3s ease;
        }}
        
        .back-link:hover {{ color: #764ba2; transform: translateX(-5px); }}
        
        .article-header {{
            border-bottom: 3px solid rgba(102, 126, 234, 0.1); 
            padding-bottom: 30px; margin-bottom: 40px;
        }}
        
        .article-category {{
            display: inline-block; background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 10px 20px; border-radius: 20px; 
            font-weight: 600; margin-bottom: 20px; font-size: 1em;
        }}
        
        .article-title {{
            font-size: 2.5em; font-weight: 800; line-height: 1.2; 
            margin-bottom: 20px; color: #333;
        }}
        
        .article-meta {{
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px; background: rgba(102, 126, 234, 0.05); 
            padding: 20px; border-radius: 15px; margin-bottom: 30px;
        }}
        
        .meta-item {{
            display: flex; flex-direction: column; gap: 5px;
        }}
        
        .meta-label {{
            font-size: 0.9em; color: #666; font-weight: 600;
        }}
        
        .meta-value {{
            font-size: 1em; color: #333; font-weight: 500;
        }}
        
        .article-source {{
            background: rgba(102, 126, 234, 0.1); color: #667eea; 
            padding: 8px 16px; border-radius: 20px; font-weight: 600;
            display: inline-block; width: fit-content;
        }}
        
        .article-content {{
            font-size: 1.2em; line-height: 1.8; margin-bottom: 40px;
        }}
        
        .content-section {{
            margin-bottom: 30px;
        }}
        
        .content-section h3 {{
            color: #667eea; font-size: 1.4em; margin-bottom: 15px;
            font-weight: 700; border-left: 4px solid #667eea;
            padding-left: 15px;
        }}
        
        .extended-content {{
            background: rgba(118, 75, 162, 0.05);
            padding: 25px; border-radius: 15px; margin-bottom: 30px;
            border-left: 4px solid #764ba2;
        }}
        
        .ai-commentary {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
            border-left: 5px solid #667eea; padding: 30px; border-radius: 15px;
            margin-bottom: 30px;
        }}
        
        .ai-commentary h4 {{
            color: #667eea; font-size: 1.3em; margin-bottom: 15px; 
            font-weight: 700; display: flex; align-items: center; gap: 10px;
        }}
        
        .ai-commentary-content {{
            font-size: 1.1em; line-height: 1.7; color: #555;
        }}
        
        .article-actions {{
            text-align: center; padding-top: 30px; 
            border-top: 2px solid rgba(102, 126, 234, 0.1);
        }}
        
        .original-link {{
            display: inline-block; background: linear-gradient(45deg, #667eea, #764ba2);
            color: white; padding: 15px 30px; border-radius: 25px; 
            text-decoration: none; font-weight: 600; font-size: 1.1em;
            transition: all 0.3s ease; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        
        .original-link:hover {{
            transform: translateY(-3px); box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
        }}
        
        @media (max-width: 768px) {{
            .article-container {{ padding: 30px 25px; }}
            .article-title {{ font-size: 2em; }}
            .article-meta {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="article-container">
        <a href="../index.html" class="back-link">← 返回首页</a>
        
        <div class="article-header">
            <div class="article-category">{article['category_icon']} {article['category']}</div>
            <h1 class="article-title">{display_title}</h1>
            
            <div class="article-meta">
                <div class="meta-item">
                    <div class="meta-label">📰 新闻来源</div>
                    <div class="meta-value article-source">{article['source']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">⏰ 发布时间</div>
                    <div class="meta-value">{article['full_time']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">🏷️ 新闻分类</div>
                    <div class="meta-value">{article['category_icon']} {article['category']}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">🔗 原文链接</div>
                    <div class="meta-value">
                        <a href="{article['url']}" target="_blank" style="color: #667eea; text-decoration: none;">查看原文</a>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="article-content">
            <div class="content-section">
                <h3>📋 新闻摘要</h3>
                <p>{display_summary}</p>
            </div>
            
            {('<div class="extended-content"><h3>📊 深度分析</h3>' + extended_content + '</div>') if extended_content else ''}
        </div>
        
        {('<div class="ai-commentary"><h4>🤖 AI专家点评</h4><div class="ai-commentary-content">' +
        article['ai_commentary'] + '</div></div>') if article.get('ai_commentary') else ''}
        
        <div class="article-actions">
            <a href="{article['url']}" target="_blank" class="original-link">查看英文原文 →</a>
        </div>
    </div>
</body>
</html>'''

    return html

def main():
    """主函数"""
    print("🎯 里程碑02.1优化版 - AI新闻推送系统启动")
    print("=" * 60)
    
    # 加载环境变量
    load_env_file()
    
    # 获取API密钥
    gnews_key = os.environ.get('GNEWS_API_KEY')
    newsapi_key = os.environ.get('NEWSAPI_KEY')
    
    if not gnews_key:
        print("❌ 缺少必要的API密钥")
        return
    
    # 创建多源新闻聚合器
    aggregator = MultiNewsAggregator(gnews_key, newsapi_key)
    
    # 聚合新闻
    articles = aggregator.aggregate_news(max_total=60)
    
    if not articles:
        print("❌ 未获取到任何新闻")
        return
    
    # 处理文章
    processed_articles = aggregator.process_articles(articles)
    
    # 确保目录存在
    os.makedirs('docs', exist_ok=True)
    os.makedirs('docs/news', exist_ok=True)
    
    # 生成主页
    print("📄 生成优化版主页...")
    main_html = generate_main_page(processed_articles)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(main_html)
    
    # 生成文章详情页
    print("📄 生成丰富内容的文章详情页...")
    for article in processed_articles:
        article_html = generate_article_page(article)
        with open(f"docs/news/{article['id']}.html", 'w', encoding='utf-8') as f:
            f.write(article_html)
    
    # 保存增强的新闻数据
    enhanced_data = {
        'last_updated': datetime.now().isoformat(),
        'total_count': len(processed_articles),
        'categories': list(set(article['category'] for article in processed_articles)),
        'articles': processed_articles
    }
    
    with open('docs/enhanced_news_data.json', 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, ensure_ascii=False, indent=2)
    
    print("🎉 里程碑02.1优化版生成完成！")
    print(f"✅ 处理了 {len(processed_articles)} 条新闻")
    print(f"📂 生成了 {len(processed_articles)} 个丰富内容的详情页面")
    print("🌐 访问地址: https://velist.github.io/ai-news-pusher/docs/")

if __name__ == "__main__":
    main()