#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import shutil
from pathlib import Path

def cleanup_old_files():
    """删除旧版本文件"""
    files_to_remove = [
        'test_translation_ui.html',
        'index.html'  # 根目录的重定向文件
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ 已删除: {file_path}")
        else:
            print(f"ℹ️  文件不存在: {file_path}")

def verify_vercel_config():
    """验证Vercel配置"""
    vercel_config = {
        "version": 2,
        "name": "ai-news-pusher",
        "public": True,
        "github": {
            "enabled": True,
            "autoAlias": True
        },
        "buildCommand": "echo 'Static site - no build needed'",
        "outputDirectory": "docs",
        "rewrites": [
            {
                "source": "/",
                "destination": "/index.html"
            },
            {
                "source": "/news/(.*)",
                "destination": "/news/$1"
            }
        ],
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {
                        "key": "Cache-Control",
                        "value": "public, max-age=3600"
                    },
                    {
                        "key": "X-Content-Type-Options",
                        "value": "nosniff"
                    }
                ]
            }
        ],
        "cleanUrls": True,
        "trailingSlash": False
    }
    
    with open('vercel.json', 'w', encoding='utf-8') as f:
        json.dump(vercel_config, f, indent=2, ensure_ascii=False)
    
    print("✅ Vercel配置已更新")

def verify_docs_structure():
    """验证docs目录结构"""
    docs_path = Path('docs')
    
    if not docs_path.exists():
        print("❌ docs目录不存在")
        return False
    
    index_file = docs_path / 'index.html'
    if not index_file.exists():
        print("❌ docs/index.html不存在")
        return False
    
    news_dir = docs_path / 'news'
    if not news_dir.exists():
        print("❌ docs/news目录不存在")
        return False
    
    print("✅ docs目录结构正确")
    return True

def create_vercel_ignore():
    """创建.vercelignore文件"""
    ignore_content = """# 忽略不需要部署的文件
test_*.html
test_*.py
*.py
*.md
*.bak
translation/
old_files/
archive/
.env*
.git/
.github/
.claude/
.kiro/
*.png
*.jpg
*.jpeg
*.gif
素材/
反馈*.png
部署错误*.png
重复错误*.png
重建提示.png
邮件提醒*.png
内容模糊.png
千篇一律引发关注.png
"""
    
    with open('.vercelignore', 'w', encoding='utf-8') as f:
        f.write(ignore_content)
    
    print("✅ 已创建.vercelignore文件")

def main():
    print("🚀 开始清理和修复Vercel部署...")
    
    # 1. 清理旧文件
    cleanup_old_files()
    
    # 2. 验证docs结构
    if not verify_docs_structure():
        print("❌ docs目录结构有问题，请检查")
        return
    
    # 3. 更新Vercel配置
    verify_vercel_config()
    
    # 4. 创建.vercelignore
    create_vercel_ignore()
    
    print("\n✅ 清理和修复完成！")
    print("\n📋 接下来的步骤：")
    print("1. 运行: git add .")
    print("2. 运行: git commit -m 'fix: 清理旧文件并修复Vercel部署配置'")
    print("3. 运行: git push")
    print("4. 在Vercel控制台重新部署项目")
    
    print("\n🎯 部署要点：")
    print("- 输出目录: docs")
    print("- 主页面: docs/index.html (包含tab分类功能)")
    print("- 新闻详情: docs/news/*.html (中文内容)")
    print("- 原文链接: 点击'阅读原文'跳转")

if __name__ == "__main__":
    main()