#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制Vercel同步最新内容
解决GitHub Pages已更新但Vercel未同步的问题
"""

import os
import subprocess
import json
from datetime import datetime

def create_sync_trigger():
    """创建同步触发器"""
    print("🔄 创建Vercel同步触发器...")
    print("=" * 60)
    print("📋 问题描述:")
    print("   • GitHub Pages: 已部署新内容")
    print("   • Vercel: 未同步最新内容")
    print("   • 重新部署: 提示需要新提交")
    print("💡 解决方案: 创建新提交触发Vercel自动同步")
    
    # 1. 创建同步标记文件
    sync_file = "docs/.vercel-sync-trigger"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    sync_content = f"""# Vercel同步触发器

## 同步时间
{current_time}

## 同步原因
- GitHub Pages已部署新内容
- Vercel未自动同步
- 需要新提交触发Vercel重新部署

## 系统状态
- ✅ GitHub Pages: 最新内容已部署
- 🔄 Vercel: 等待同步
- 📱 用户体验: 需要统一两个平台的内容

## 预期结果
此提交将触发Vercel检测到变化并自动部署最新内容，
确保Vercel和GitHub Pages显示相同的最新内容。

## AI新闻翻译系统特性
- 🤖 硅基流动AI翻译
- ✅ 真实新闻中文翻译
- 🎯 智能质量评估
- 📱 响应式H5界面
- ⏰ 自动更新机制
"""
    
    with open(sync_file, 'w', encoding='utf-8') as f:
        f.write(sync_content)
    
    print(f"✅ 创建同步触发文件: {sync_file}")
    
    # 2. 更新部署时间戳
    timestamp_file = "docs/.deployment-sync-timestamp"
    with open(timestamp_file, 'w', encoding='utf-8') as f:
        f.write(f"Vercel同步时间: {current_time}\n")
        f.write("目的: 强制Vercel同步GitHub Pages最新内容\n")
        f.write("状态: 创建新提交触发自动部署\n")
    
    print(f"✅ 更新时间戳文件: {timestamp_file}")
    
    return [sync_file, timestamp_file]

def update_readme_sync_info():
    """更新README中的同步信息"""
    print("\n📝 更新README同步信息...")
    
    try:
        # 读取现有README
        if os.path.exists("README.md"):
            with open("README.md", 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # 添加同步状态信息
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sync_info = f"""

## 🔄 部署同步状态

**最后同步时间**: {current_time}

### 访问链接
- 🌐 **Vercel部署**: https://ai-news-pusher.vercel.app
- 📱 **GitHub Pages**: https://velist.github.io/ai-news-pusher/docs/

### 同步说明
此项目同时部署在Vercel和GitHub Pages上，确保两个平台内容保持同步。

### 系统特性
- 🤖 硅基流动AI翻译 - 成本降低80-95%
- ✅ 真实新闻中文翻译 - 告别模板内容
- 🎯 智能质量评估 - 置信度评分
- 📱 响应式H5界面 - 完美移动体验
- ⏰ 自动更新机制 - 每小时获取最新资讯

---
*最后更新: {current_time}*
"""
        
        # 如果README中已有同步状态部分，替换它
        if "## 🔄 部署同步状态" in content:
            # 找到同步状态部分并替换
            start_marker = "## 🔄 部署同步状态"
            if "---" in content[content.find(start_marker):]:
                end_marker = content[content.find(start_marker):].find("---") + content.find(start_marker) + 3
                # 找到下一行的开始
                next_line_start = content.find("\n", end_marker) + 1
                content = content[:content.find(start_marker)] + sync_info + content[next_line_start:]
            else:
                content = content[:content.find(start_marker)] + sync_info
        else:
            content += sync_info
        
        # 写回README
        with open("README.md", 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ README同步信息已更新")
        return True
        
    except Exception as e:
        print(f"⚠️ README更新失败: {str(e)}")
        return False

def commit_and_push_sync():
    """提交并推送同步更改"""
    print("\n📤 提交并推送同步更改...")
    
    try:
        # 添加所有文件
        subprocess.run(["git", "add", "."], check=True)
        print("✅ 文件已添加到Git")
        
        # 创建提交
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        commit_msg = f"🔄 强制Vercel同步最新内容 - {current_time}"
        
        result = subprocess.run(["git", "commit", "-m", commit_msg], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 提交成功")
            print(f"   📝 提交信息: {commit_msg}")
            
            # 推送到GitHub
            push_result = subprocess.run(["git", "push"], 
                                       capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("✅ 推送成功")
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
        print(f"❌ Git操作失败: {str(e)}")
        return False

def provide_sync_guidance():
    """提供同步指导"""
    print("\n🎯 Vercel同步指导:")
    print("=" * 60)
    
    print("📋 新提交已创建，Vercel应该会:")
    print("   1. 自动检测到新的提交")
    print("   2. 触发新的构建和部署")
    print("   3. 部署最新的内容")
    print("   4. 与GitHub Pages内容保持同步")
    
    print("\n⏰ 预期时间线:")
    print("   • 提交推送: 立即完成")
    print("   • Vercel检测: 1-2分钟")
    print("   • 构建部署: 2-3分钟")
    print("   • 内容同步: 3-5分钟")
    
    print("\n🔍 监控方法:")
    print("   1. 访问 https://vercel.com/dashboard")
    print("   2. 查看ai-news-pusher项目")
    print("   3. 检查最新部署状态")
    print("   4. 确认部署时间和内容")
    
    print("\n🌐 验证同步:")
    print("   • Vercel: https://ai-news-pusher.vercel.app")
    print("   • GitHub Pages: https://velist.github.io/ai-news-pusher/docs/")
    print("   • 对比两个网站的内容和更新时间")

def main():
    """主同步流程"""
    print("🚀 强制Vercel同步最新内容")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 创建同步触发器
    created_files = create_sync_trigger()
    
    # 2. 更新README信息
    readme_updated = update_readme_sync_info()
    
    # 3. 提交并推送
    git_success = commit_and_push_sync()
    
    # 4. 提供指导
    provide_sync_guidance()
    
    # 总结
    print("\n📊 同步操作总结:")
    print("=" * 60)
    print(f"✅ 触发文件: 已创建 {len(created_files)} 个")
    print(f"✅ README更新: {'成功' if readme_updated else '失败'}")
    print(f"✅ Git操作: {'成功' if git_success else '失败'}")
    
    if git_success:
        print("\n🎉 同步触发成功！")
        print("💡 新提交已推送，Vercel应该会自动检测并部署")
        print("🔄 这将解决GitHub Pages和Vercel内容不同步的问题")
        print("⏰ 请等待3-5分钟让Vercel完成部署")
        
        print("\n🌐 验证链接:")
        print("   📱 Vercel网站: https://ai-news-pusher.vercel.app")
        print("   📊 GitHub Pages: https://velist.github.io/ai-news-pusher/docs/")
        print("   🔧 Vercel控制台: https://vercel.com/dashboard")
        
        print("\n💡 如果5分钟后仍未同步:")
        print("   1. 检查Vercel控制台的部署日志")
        print("   2. 确认GitHub集成设置正确")
        print("   3. 手动触发Vercel重新部署")
    else:
        print("\n❌ 同步触发失败")
        print("💡 请检查Git配置和网络连接")
    
    print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()