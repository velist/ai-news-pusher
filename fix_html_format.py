#!/usr/bin/env python3
"""
改进版本 - 修复所有新闻详情页的markdown格式问题
"""

import os
import json
import re
from pathlib import Path

def fix_extended_content_format(content):
    """修复扩展内容中嵌套的HTML标签问题"""
    
    # 修复嵌套在p标签内的h4和h5标签
    content = re.sub(r'<p><h4>([^<]+)</h4></p>', r'<h4>\1</h4>', content)
    content = re.sub(r'<p><h5>([^<]+)</h5></p>', r'<h5>\1</h5>', content)
    
    # 修复多余的空p标签
    content = re.sub(r'<p></p>', '', content)
    content = re.sub(r'<p>\s*</p>', '', content)
    
    return content

def main():
    """修复所有页面的格式问题"""
    
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
            
            # 修复扩展内容格式问题
            content = fix_extended_content_format(content)
            
            # 保存修复后的内容
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ 修复失败 {html_file}: {e}")
    
    print(f"\n🎉 格式修复完成!")
    print(f"✅ 成功修复: {success_count} 个文件")
    print(f"❌ 修复失败: {len(html_files) - success_count} 个文件")

if __name__ == "__main__":
    main()