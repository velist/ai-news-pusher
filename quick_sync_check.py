#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查Vercel同步状态
"""

import urllib.request
import time
from datetime import datetime

def quick_check():
    """快速检查两个平台的状态"""
    print("🔍 快速同步状态检查")
    print("=" * 50)
    
    try:
        # 检查Vercel
        print("🌐 检查Vercel...")
        with urllib.request.urlopen("https://ai-news-pusher.vercel.app", timeout=10) as response:
            vercel_content = response.read().decode('utf-8')
        vercel_length = len(vercel_content)
        
        # 检查GitHub Pages
        print("📱 检查GitHub Pages...")
        with urllib.request.urlopen("https://velist.github.io/ai-news-pusher/docs/", timeout=10) as response:
            github_content = response.read().decode('utf-8')
        github_length = len(github_content)
        
        # 比较结果
        print(f"\n📊 内容长度对比:")
        print(f"   Vercel: {vercel_length:,} 字符")
        print(f"   GitHub Pages: {github_length:,} 字符")
        
        if vercel_length == github_length:
            print("🎉 完全同步！内容长度完全一致")
            return "完全同步"
        else:
            diff = abs(vercel_length - github_length)
            similarity = 1 - (diff / max(vercel_length, github_length))
            print(f"   差异: {diff:,} 字符")
            print(f"   相似度: {similarity:.2%}")
            
            if similarity > 0.95:
                print("✅ 基本同步！内容基本一致")
                return "基本同步"
            elif similarity > 0.8:
                print("⚠️ 部分同步，仍有差异")
                return "部分同步"
            else:
                print("❌ 仍未同步，差异较大")
                return "未同步"
                
    except Exception as e:
        print(f"❌ 检查失败: {str(e)}")
        return "检查失败"

def main():
    """主检查流程"""
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 等待一段时间让部署开始
    print("\n⏳ 等待30秒让Vercel开始处理...")
    time.sleep(30)
    
    # 进行3次检查，间隔1分钟
    for i in range(3):
        print(f"\n🔍 第 {i+1} 次检查:")
        result = quick_check()
        
        if result in ["完全同步", "基本同步"]:
            print(f"\n🎉 同步成功！状态: {result}")
            print("✅ Vercel已成功同步GitHub Pages内容")
            break
        elif i < 2:
            print(f"\n⏳ 等待60秒后进行下一次检查...")
            time.sleep(60)
        else:
            print(f"\n⚠️ 3次检查后状态: {result}")
            print("💡 可能需要手动在Vercel控制台触发部署")
    
    print(f"\n⏰ 检查完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🌐 访问链接:")
    print("   📱 Vercel: https://ai-news-pusher.vercel.app")
    print("   📊 GitHub Pages: https://velist.github.io/ai-news-pusher/docs/")
    print("   🔧 Vercel控制台: https://vercel.com/dashboard")

if __name__ == "__main__":
    main()