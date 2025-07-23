#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用现有数据重新生成HTML页面
"""

import json
import os
from optimized_html_generator import AppleStyleNewsGenerator

def regenerate_html():
    """使用现有的新闻数据重新生成HTML页面"""
    try:
        # 读取现有的新闻数据
        with open('docs/news_data.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print("📖 读取现有新闻数据...")
    except FileNotFoundError:
        print("❌ 未找到现有新闻数据文件")
        return False
    
    if not articles:
        print("❌ 新闻数据为空")
        return False
    
    generator = AppleStyleNewsGenerator()
    
    # 使用现有方法生成HTML
    print("🎨 正在生成页面...")
    success = generator.generate_optimized_html(articles)
    
    if success:
        print("✅ 页面重新生成完成:")
        print("   📄 首页: docs/index.html")
        print(f"   📰 详情页: docs/news/ ({len(articles)} 篇)")
        print("🎉 使用现有数据重新生成完成！")
        return True
    else:
        print("❌ 页面生成失败")
        return False

if __name__ == "__main__":
    regenerate_html()