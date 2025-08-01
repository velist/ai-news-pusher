#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户体验优化版 - AI新闻推送系统
专为国内用户打造，集成翻译、AI点评、多分类等功能
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
import sys
import time
import hashlib

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

class AICommentator:
    """AI点评生成器"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
    def generate_commentary(self, title, summary, category="AI科技"):
        """生成AI点评"""
        try:
            prompt = f"""作为AI行业专家，请为以下新闻撰写一段专业点评，要求：

1. 分析新闻的行业意义和影响
2. 指出技术发展趋势或商业价值
3. 对普通读者提供易懂的解读
4. 控制在80-120字以内
5. 语言要专业但不晦涩

新闻分类：{category}
新闻标题：{title}
新闻摘要：{summary}

专家点评："""
            
            payload = {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 512
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
                if commentary.startswith('专家点评：'):
                    commentary = commentary[5:].strip()
                return commentary
                
        except Exception as e:
            print(f"AI点评生成失败: {e}")
            
        return ""

def get_news_categories():
    """定义新闻分类"""
    return {
        "热门": {
            "queries": [
                "OpenAI OR ChatGPT OR GPT OR Claude OR Gemini",
                "AI breakthrough OR artificial intelligence news"
            ],
            "icon": "🔥",
            "description": "最新最热的AI资讯",
            "max_per_query": 8
        },
        "公司动态": {
            "queries": [
                "OpenAI OR Anthropic OR Google AI OR Microsoft AI",
                "AI company OR AI startup OR AI funding"
            ],
            "icon": "🏢", 
            "description": "AI公司最新动态",
            "max_per_query": 6
        },
        "技术突破": {
            "queries": [
                "AI model OR machine learning OR deep learning",
                "AI research OR AI algorithm OR neural network"
            ],
            "icon": "🚀",
            "description": "前沿技术进展",
            "max_per_query": 6
        },
        "行业应用": {
            "queries": [
                "AI application OR AI tool OR AI software",
                "AI automation OR AI productivity"
            ],
            "icon": "⚡",
            "description": "AI实际应用案例",
            "max_per_query": 6
        },
        "投资并购": {
            "queries": [
                "AI investment OR AI funding OR AI acquisition",
                "AI IPO OR AI venture capital"
            ],
            "icon": "💰",
            "description": "投资与商业动态",
            "max_per_query": 5
        },
        "政策监管": {
            "queries": [
                "AI regulation OR AI policy OR AI governance",
                "AI law OR AI ethics OR AI safety"
            ],
            "icon": "📋",
            "description": "政策法规动向",
            "max_per_query": 5
        }
    }

def fetch_categorized_news(api_key, max_retries=2):
    """按分类获取新闻"""
    categories = get_news_categories()
    all_articles = []
    
    print("🔍 开始按分类获取新闻...")
    
    for category_name, config in categories.items():
        print(f"\n📰 获取 {config['icon']} {category_name} 新闻...")
        category_articles = []
        
        for query in config['queries']:
            for attempt in range(max_retries):
                try:
                    params = {
                        "q": query,
                        "lang": "en",
                        "country": "us",
                        "max": config['max_per_query'],
                        "sortby": "publishedAt",
                        "apikey": api_key
                    }
                    
                    query_string = urllib.parse.urlencode(params)
                    url = f"https://gnews.io/api/v4/search?{query_string}"
                    
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'Mozilla/5.0 (compatible; NewsBot/1.0)')
                    
                    with urllib.request.urlopen(req, timeout=15) as response:
                        data = json.loads(response.read().decode())
                    
                    if 'articles' in data and data['articles']:
                        for article in data['articles']:
                            if article.get('title') and article.get('url'):
                                processed_article = {
                                    "id": hashlib.md5(f"{article['url']}{article['title']}".encode()).hexdigest()[:12],
                                    "title": article.get('title', '').strip(),
                                    "summary": article.get('description', '').strip(),
                                    "source": article.get('source', {}).get('name', '未知来源'),
                                    "url": article.get('url', ''),
                                    "category": category_name,
                                    "category_icon": config['icon'],
                                    "publishedAt": article.get('publishedAt'),
                                    "image": article.get('image'),
                                    "time": format_publish_time(article.get('publishedAt')),
                                    "original_query": query
                                }
                                category_articles.append(processed_article)
                        
                        print(f"  ✅ {query[:30]}... 获取到 {len(data['articles'])} 条")
                        break
                        
                except Exception as e:
                    print(f"  ❌ 查询失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1)
            
            time.sleep(0.5)  # 避免频率限制
        
        # 去重并限制数量
        seen_urls = set()
        unique_articles = []
        for article in category_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        # 按发布时间排序，取最新的
        unique_articles.sort(key=lambda x: x.get('publishedAt', ''), reverse=True)
        final_articles = unique_articles[:10]  # 每个分类最多10条
        
        all_articles.extend(final_articles)
        print(f"  📊 {category_name} 最终保留 {len(final_articles)} 条")
    
    print(f"\n📊 总计获取 {len(all_articles)} 条新闻")
    return all_articles

def format_publish_time(published_at):
    """格式化发布时间"""
    if not published_at:
        return "时间未知"
    
    try:
        if published_at.endswith('Z'):
            published_time = datetime.fromisoformat(published_at[:-1])
        else:
            published_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        
        now = datetime.now()
        time_diff = now - published_time.replace(tzinfo=None)
        
        if time_diff.days > 0:
            if time_diff.days == 1:
                return "昨天"
            elif time_diff.days < 7:
                return f"{time_diff.days}天前"
            else:
                return published_time.strftime("%m月%d日")
        elif time_diff.seconds > 3600:
            hours = time_diff.seconds // 3600
            return f"{hours}小时前"
        elif time_diff.seconds > 60:
            minutes = time_diff.seconds // 60
            return f"{minutes}分钟前"
        else:
            return "刚刚"
            
    except Exception:
        return "时间未知"

def translate_and_enhance_articles(articles, translator, commentator):
    """翻译并增强文章内容"""
    print("\n🌐 开始翻译和AI点评...")
    
    enhanced_articles = []
    for i, article in enumerate(articles, 1):
        print(f"处理第 {i}/{len(articles)} 条: {article['title'][:50]}...")
        
        try:
            # 翻译标题
            translated_title = translator.translate_text(article['title'])
            if translated_title != article['title']:
                article['translated_title'] = translated_title
            
            # 翻译摘要
            if article['summary']:
                translated_summary = translator.translate_text(article['summary'])
                if translated_summary != article['summary']:
                    article['translated_summary'] = translated_summary
            
            # 生成AI点评 (只对前20条生成，控制成本)
            if i <= 20:
                commentary = commentator.generate_commentary(
                    article.get('translated_title', article['title']),
                    article.get('translated_summary', article['summary']),
                    article['category']
                )
                if commentary:
                    article['ai_commentary'] = commentary
            
            enhanced_articles.append(article)
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            enhanced_articles.append(article)  # 即使处理失败也保留原文
        
        # 避免过于频繁的API调用
        if i % 5 == 0:
            time.sleep(1)
    
    print(f"✅ 翻译和点评完成，成功处理 {len(enhanced_articles)} 条")
    return enhanced_articles

def generate_user_friendly_html(articles):
    """生成用户友好的HTML页面"""
    update_time = datetime.now().strftime('%Y年%m月%d日 %H:%M')
    categories = get_news_categories()
    
    # 按分类组织文章
    categorized_articles = {}
    for category_name in categories.keys():
        categorized_articles[category_name] = [
            article for article in articles if article.get('category') == category_name
        ]
    
    # 添加"全部"分类
    categorized_articles = {"全部": articles, **categorized_articles}
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 专业AI资讯平台</title>
    <meta name="description" content="专注AI前沿资讯，提供OpenAI、ChatGPT等最新动态，智能翻译+专家点评，您的AI信息门户">
    <meta name="keywords" content="AI新闻,人工智能,OpenAI,ChatGPT,AI投资,AI技术,AI应用">
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
        
        .stats {{ 
            display: flex; justify-content: center; gap: 40px; margin-top: 30px;
            flex-wrap: wrap;
        }}
        
        .stat-item {{ 
            background: rgba(102, 126, 234, 0.1); padding: 20px 30px; 
            border-radius: 16px; text-align: center; min-width: 140px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }}
        
        .stat-number {{ 
            font-size: 2.2em; font-weight: 800; color: #667eea; 
            margin-bottom: 5px; display: block;
        }}
        
        .stat-label {{ font-size: 1em; color: #666; font-weight: 500; }}
        
        .tabs {{ 
            display: flex; gap: 15px; margin-bottom: 40px; 
            flex-wrap: wrap; justify-content: center;
            background: rgba(255,255,255,0.9); padding: 20px;
            border-radius: 20px; backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .tab {{ 
            background: rgba(255,255,255,0.8); color: #555; border: 2px solid rgba(0,0,0,0.1);
            padding: 15px 25px; border-radius: 25px; cursor: pointer; 
            font-size: 1.1em; font-weight: 600; transition: all 0.3s ease;
            display: flex; align-items: center; gap: 8px; white-space: nowrap;
        }}
        
        .tab:hover {{ 
            background: rgba(102, 126, 234, 0.1); border-color: #667eea;
            transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        }}
        
        .tab.active {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; border-color: transparent;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }}
        
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        .news-grid {{ 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); 
            gap: 30px; margin-top: 20px;
        }}
        
        .news-card {{ 
            background: rgba(255,255,255,0.95); border-radius: 20px; 
            padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: all 0.4s ease; cursor: pointer; position: relative;
            backdrop-filter: blur(15px); border: 1px solid rgba(255,255,255,0.3);
            overflow: hidden;
        }}
        
        .news-card:hover {{ 
            transform: translateY(-8px); 
            box-shadow: 0 25px 60px rgba(0,0,0,0.15);
        }}
        
        .news-card::before {{ 
            content: ''; position: absolute; top: 0; left: 0; right: 0; 
            height: 5px; background: linear-gradient(90deg, #667eea, #764ba2);
        }}
        
        .category-tag {{ 
            position: absolute; top: 20px; right: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2); color: white;
            padding: 8px 16px; border-radius: 20px; font-size: 0.9em; 
            font-weight: 700; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            display: flex; align-items: center; gap: 5px;
        }}
        
        .news-title {{ 
            font-size: 1.4em; font-weight: 700; color: #333; 
            margin-bottom: 15px; line-height: 1.4; padding-right: 120px;
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .translated-title {{ 
            color: #2c3e50; border-left: 4px solid #667eea; 
            padding-left: 15px; margin-bottom: 10px;
        }}
        
        .original-title {{ 
            color: #7f8c8d; font-size: 0.9em; margin-bottom: 15px;
            font-style: italic;
        }}
        
        .news-summary {{ 
            color: #666; margin-bottom: 20px; line-height: 1.7;
            font-size: 1em; display: -webkit-box; -webkit-line-clamp: 3; 
            -webkit-box-orient: vertical; overflow: hidden;
        }}
        
        .ai-commentary {{ 
            background: linear-gradient(135deg, #e8f4fd 0%, #f0f8ff 100%);
            border-left: 4px solid #667eea; padding: 18px; margin: 20px 0;
            border-radius: 0 12px 12px 0; position: relative;
        }}
        
        .ai-commentary::before {{
            content: '🤖'; position: absolute; top: -5px; left: -2px;
            background: white; padding: 5px; border-radius: 50%; 
            font-size: 1.2em; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .ai-commentary-label {{ 
            font-weight: 700; color: #667eea; font-size: 0.9em; 
            margin-bottom: 8px; margin-left: 25px;
        }}
        
        .ai-commentary-content {{ 
            color: #444; line-height: 1.6; font-size: 0.95em;
        }}
        
        .news-meta {{ 
            display: flex; justify-content: space-between; align-items: center;
            padding-top: 20px; border-top: 2px solid #f0f0f0; margin-top: 20px;
        }}
        
        .news-source {{ 
            font-weight: 700; color: #667eea; font-size: 1em;
            background: rgba(102, 126, 234, 0.1); padding: 6px 12px;
            border-radius: 15px;
        }}
        
        .news-time {{ 
            color: #999; font-size: 0.9em; font-weight: 500;
        }}
        
        .no-news {{ 
            text-align: center; color: #666; padding: 60px 20px; 
            font-size: 1.2em; background: rgba(255,255,255,0.9);
            border-radius: 20px; margin: 20px 0;
        }}
        
        .footer {{
            text-align: center; margin-top: 60px; padding: 40px;
            background: rgba(255,255,255,0.1); border-radius: 25px;
            backdrop-filter: blur(15px); color: rgba(255,255,255,0.9);
        }}
        
        .footer h3 {{ margin-bottom: 15px; font-size: 1.3em; }}
        .footer p {{ margin: 8px 0; font-size: 1em; }}
        .footer a {{ color: rgba(255,255,255,0.9); text-decoration: none; font-weight: 600; }}
        .footer a:hover {{ text-decoration: underline; }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .header {{ padding: 25px 20px; }}
            .header h1 {{ font-size: 2.2em; }}
            .stats {{ gap: 20px; }}
            .tabs {{ gap: 10px; padding: 15px; }}
            .tab {{ padding: 12px 18px; font-size: 1em; }}
            .news-grid {{ grid-template-columns: 1fr; gap: 20px; }}
            .news-card {{ padding: 20px; }}
            .news-title {{ padding-right: 80px; font-size: 1.2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p class="subtitle">专注人工智能前沿资讯 · 智能翻译 · 专家点评 · 每日精选</p>
            <div class="update-time">最后更新: {update_time}</div>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{len(articles)}</span>
                    <span class="stat-label">今日资讯</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len([a for a in articles if a.get('translated_title')])}</span>
                    <span class="stat-label">中文翻译</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len([a for a in articles if a.get('ai_commentary')])}</span>
                    <span class="stat-label">AI点评</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(categorized_articles) - 1}</span>
                    <span class="stat-label">新闻分类</span>
                </div>
            </div>
        </div>
        
        <div class="tabs">'''
    
    # 生成标签
    for i, (category_name, articles_list) in enumerate(categorized_articles.items()):
        if category_name == "全部":
            icon = "📊"
            count = len(articles_list)
        else:
            category_config = categories.get(category_name, {})
            icon = category_config.get('icon', '📰')
            count = len(articles_list)
        
        active_class = ' active' if i == 0 else ''
        html += f'''            <div class="tab{active_class}" onclick="showCategory('{category_name}')">
                <span>{icon}</span>
                <span>{category_name}</span>
                <span>({count})</span>
            </div>
'''
    
    html += '        </div>\n'
    
    # 生成内容区域
    for i, (category_name, articles_list) in enumerate(categorized_articles.items()):
        active_class = ' active' if i == 0 else ''
        html += f'        <div id="category-{category_name}" class="tab-content{active_class}">\n'
        
        if articles_list:
            html += '            <div class="news-grid">\n'
            for article in articles_list:
                # 使用翻译后的标题，如果没有则使用原标题
                display_title = article.get('translated_title', article.get('title', '无标题'))
                original_title = article.get('title', '') if article.get('translated_title') else ''
                display_summary = article.get('translated_summary', article.get('summary', '无摘要'))
                
                # 构建标题HTML
                title_html = f'<h3 class="news-title translated-title">{display_title}</h3>'
                if original_title:
                    title_html += f'<p class="original-title">{original_title}</p>'
                
                # AI点评HTML
                commentary_html = ""
                if article.get('ai_commentary'):
                    commentary_html = f'''
                    <div class="ai-commentary">
                        <div class="ai-commentary-label">AI专家点评</div>
                        <div class="ai-commentary-content">{article['ai_commentary']}</div>
                    </div>'''
                
                html += f'''                <div class="news-card" onclick="openDetail('{article.get('id', '')}')">
                    <div class="category-tag">
                        <span>{article.get('category_icon', '📰')}</span>
                        <span>{article.get('category', '未分类')}</span>
                    </div>
                    {title_html}
                    <p class="news-summary">{display_summary}</p>
                    {commentary_html}
                    <div class="news-meta">
                        <span class="news-source">{article.get('source', '未知来源')}</span>
                        <span class="news-time">{article.get('time', '未知时间')}</span>
                    </div>
                </div>
'''
            html += '            </div>\n'
        else:
            html += '            <div class="no-news">该分类暂无新闻</div>\n'
        
        html += '        </div>\n'
    
    html += f'''        
        <div class="footer">
            <h3>🤖 AI科技日报</h3>
            <p>专注人工智能领域，为您提供最权威、最及时的AI资讯</p>
            <p>智能翻译 · 专家点评 · 分类精选 · 每日更新</p>
            <p style="margin-top: 20px;">
                <a href="https://github.com/velist/ai-news-pusher" target="_blank">GitHub开源</a> · 
                <a href="mailto:contact@ai-daily.news">联系我们</a> · 
                <a href="/rss" target="_blank">RSS订阅</a>
            </p>
            <p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
                数据来源：GNews API | 翻译服务：硅基流动 | 更新频率：每2小时
            </p>
        </div>
    </div>
    
    <script>
        function showCategory(category) {{
            // 隐藏所有内容
            document.querySelectorAll('.tab-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的内容
            document.getElementById('category-' + category).classList.add('active');
            event.target.closest('.tab').classList.add('active');
            
            // 滚动到顶部
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        function openDetail(articleId) {{
            if (articleId) {{
                window.open('news/' + articleId + '.html', '_blank');
            }}
        }}
        
        // 页面加载动画
        document.addEventListener('DOMContentLoaded', function() {{
            const cards = document.querySelectorAll('.news-card');
            cards.forEach((card, index) => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(30px)';
                setTimeout(() => {{
                    card.style.transition = 'all 0.6s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }}, index * 100);
            }});
            
            // 统计信息动画
            const statNumbers = document.querySelectorAll('.stat-number');
            statNumbers.forEach((stat, index) => {{
                const finalNumber = parseInt(stat.textContent);
                let currentNumber = 0;
                const increment = finalNumber / 30;
                const timer = setInterval(() => {{
                    currentNumber += increment;
                    if (currentNumber >= finalNumber) {{
                        stat.textContent = finalNumber;
                        clearInterval(timer);
                    }} else {{
                        stat.textContent = Math.floor(currentNumber);
                    }}
                }}, 50);
            }});
        }});
    </script>
</body>
</html>'''
    
    return html

def generate_enhanced_detail_page(article):
    """生成丰富的详情页面"""
    # 使用翻译后的内容
    display_title = article.get('translated_title', article.get('title', '无标题'))
    original_title = article.get('title', '') if article.get('translated_title') else ''
    display_summary = article.get('translated_summary', article.get('summary', '无摘要'))
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_title} - AI科技日报</title>
    <meta name="description" content="{display_summary[:150]}...">
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; padding: 20px; min-height: 100vh;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .back-btn {{ 
            background: rgba(255,255,255,0.9); color: #667eea; border: none;
            padding: 15px 30px; border-radius: 30px; text-decoration: none;
            display: inline-flex; align-items: center; gap: 10px; font-weight: 600;
            margin-bottom: 30px; transition: all 0.3s ease; font-size: 1.1em;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        }}
        .back-btn:hover {{ 
            background: #667eea; color: white; transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(102, 126, 234, 0.3);
        }}
        .article {{ 
            background: rgba(255,255,255,0.95); border-radius: 25px; 
            padding: 50px; box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.3);
        }}
        .article-title {{ 
            font-size: 2.5em; font-weight: 800; color: #2c3e50; 
            margin-bottom: 15px; line-height: 1.3;
        }}
        .original-title {{
            font-size: 1.1em; color: #7f8c8d; font-style: italic;
            margin-bottom: 25px; padding: 15px; background: rgba(0,0,0,0.03);
            border-radius: 10px; border-left: 4px solid #bdc3c7;
        }}
        .article-meta {{ 
            display: flex; justify-content: space-between; align-items: center;
            padding: 25px 0; border-bottom: 3px solid #ecf0f1; margin-bottom: 35px;
            flex-wrap: wrap; gap: 15px;
        }}
        .meta-left {{ display: flex; align-items: center; gap: 15px; }}
        .article-source {{ 
            font-weight: 700; color: white; font-size: 1.2em;
            background: linear-gradient(45deg, #667eea, #764ba2);
            padding: 10px 20px; border-radius: 25px;
        }}
        .article-time {{ color: #666; font-size: 1em; }}
        .article-category {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); color: white;
            padding: 10px 20px; border-radius: 25px; font-size: 1em; font-weight: 600;
            display: flex; align-items: center; gap: 8px;
        }}
        .article-content {{ 
            font-size: 1.2em; color: #2c3e50; line-height: 1.8; 
            margin-bottom: 35px; text-align: justify;
        }}
        .ai-commentary {{ 
            background: linear-gradient(135deg, #e8f4fd 0%, #f0f8ff 100%);
            border: 2px solid #667eea; padding: 30px; margin: 35px 0;
            border-radius: 20px; position: relative;
        }}
        .ai-commentary::before {{
            content: '🤖 AI专家点评'; position: absolute; top: -15px; left: 25px;
            background: white; padding: 5px 15px; font-weight: 700;
            color: #667eea; border-radius: 20px; font-size: 1.1em;
        }}
        .ai-commentary-content {{ 
            color: #2c3e50; line-height: 1.7; font-size: 1.1em; margin-top: 10px;
        }}
        .read-original {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); color: white;
            padding: 18px 40px; border-radius: 35px; text-decoration: none;
            display: inline-flex; align-items: center; gap: 12px; font-weight: 700;
            font-size: 1.2em; transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }}
        .read-original:hover {{ 
            transform: translateY(-3px); 
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }}
        .additional-info {{
            background: rgba(0,0,0,0.03); padding: 25px; border-radius: 15px;
            margin: 30px 0; border-left: 5px solid #667eea;
        }}
        .additional-info h4 {{ color: #667eea; margin-bottom: 15px; font-size: 1.3em; }}
        .additional-info p {{ color: #555; line-height: 1.6; }}
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            .article {{ padding: 30px 25px; }}
            .article-title {{ font-size: 2em; }}
            .article-meta {{ flex-direction: column; align-items: flex-start; }}
            .back-btn {{ padding: 12px 24px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-btn">
            <span>←</span>
            <span>返回首页</span>
        </a>
        
        <div class="article">
            <h1 class="article-title">{display_title}</h1>
            
            {f'<div class="original-title">原文标题: {original_title}</div>' if original_title else ''}
            
            <div class="article-meta">
                <div class="meta-left">
                    <span class="article-source">{article.get('source', '未知来源')}</span>
                    <span class="article-time">{article.get('time', '未知时间')}</span>
                </div>
                <div class="article-category">
                    <span>{article.get('category_icon', '📰')}</span>
                    <span>{article.get('category', '未分类')}</span>
                </div>
            </div>
            
            <div class="article-content">
                <p>{display_summary}</p>
            </div>
            
            {('<div class="ai-commentary"><div class="ai-commentary-content">' + article['ai_commentary'] + '</div></div>') if article.get('ai_commentary') else ''}
            
            <div class="additional-info">
                <h4>📊 文章信息</h4>
                <p><strong>新闻来源:</strong> {article.get('source', '未知来源')}</p>
                <p><strong>发布时间:</strong> {article.get('publishedAt', '未知')}</p>
                <p><strong>新闻分类:</strong> {article.get('category', '未分类')}</p>
                <p><strong>翻译状态:</strong> {'✅ 已翻译' if article.get('translated_title') else '❌ 原文'}</p>
                <p><strong>AI点评:</strong> {'✅ 已生成' if article.get('ai_commentary') else '❌ 暂无'}</p>
            </div>
            
            <a href="{article.get('url', '#')}" target="_blank" class="read-original">
                <span>🔗</span>
                <span>阅读英文原文</span>
                <span>→</span>
            </a>
        </div>
    </div>
</body>
</html>'''
    return html

def main():
    """主函数 - 用户体验优化版"""
    print("🚀 用户体验优化版 - AI新闻推送系统")
    print("=" * 60)
    
    try:
        # 1. 加载环境变量
        load_env_file()
        
        # 2. 初始化API服务
        gnews_api_key = os.getenv('GNEWS_API_KEY')
        siliconflow_api_key = os.getenv('SILICONFLOW_API_KEY')
        
        if not gnews_api_key:
            print("❌ 缺少GNEWS_API_KEY")
            return False
        
        # 3. 创建目录
        os.makedirs('docs', exist_ok=True)
        os.makedirs('docs/news', exist_ok=True)
        
        # 4. 获取分类新闻
        articles = fetch_categorized_news(gnews_api_key)
        
        if not articles:
            print("❌ 未获取到新闻")
            return False
        
        # 5. 翻译和AI点评
        if siliconflow_api_key:
            translator = SiliconFlowTranslator(siliconflow_api_key)
            commentator = AICommentator(siliconflow_api_key)
            articles = translate_and_enhance_articles(articles, translator, commentator)
        else:
            print("⚠️ 未配置翻译API，跳过翻译和点评")
        
        # 6. 生成用户友好的HTML页面
        print("\n🎨 生成用户友好的网页...")
        html_content = generate_user_friendly_html(articles)
        
        with open('docs/index.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 7. 生成增强的详情页
        print("📄 生成详情页...")
        for article in articles:
            detail_html = generate_enhanced_detail_page(article)
            detail_path = f"docs/news/{article['id']}.html"
            with open(detail_path, 'w', encoding='utf-8') as f:
                f.write(detail_html)
        
        # 8. 保存数据
        news_data = {
            'last_updated': datetime.now().isoformat(),
            'total_count': len(articles),
            'translated_count': len([a for a in articles if a.get('translated_title')]),
            'commentary_count': len([a for a in articles if a.get('ai_commentary')]),
            'categories': list(get_news_categories().keys()),
            'articles': articles
        }
        
        with open('docs/news_data.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2, default=str)
        
        # 9. 最终报告
        print("\n" + "=" * 60)
        print("🎉 用户体验优化版生成完成！")
        print("=" * 60)
        print(f"📰 总新闻数: {len(articles)}")
        print(f"🌐 翻译文章: {len([a for a in articles if a.get('translated_title')])}")
        print(f"🤖 AI点评: {len([a for a in articles if a.get('ai_commentary')])}")
        print(f"📁 详情页面: {len(articles)}")
        print(f"🎯 新闻分类: {len(get_news_categories())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统运行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)