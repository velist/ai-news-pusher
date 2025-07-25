#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel同步测试脚本
"""

import subprocess
import json
import os
from datetime import datetime

def check_vercel_config():
    """检查Vercel配置"""
    print("🔍 检查Vercel配置文件...")
    
    if os.path.exists("vercel.json"):
        with open("vercel.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ vercel.json 配置:")
        print(f"   📦 项目名称: {config.get('name', 'N/A')}")
        print(f"   🌐 公开状态: {config.get('public', 'N/A')}")
        print(f"   🔗 GitHub集成: {config.get('github', {}).get('enabled', 'N/A')}")
        print(f"   📁 路由数量: {len(config.get('routes', []))}")
        
        # 检查路由配置
        routes = config.get('routes', [])
        for i, route in enumerate(routes):
            print(f"   📍 路由{i+1}: {route.get('src', 'N/A')} -> {route.get('dest', 'N/A')}")
        
        return True
    else:
        print("❌ vercel.json 文件不存在")
        return False

def check_docs_structure():
    """检查docs目录结构"""
    print("\n📁 检查docs目录结构...")
    
    if not os.path.exists("docs"):
        print("❌ docs目录不存在")
        return False
    
    required_files = [
        "docs/index.html",
        "docs/enhanced_news_data.json",
        "docs/news_data.json"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {size:,} 字节")
        else:
            print(f"❌ {file_path}: 不存在")
    
    # 检查news子目录
    news_dir = "docs/news"
    if os.path.exists(news_dir):
        news_files = [f for f in os.listdir(news_dir) if f.endswith('.html')]
        print(f"✅ {news_dir}: {len(news_files)} 个新闻页面")
    else:
        print(f"❌ {news_dir}: 不存在")
    
    return True

def test_github_pages():
    """测试GitHub Pages访问"""
    print("\n🌐 测试GitHub Pages访问...")
    
    try:
        import urllib.request
        url = "https://velist.github.io/ai-news-pusher/"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode('utf-8')
            
        if "AI科技日报" in content:
            print(f"✅ GitHub Pages正常访问: {url}")
            
            # 检查内容特征
            if "硅基流动" in content or "siliconflow" in content.lower():
                print("✅ 包含AI翻译标识")
            else:
                print("⚠️ 未找到AI翻译标识")
                
            return True
        else:
            print("⚠️ GitHub Pages可访问但内容异常")
            return False
            
    except Exception as e:
        print(f"❌ GitHub Pages访问失败: {str(e)}")
        return False

def create_vercel_deployment_trigger():
    """创建Vercel部署触发文件"""
    print("\n🚀 创建Vercel部署触发...")
    
    # 创建一个小的更新来触发Vercel重新部署
    trigger_file = "docs/.vercel-trigger"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(trigger_file, 'w', encoding='utf-8') as f:
        f.write(f"Vercel部署触发时间: {timestamp}\n")
        f.write("此文件用于触发Vercel重新部署\n")
    
    print(f"✅ 创建触发文件: {trigger_file}")
    return trigger_file

def run_git_operations():
    """执行Git操作"""
    print("\n📤 执行Git提交和推送...")
    
    try:
        # 添加所有文件
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        print("✅ 文件已添加到Git")
        
        # 提交更改
        commit_msg = f"🔄 触发Vercel同步 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(["git", "commit", "-m", commit_msg], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 提交成功")
            
            # 推送到GitHub
            push_result = subprocess.run(["git", "push"], 
                                       capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("✅ 推送到GitHub成功")
                return True
            else:
                print(f"❌ 推送失败: {push_result.stderr}")
                return False
        else:
            if "nothing to commit" in result.stdout:
                print("ℹ️ 没有新的更改需要提交")
                return True
            else:
                print(f"❌ 提交失败: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Git操作异常: {str(e)}")
        return False

def provide_vercel_troubleshooting():
    """提供Vercel故障排除建议"""
    print("\n🔧 Vercel同步故障排除建议:")
    print("=" * 60)
    
    print("1. 检查Vercel项目设置:")
    print("   • 访问 https://vercel.com/dashboard")
    print("   • 确认项目已连接到正确的GitHub仓库")
    print("   • 检查 'Git Integration' 设置是否启用")
    
    print("\n2. 检查部署设置:")
    print("   • Framework Preset: 选择 'Other' 或 'Static'")
    print("   • Build Command: 留空")
    print("   • Output Directory: docs")
    print("   • Install Command: 留空")
    
    print("\n3. 环境变量配置:")
    print("   • GNEWS_API_KEY: c3cb6fef0f86251ada2b515017b97143")
    print("   • SILICONFLOW_API_KEY: sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa")
    
    print("\n4. 手动触发部署:")
    print("   • 在Vercel项目页面点击 'Redeploy'")
    print("   • 或者在GitHub推送新的commit")
    
    print("\n5. 检查部署日志:")
    print("   • 在Vercel项目页面查看 'Functions' 和 'Deployments' 日志")
    print("   • 查找错误信息和警告")
    
    print("\n6. 验证文件结构:")
    print("   • 确保docs/index.html存在且内容正确")
    print("   • 确保vercel.json配置正确")
    print("   • 检查文件权限和编码")

def main():
    """主测试流程"""
    print("🚀 Vercel同步诊断测试")
    print("=" * 60)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 检查配置
    vercel_config_ok = check_vercel_config()
    
    # 2. 检查文件结构
    docs_structure_ok = check_docs_structure()
    
    # 3. 测试GitHub Pages
    github_pages_ok = test_github_pages()
    
    # 4. 创建部署触发
    trigger_file = create_vercel_deployment_trigger()
    
    # 5. 执行Git操作
    git_ok = run_git_operations()
    
    # 6. 提供故障排除建议
    provide_vercel_troubleshooting()
    
    # 总结
    print("\n📊 诊断结果总结:")
    print("=" * 60)
    print(f"✅ Vercel配置: {'正常' if vercel_config_ok else '异常'}")
    print(f"✅ 文件结构: {'正常' if docs_structure_ok else '异常'}")
    print(f"✅ GitHub Pages: {'正常' if github_pages_ok else '异常'}")
    print(f"✅ Git操作: {'成功' if git_ok else '失败'}")
    
    if all([vercel_config_ok, docs_structure_ok, github_pages_ok, git_ok]):
        print("\n🎉 所有检查通过！Vercel应该会在几分钟内同步")
        print("💡 如果Vercel仍未同步，请手动在Vercel控制台触发重新部署")
    else:
        print("\n⚠️ 发现问题，请根据上述建议进行修复")
    
    print(f"\n🎯 下一步: 等待5-10分钟后检查Vercel部署状态")
    print(f"📱 GitHub Pages: https://velist.github.io/ai-news-pusher/")

if __name__ == "__main__":
    main()