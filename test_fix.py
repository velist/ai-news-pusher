#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复版本
"""

import os
import json
from datetime import datetime, timedelta

def main():
    print("🚀 启动测试版本...")
    
    # 检查API密钥
    api_key = os.getenv('GNEWS_API_KEY')
    if not api_key:
        print("⚠️ GNEWS_API_KEY环境变量未设置，将使用示例数据")
    
    try:
        # 生成示例文章
        articles = [
            {
                "id": "test_1",
                "title": "测试新闻1",
                "summary": "这是一条测试新闻",
                "source": "测试来源",
                "url": "#",
                "category": "AI技术",
                "time": "刚刚",
                "added_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        # 确保目录存在
        os.makedirs('docs', exist_ok=True)
        os.makedirs('docs/news', exist_ok=True)
        
        # 生成详情页面
        for article in articles:
            detail_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{article['title']} - AI科技日报</title>
</head>
<body>
    <h1>{article['title']}</h1>
    <p>{article['summary']}</p>
    <a href="../index.html">返回首页</a>
</body>
</html>'''
            
            detail_path = f"docs/news/{article['id']}.html"
            with open(detail_path, 'w', encoding='utf-8') as f:
                f.write(detail_html)
        
        print(f"✅ 测试成功！生成了 {len(articles)} 个详情页面")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 测试完成！")
    else:
        print("❌ 测试失败！")