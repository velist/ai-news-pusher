#!/usr/bin/env python3
"""
修复所有新闻详情页的格式问题
1. 调整标题大小
2. 修复markdown格式显示
3. 优化样式
"""

import os
import json
import re
from pathlib import Path

def fix_news_page(file_path, article_data):
    """修复单个新闻页面"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 修复标题样式 - 从2.5em改为1.8em
        content = re.sub(
            r'font-size: 2\.5em; font-weight: 800;',
            'font-size: 1.8em; font-weight: 700;',
            content
        )
        
        # 2. 修复扩展内容样式
        extended_content_style = """        .extended-content {
            background: rgba(118, 75, 162, 0.05);
            padding: 25px; border-radius: 15px; margin-bottom: 30px;
            border-left: 4px solid #764ba2;
        }
        
        .extended-content h4 {
            color: #333; font-size: 1.4em; margin: 25px 0 15px 0;
            font-weight: 600;
        }
        
        .extended-content h5 {
            color: #667eea; font-size: 1.2em; margin: 20px 0 10px 0;
            font-weight: 600;
        }
        
        .extended-content p {
            font-size: 1em; line-height: 1.7; margin-bottom: 15px;
            color: #555;
        }
        
        .extended-content ul {
            margin: 15px 0; padding-left: 20px;
        }
        
        .extended-content li {
            font-size: 1em; line-height: 1.6; margin-bottom: 8px;
            color: #555;
        }"""
        
        # 替换扩展内容样式
        content = re.sub(
            r'        \.extended-content \{[^}]*\}',
            extended_content_style,
            content,
            flags=re.DOTALL
        )
        
        # 3. 修复markdown格式显示问题
        if article_data and 'extended_content' in article_data:
            extended_content = article_data['extended_content']
            if extended_content:
                # 将markdown格式转换为HTML
                html_content = convert_markdown_to_html(extended_content)
                
                # 查找并替换扩展内容
                pattern = r'<div class="extended-content">.*?</div>'
                replacement = f'<div class="extended-content">\n                <h3>📊 深度分析</h3>\n{html_content}\n            </div>'
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # 保存修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 修复完成: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败 {file_path}: {e}")
        return False

def convert_markdown_to_html(markdown_text):
    """将markdown文本转换为HTML"""
    html = markdown_text
    
    # 转换标题
    html = re.sub(r'^### ([^\n]+)', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### ([^\n]+)', r'<h5>🔍 \1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^##### ([^\n]+)', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    
    # 转换加粗文本
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
    
    # 转换列表
    lines = html.split('\n')
    result_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if line.startswith('- '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            result_lines.append(f'    <li>{line[2:]}</li>')
        else:
            if in_list:
                result_lines.append('</ul>')
                in_list = False
            if line:
                result_lines.append(f'<p>{line}</p>')
    
    if in_list:
        result_lines.append('</ul>')
    
    return '\n                '.join(result_lines)

def main():
    # 读取新闻数据
    data_file = Path('docs/enhanced_news_data.json')
    if not data_file.exists():
        print("❌ 找不到新闻数据文件")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    # 创建文章ID到数据的映射
    articles_map = {article['id']: article for article in news_data['articles']}
    
    # 获取所有新闻页面文件
    news_dir = Path('docs/news')
    if not news_dir.exists():
        print("❌ 找不到新闻目录")
        return
    
    html_files = list(news_dir.glob('*.html'))
    print(f"📋 找到 {len(html_files)} 个新闻页面文件")
    
    success_count = 0
    
    for html_file in html_files:
        # 从文件名提取文章ID
        article_id = html_file.stem
        article_data = articles_map.get(article_id)
        
        if fix_news_page(html_file, article_data):
            success_count += 1
    
    print(f"\n🎉 批量修复完成!")
    print(f"✅ 成功修复: {success_count} 个文件")
    print(f"❌ 修复失败: {len(html_files) - success_count} 个文件")

if __name__ == "__main__":
    main()