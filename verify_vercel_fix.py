#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Vercel schema修复结果
"""

import time
import urllib.request
import json
from datetime import datetime

def validate_vercel_config():
    """验证vercel.json配置"""
    print("🔍 验证vercel.json配置...")
    
    try:
        with open("vercel.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必需的属性
        required_props = ['version', 'name', 'public', 'github', 'routes', 'headers']
        missing_props = []
        
        for prop in required_props:
            if prop not in config:
                missing_props.append(prop)
        
        # 检查是否有无效属性
        invalid_props = []
        for key in config.keys():
            if key.startswith('_'):
                invalid_props.append(key)
        
        if missing_props:
            print(f"❌ 缺少必需属性: {', '.join(missing_props)}")
            return False
        
        if invalid_props:
            print(f"❌ 包含无效属性: {', '.join(invalid_props)}")
            return False
        
        print("✅ vercel.json配置验证通过")
        print(f"   📋 版本: {config.get('version')}")
        print(f"   📦 项目名: {config.get('name')}")
        print(f"   🌐 公开状态: {config.get('public')}")
        print(f"   📁 路由数量: {len(config.get('routes', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置验证失败: {str(e)}")
        return False

def check_vercel_deployment():
    """检查Vercel部署状态"""
    print("\n🌐 检查Vercel部署状态...")
    
    vercel_url = "https://ai-news-pusher.vercel.app"
    
    for attempt in range(3):
        try:
            print(f"   尝试 {attempt + 1}/3...")
            
            with urllib.request.urlopen(vercel_url, timeout=15) as response:
                content = response.read().decode('utf-8')
                status_code = response.getcode()
            
            if status_code == 200:
                if "AI科技日报" in content:
                    print(f"✅ Vercel部署成功: {vercel_url}")
                    
                    # 检查内容特征
                    features = []
                    if "硅基流动" in content or "AI翻译" in content:
                        features.append("AI翻译功能")
                    if "新闻" in content:
                        features.append("新闻内容")
                    if "响应式" in content or "mobile" in content.lower():
                        features.append("响应式设计")
                    
                    if features:
                        print(f"   🎯 包含功能: {', '.join(features)}")
                    
                    return True
                else:
                    print("⚠️ Vercel可访问但内容可能不完整")
                    if attempt < 2:
                        time.sleep(10)
                        continue
                    return False
            else:
                print(f"⚠️ HTTP状态码: {status_code}")
                if attempt < 2:
                    time.sleep(10)
                    continue
                return False
                
        except Exception as e:
            print(f"   ❌ 访问失败: {str(e)}")
            if attempt < 2:
                print("   ⏳ 等待10秒后重试...")
                time.sleep(10)
            else:
                print("   💡 可能还在构建中，请稍后再试")
                return False
    
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

def provide_troubleshooting():
    """提供故障排除指导"""
    print("\n🔧 故障排除指导:")
    print("=" * 50)
    
    print("📋 如果Vercel仍然构建失败:")
    print("   1. 访问 https://vercel.com/dashboard")
    print("   2. 找到ai-news-pusher项目")
    print("   3. 点击最新的部署查看详细日志")
    print("   4. 检查是否有其他配置错误")
    
    print("\n🔑 环境变量检查:")
    print("   确保在Vercel项目设置中配置了:")
    print("   • GNEWS_API_KEY")
    print("   • SILICONFLOW_API_KEY")
    
    print("\n📁 项目设置检查:")
    print("   • Framework Preset: Other")
    print("   • Build Command: (留空)")
    print("   • Output Directory: docs")
    print("   • Install Command: (留空)")
    
    print("\n🔄 手动重新部署:")
    print("   如果自动部署失败，可以:")
    print("   1. 在Vercel控制台点击'Redeploy'")
    print("   2. 或者推送一个新的commit触发部署")

def main():
    """主验证流程"""
    print("🚀 验证Vercel Schema修复结果")
    print("=" * 60)
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 验证配置文件
    config_valid = validate_vercel_config()
    
    # 2. 等待部署完成
    if config_valid:
        print("\n⏳ 等待Vercel构建完成...")
        print("   构建通常需要2-5分钟时间")
        time.sleep(30)  # 等待30秒让构建开始
    
    # 3. 检查Vercel部署
    vercel_ok = check_vercel_deployment()
    
    # 4. 检查GitHub Pages
    github_ok = check_github_pages()
    
    # 5. 提供故障排除指导
    if not vercel_ok:
        provide_troubleshooting()
    
    # 总结
    print("\n📊 验证结果总结:")
    print("=" * 60)
    
    print(f"✅ 配置文件: {'有效' if config_valid else '无效'}")
    print(f"✅ Vercel部署: {'成功' if vercel_ok else '失败/进行中'}")
    print(f"✅ GitHub Pages: {'正常' if github_ok else '异常'}")
    
    if config_valid and vercel_ok:
        print("\n🎉 修复完全成功！")
        print("💡 Vercel schema错误已解决")
        print("🌐 网站正常运行")
        
        print("\n🚀 系统特性:")
        print("   🤖 硅基流动AI翻译")
        print("   ✅ 真实新闻中文翻译")
        print("   🎯 智能质量评估")
        print("   📱 响应式H5界面")
        print("   ⏰ 自动更新机制")
        
    elif config_valid and not vercel_ok:
        print("\n⚠️ 配置已修复，但部署可能还在进行中")
        print("💡 请等待5-10分钟后再次检查")
        print("🔧 如果持续失败，请查看Vercel控制台日志")
        
    else:
        print("\n❌ 仍有问题需要解决")
        print("💡 请检查配置文件和部署设置")
    
    print("\n🌐 访问链接:")
    print("   📱 主要网站: https://ai-news-pusher.vercel.app")
    print("   📊 备用网站: https://velist.github.io/ai-news-pusher/docs/")
    print("   🔧 Vercel控制台: https://vercel.com/dashboard")
    
    print(f"\n⏰ 验证完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()