#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复HTML生成脚本 - 确保正确显示中文内容
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path

def load_env_file():
    """加载环境变量"""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("环境变量加载完成")
    else:
        print("警告：.env文件不存在")

def convert_markdown_to_html(text):
    """将简单的markdown格式转换为HTML"""
    if not text:
        return ""
    
    # 处理粗体 **text** -> <strong>text</strong>
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # 处理换行
    text = text.replace('\n\n', '</p><p>')
    text = text.replace('\n', '<br>')
    
    # 包装在段落标签中
    if text and not text.startswith('<p>'):
        text = f'<p>{text}</p>'
    
    return text

def generate_enhanced_html():
    """生成增强版HTML页面"""
    print("开始生成增强版HTML页面...")
    
    docs_dir = Path("docs")
    
    # 优先使用enhanced_chinese_news_data.json，如果不存在则使用news_data.json
    enhanced_data_file = docs_dir / "enhanced_chinese_news_data.json"
    news_data_file = docs_dir / "news_data.json"
    
    if enhanced_data_file.exists():
        with open(enhanced_data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # enhanced_chinese_news_data.json的结构包含articles数组
        if isinstance(data, dict) and 'articles' in data:
            news_data = data['articles']
        else:
            news_data = data
        print(f"使用enhanced_chinese_news_data.json，包含 {len(news_data)} 条新闻")
    elif news_data_file.exists():
        with open(news_data_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        print(f"使用news_data.json，包含 {len(news_data)} 条新闻")
    else:
        print("错误：找不到新闻数据文件")
        return False
    
    # 按类别分组新闻
    categories = {}
    for item in news_data:
        # 优先使用中文分类
        category = item.get('category_chinese', item.get('category', 'AI科技'))
        if isinstance(category, dict):
            category = category.get('name', 'AI科技')
        
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    print(f"发现 {len(categories)} 个类别: {list(categories.keys())}")
    
    # 生成主页HTML
    html_content = generate_index_html(categories)
    
    # 写入index.html
    index_file = docs_dir / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 生成详情页
    generate_detail_pages(news_data)
    
    print("HTML页面生成完成")
    return True

def generate_index_html(categories):
    """生成主页HTML"""
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 中文智能新闻</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .update-time {
            color: #888;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .tab {
            padding: 12px 24px;
            background: transparent;
            border: 2px solid #ddd;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            color: #666;
        }
        
        .tab.active {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-color: transparent;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .tab:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .news-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .news-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .news-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .news-meta {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        
        .freshness-score {
            background: linear-gradient(45deg, #10B981, #059669);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 500;
        }
        
        .news-source {
            color: #667eea;
            font-weight: 500;
            font-size: 0.9em;
        }
        
        .news-time {
            color: #888;
            font-size: 0.9em;
        }
        
        .news-description {
            color: #555;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .category-content {
            display: none;
        }
        
        .category-content.active {
            display: block;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .tabs {
                justify-content: flex-start;
                overflow-x: auto;
                padding: 10px;
            }
            
            .news-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p>智能翻译 · 中文本地化 · AI点评 · 实时更新</p>
            <div class="update-time">最后更新：''' + datetime.now().strftime("%Y年%m月%d日 %H:%M") + '''</div>
        </div>
        
        <div class="tabs">
'''
    
    # 添加标签页
    tab_index = 0
    for category in categories.keys():
        active_class = "active" if tab_index == 0 else ""
        # 为类别添加图标
        icon = "🤖" if "AI" in category else "📊" if "经济" in category else "🎮" if "游戏" in category else "🔬"
        html += f'            <div class="tab {active_class}" onclick="showCategory(\'{category}\')"> {icon} {category}</div>\n'
        tab_index += 1
    
    html += '''        </div>
        
'''
    
    # 添加每个类别的内容
    content_index = 0
    for category, items in categories.items():
        active_class = "active" if content_index == 0 else ""
        html += f'        <div id="{category}" class="category-content {active_class}">\n'
        html += '            <div class="news-grid">\n'
        
        for item in items[:12]:  # 每个类别最多显示12条
            # 优先使用中文字段，否则使用英文字段
            title = item.get('ai_translation', {}).get('translated_title', item.get('title', '无标题'))
            
            # 处理描述字段
            description = item.get('ai_translation', {}).get('translated_description', item.get('description', '无描述'))
            
            source_info = item.get('source', {})
            if isinstance(source_info, dict):
                source = source_info.get('name', '未知来源')
            else:
                source = str(source_info) if source_info else '未知来源'
            time_str = item.get('time_info', {}).get('relative', item.get('relative_time', item.get('time', '未知时间')))
            freshness = item.get('freshness_score', 0.5)
            article_id = item.get('id', '')
            
            html += f'''                <div class="news-card" data-article-id="{article_id}" onclick="openNews('{article_id}')">
                    <div class="news-title">{title}</div>
                    <div class="news-meta">
                        <span class="freshness-score">新鲜度: {freshness:.2f}</span>
                        <span class="news-source">{source}</span>
                        <span class="news-time">{time_str}</span>
                    </div>
                    <div class="news-description">{description}</div>
                </div>
'''
        
        html += '            </div>\n'
        html += '        </div>\n\n'
        content_index += 1
    
    html += '''    </div>
    
    <script>
        function showCategory(category) {
            // 隐藏所有内容
            const contents = document.querySelectorAll('.category-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // 移除所有标签的active状态
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // 显示选中的内容
            document.getElementById(category).classList.add('active');
            
            // 激活选中的标签
            event.target.classList.add('active');
        }
        
        function openNews(articleId) {
            if (articleId) {
                window.open(`news/${articleId}.html`, '_blank');
            }
        }
    </script>
</body>
</html>'''
    
    return html

def generate_detail_pages(news_data):
    """生成详情页"""
    news_dir = Path("docs/news")
    news_dir.mkdir(exist_ok=True)
    
    for item in news_data:
        article_id = item.get('id', '')
        if not article_id:
            continue
            
        # 优先使用中文字段
        title = item.get('ai_translation', {}).get('translated_title', item.get('title', '无标题'))
        # 丰富正文内容：结合翻译描述和原始内容
        translated_desc = item.get('ai_translation', {}).get('translated_description', '')
        original_content = item.get('content', item.get('description', ''))
        
        # 构建更丰富的正文内容
        content_parts = []
        if translated_desc and translated_desc.strip():
            content_parts.append(translated_desc)
        
        # 如果原始内容存在且与翻译描述不同，添加更多信息
        if original_content and original_content.strip():
            # 截取原始内容的前500字符作为补充
            additional_content = original_content[:500]
            if additional_content != translated_desc:
                content_parts.append(f"\n\n根据原文报道，{additional_content}...")
        
        # 如果仍然没有足够内容，添加基于标题的扩展描述
        if len(''.join(content_parts)) < 100:
            content_parts.append(f"\n\n这是一篇关于{title}的重要科技新闻报道。该新闻涉及当前科技行业的最新发展动态，值得关注。")
        
        content = ''.join(content_parts) if content_parts else '暂无详细内容'
        source_info = item.get('source', {})
        if isinstance(source_info, dict):
            source = source_info.get('name', '未知来源')
        else:
            source = str(source_info) if source_info else '未知来源'
        url = item.get('url', '#')
        time_str = item.get('time_info', {}).get('relative', item.get('relative_time', item.get('time', '未知时间')))
        category = item.get('category_chinese', item.get('category', 'AI科技'))
        if isinstance(category, dict):
            category = category.get('name', 'AI科技')
        
        # AI点评 - 处理markdown格式
        ai_commentary = ""
        if 'ai_commentary' in item and item['ai_commentary'].get('success'):
            raw_commentary = item['ai_commentary'].get('commentary', '')
            # 将markdown格式转换为HTML
            ai_commentary = convert_markdown_to_html(raw_commentary)
        
        detail_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AI科技日报</title>
    <style>
        body {{
            font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .back-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }}
        
        .back-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .article-header {{
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .article-title {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            line-height: 1.3;
        }}
        
        .article-meta {{
            display: flex;
            align-items: center;
            gap: 15px;
            color: #666;
            flex-wrap: wrap;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .category-tag {{
            background: linear-gradient(45deg, #10B981, #059669);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        
        .article-content {{
            font-size: 1.1em;
            color: #444;
            margin-bottom: 30px;
            text-align: justify;
        }}
        
        .ai-commentary {{
            background: linear-gradient(135deg, #e8f4fd 0%, #f0f9ff 100%);
            border-left: 4px solid #667eea;
            padding: 25px;
            margin: 30px 0;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        }}
        
        .ai-commentary h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .original-link {{
            text-align: center;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #eee;
        }}
        
        .original-btn {{
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }}
        
        .original-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}
            
            .article-title {{
                font-size: 1.5em;
            }}
            
            .article-meta {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-btn">← 返回首页</a>
        
        <div class="article-header">
            <h1 class="article-title">{title}</h1>
            <div class="article-meta">
                <div class="meta-item">
                    <span class="category-tag">{category}</span>
                </div>
                <div class="meta-item">
                    <span>📰 {source}</span>
                </div>
                <div class="meta-item">
                    <span>🕒 {time_str}</span>
                </div>
            </div>
        </div>
        
        <div class="article-content">
            {content}
        </div>
'''
        
        if ai_commentary:
            detail_html += f'''
        <div class="ai-commentary">
            <h3>🤖 AI智能点评</h3>
            <div class="commentary-content">{ai_commentary}</div>
        </div>
'''
        
        detail_html += f'''
        <div class="original-link">
            <a href="{url}" target="_blank" class="original-btn">📖 阅读原文</a>
        </div>
    </div>
</body>
</html>'''
        
        # 写入详情页文件
        detail_file = news_dir / f"{article_id}.html"
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write(detail_html)

if __name__ == "__main__":
    load_env_file()
    generate_enhanced_html()
    print("HTML修复完成！")