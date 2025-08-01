#!/usr/bin/env python3
"""
进一步调整新闻详情页字体大小
"""

import os
import re
from pathlib import Path

def adjust_font_sizes(content):
    """调整字体大小"""
    
    # 调整文章内容基础字体大小 从1.2em降到1em
    content = re.sub(
        r'\.article-content \{\s*font-size: 1\.2em;',
        '.article-content {\n            font-size: 1em;',
        content
    )
    
    # 调整扩展内容段落字体 从1em降到0.95em
    content = re.sub(
        r'\.extended-content p \{\s*font-size: 1em;',
        '.extended-content p {\n            font-size: 0.95em;',
        content
    )
    
    # 调整扩展内容列表字体 从1em降到0.95em
    content = re.sub(
        r'\.extended-content li \{\s*font-size: 1em;',
        '.extended-content li {\n            font-size: 0.95em;',
        content
    )
    
    # 调整AI点评内容字体 从1.1em降到1em
    content = re.sub(
        r'\.ai-commentary-content \{\s*font-size: 1\.1em;',
        '.ai-commentary-content {\n            font-size: 1em;',
        content
    )
    
    # 调整内容区h3字体 从1.4em降到1.3em
    content = re.sub(
        r'\.content-section h3 \{\s*color: #667eea; font-size: 1\.4em;',
        '.content-section h3 {\n            color: #667eea; font-size: 1.3em;',
        content
    )
    
    # 调整扩展内容h4字体 从1.4em降到1.2em
    content = re.sub(
        r'\.extended-content h4 \{\s*color: #333; font-size: 1\.4em;',
        '.extended-content h4 {\n            color: #333; font-size: 1.2em;',
        content
    )
    
    # 调整扩展内容h5字体 从1.2em降到1.1em
    content = re.sub(
        r'\.extended-content h5 \{\s*color: #667eea; font-size: 1\.2em;',
        '.extended-content h5 {\n            color: #667eea; font-size: 1.1em;',
        content
    )
    
    return content

def main():
    """批量调整所有新闻页面字体大小"""
    
    news_dir = Path('docs/news')
    if not news_dir.exists():
        print("❌ 找不到新闻目录")
        return
    
    html_files = list(news_dir.glob('*.html'))
    print(f"📋 找到 {len(html_files)} 个新闻页面文件")
    
    success_count = 0
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 调整字体大小
            content = adjust_font_sizes(content)
            
            # 保存修改后的内容
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ 处理失败 {html_file}: {e}")
    
    print(f"\n🎉 字体调整完成!")
    print(f"✅ 成功处理: {success_count} 个文件")
    print(f"❌ 处理失败: {len(html_files) - success_count} 个文件")

if __name__ == "__main__":
    main()