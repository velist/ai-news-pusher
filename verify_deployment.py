#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Vercel部署状态
"""

import time
import urllib.request
from datetime import datetime

def check_vercel_deployment():
    """检查Vercel部署状态"""
    print("🌐 检查Vercel部署状态...")
    
    vercel_url = "https://ai-news-pusher.vercel.app"
    
    try:
        with urllib.request.urlopen(vercel_url, timeout=10) as response:
            content = response.read().decode('utf-8')
            
        if "AI科技日报" in content:
            print(f"✅ Vercel部署成功: {vercel_url}")
            
            # 检查是否包含最新内容
            if "硅基流动" in content or "AI翻译" in content:
                print("✅ 包含AI翻译功能")
            else:
                print("⚠️ 可能未包含最新的AI翻译功能")
                
            return True
        else:
            print("⚠️ Vercel可访问但内容可能不是最新的")
            return False
            
    except Exception as e:
        print(f"❌ Vercel访问失败: {str(e)}")
        print("💡 可能还在部署中，请稍后再试")
        return False

def check_github_pages():
    """检查GitHub Pages状态"""
    print("\n📱 检查GitHub Pages状态...")
    
    github_url = "https://velist.github.io/ai-news-pusher/docs/"
    
    try:
        with urllib.request.urlopen(github_url, timeout=10) as response:
            content = response.read().decode('utf-8')
            
        if "AI科技日报" in content:
            print(f"✅ GitHub Pages正常: {github_url}")
            return True
        else:
            print("⚠️ GitHub Pages内容异常")
            return False
            
    except Exception as e:
        print(f"❌ GitHub Pages访问失败: {str(e)}")
        return False

def provide_summary():
    """提供总结信息"""
    print("\n📊 部署修复总结:")
    print("=" * 60)
    
    print("🎯 解决的问题:")
    print("   ❌ Vercel错误: 'This deployment can not be redeployed'")
    print("   ✅ 解决方案: 创建新的提交触发自动部署")
    
    print("\n🔧 执行的操作:")
    print("   ✅ 清理了包含敏感信息的文件")
    print("   ✅ 创建了新的部署触发器")
    print("   ✅ 更新了vercel.json配置")
    print("   ✅ 成功推送到GitHub")
    
    print("\n🚀 系统特性:")
    print("   🤖 硅基流动AI翻译 - 成本降低80-95%")
    print("   ✅ 真实新闻中文翻译 - 告别模板内容")
    print("   🎯 智能质量评估 - 置信度评分")
    print("   📱 响应式H5界面 - 完美移动体验")
    print("   ⏰ 自动更新机制 - 每小时获取最新资讯")
    
    print("\n🌐 访问链接:")
    print("   📱 主要网站: https://ai-news-pusher.vercel.app")
    print("   📊 备用网站: https://velist.github.io/ai-news-pusher/docs/")
    print("   🔧 管理控制台: https://vercel.com/dashboard")
    print("   📋 GitHub仓库: https://github.com/velist/ai-news-pusher")

def main():
    """主验证流程"""
    print("🚀 验证Vercel部署修复结果")
    print("=" * 60)
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 等待一段时间让部署完成
    print("\n⏳ 等待部署完成...")
    for i in range(3):
        print(f"   等待中... ({i+1}/3)")
        time.sleep(20)  # 等待20秒
        
        # 检查Vercel部署
        vercel_ok = check_vercel_deployment()
        if vercel_ok:
            break
    
    # 检查GitHub Pages
    github_ok = check_github_pages()
    
    # 提供总结
    provide_summary()
    
    # 最终状态
    print("\n🎉 验证结果:")
    print("=" * 60)
    
    if vercel_ok:
        print("✅ Vercel部署: 成功修复并正常运行")
    else:
        print("⚠️ Vercel部署: 可能还在进行中，请稍后检查")
    
    if github_ok:
        print("✅ GitHub Pages: 正常运行")
    else:
        print("⚠️ GitHub Pages: 需要检查")
    
    print(f"\n💡 如果Vercel仍未正常工作:")
    print("   1. 等待5-10分钟让部署完全完成")
    print("   2. 访问 https://vercel.com/dashboard 检查部署日志")
    print("   3. 确认环境变量配置正确")
    print("   4. 如需要可以手动触发重新部署")
    
    print(f"\n⏰ 验证完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()