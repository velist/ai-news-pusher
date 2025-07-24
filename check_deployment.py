#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署状态检查脚本
"""

import urllib.request
import json
import time
from datetime import datetime

def check_github_pages():
    """检查GitHub Pages状态"""
    print("🔍 检查GitHub Pages状态...")
    
    try:
        # 检查GitHub Pages是否可访问
        url = "https://velist.github.io/ai-news-pusher/"
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
            
        if "AI科技日报" in content:
            print("✅ GitHub Pages部署成功")
            print(f"   📱 访问地址: {url}")
            return True
        else:
            print("⚠️ GitHub Pages可访问但内容可能不是最新的")
            return False
            
    except Exception as e:
        print(f"❌ GitHub Pages访问失败: {str(e)}")
        return False

def check_github_actions():
    """检查GitHub Actions状态"""
    print("\n🔍 检查GitHub Actions状态...")
    print("📋 请手动检查以下链接:")
    print("   🔗 Actions页面: https://github.com/velist/ai-news-pusher/actions")
    print("   🔗 最新运行: https://github.com/velist/ai-news-pusher/actions/workflows/daily-news-push.yml")
    
    print("\n💡 如需手动触发:")
    print("   1. 访问上述Actions页面")
    print("   2. 点击 'AI新闻每日推送' workflow")
    print("   3. 点击 'Run workflow' 按钮")

def check_vercel_deployment():
    """检查Vercel部署建议"""
    print("\n🔍 Vercel部署检查...")
    print("📋 请检查以下配置:")
    print("   1. 访问 https://vercel.com/dashboard")
    print("   2. 确认项目已连接到GitHub仓库")
    print("   3. 检查最新部署状态")
    print("   4. 确认环境变量已配置:")
    print("      - GNEWS_API_KEY")
    print("      - SILICONFLOW_API_KEY")
    
    print("\n🔧 如果Vercel未自动更新:")
    print("   1. 在Vercel项目设置中点击 'Redeploy'")
    print("   2. 或者推送一个新的commit触发部署")

def main():
    """主检查流程"""
    print("🚀 AI新闻翻译系统部署状态检查")
    print("=" * 60)
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查GitHub Pages
    github_pages_ok = check_github_pages()
    
    # 检查GitHub Actions
    check_github_actions()
    
    # 检查Vercel部署
    check_vercel_deployment()
    
    # 总结
    print("\n📊 检查总结")
    print("=" * 60)
    
    if github_pages_ok:
        print("✅ GitHub Pages: 正常运行")
    else:
        print("⚠️ GitHub Pages: 需要检查")
    
    print("🔧 已修复的问题:")
    print("   ✅ Jekyll构建错误 - 排除了有问题的Markdown文件")
    print("   ✅ Vercel配置优化 - 改为静态文件部署")
    print("   ✅ 文件冲突解决 - 重命名了冲突文件")
    
    print("\n🎯 下一步建议:")
    print("   1. 等待5-10分钟让GitHub Actions和Vercel完成部署")
    print("   2. 手动触发GitHub Actions测试翻译系统")
    print("   3. 检查Vercel部署是否显示最新内容")
    print("   4. 如果问题持续，可以手动重新部署")
    
    print(f"\n🎉 检查完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()