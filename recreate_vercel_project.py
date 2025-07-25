#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel项目重建指南
解决持续的部署同步问题
"""

import json
import subprocess
from datetime import datetime

def analyze_current_issue():
    """分析当前问题"""
    print("🔍 分析当前Vercel部署问题")
    print("=" * 60)
    
    print("📋 问题症状:")
    print("   ❌ 手动重新部署失败")
    print("   ❌ 错误: 'This deployment can not be redeployed'")
    print("   ❌ 自动同步失败")
    print("   ❌ 多次新提交无效")
    
    print("\n🔍 可能原因:")
    print("   1. GitHub-Vercel集成损坏")
    print("   2. Webhook配置问题")
    print("   3. 项目配置缓存问题")
    print("   4. 权限或认证问题")
    print("   5. Vercel内部状态异常")
    
    print("\n💡 推荐解决方案:")
    print("   🗑️ 删除现有Vercel项目")
    print("   🆕 重新创建项目连接")
    print("   ⚙️ 重新配置所有设置")
    
    return True

def prepare_for_recreation():
    """为重建做准备"""
    print("\n📋 重建前准备工作")
    print("=" * 60)
    
    # 1. 记录当前配置
    print("📝 记录当前配置...")
    
    config_backup = {
        "project_name": "ai-news-pusher",
        "github_repo": "https://github.com/velist/ai-news-pusher",
        "domain": "ai-news-pusher.vercel.app",
        "framework": "Other",
        "build_command": "",
        "output_directory": "docs",
        "install_command": "",
        "environment_variables": {
            "GNEWS_API_KEY": "c3cb6fef0f86251ada2b515017b97143",
            "SILICONFLOW_API_KEY": "sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa"
        },
        "backup_time": datetime.now().isoformat()
    }
    
    # 保存配置备份
    with open("vercel-config-backup.json", 'w', encoding='utf-8') as f:
        json.dump(config_backup, f, indent=2, ensure_ascii=False)
    
    print("✅ 配置已备份到: vercel-config-backup.json")
    
    # 2. 确保vercel.json正确
    print("\n🔧 检查vercel.json配置...")
    
    if os.path.exists("vercel.json"):
        with open("vercel.json", 'r', encoding='utf-8') as f:
            vercel_config = json.load(f)
        print("✅ vercel.json存在且格式正确")
    else:
        print("❌ vercel.json不存在，需要创建")
    
    # 3. 检查关键文件
    print("\n📁 检查关键文件...")
    
    key_files = [
        "docs/index.html",
        "docs/enhanced_news_data.json",
        "vercel.json"
    ]
    
    for file in key_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file}: {size:,} 字节")
        else:
            print(f"❌ {file}: 不存在")
    
    return config_backup

def create_recreation_guide():
    """创建重建指南"""
    print("\n📖 创建详细重建指南...")
    
    guide_content = f"""# Vercel项目重建指南

## 重建时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 问题背景
- 现有Vercel项目出现持续的部署同步问题
- 手动重新部署失败，提示"This deployment can not be redeployed"
- 自动同步机制完全失效
- 多次新提交无法触发部署

## 重建步骤

### 第一步：删除现有项目
1. 访问 https://vercel.com/dashboard
2. 找到 `ai-news-pusher` 项目
3. 点击项目名称进入项目详情
4. 点击 `Settings` 标签
5. 滚动到页面底部找到 `Delete Project`
6. 输入项目名称确认删除
7. 点击 `Delete` 按钮

### 第二步：重新创建项目
1. 在Vercel控制台点击 `New Project`
2. 选择 `Import Git Repository`
3. 找到并选择 `velist/ai-news-pusher` 仓库
4. 点击 `Import`

### 第三步：配置项目设置
**基本设置:**
- Project Name: `ai-news-pusher`
- Framework Preset: `Other`
- Root Directory: `./` (默认)
- Build Command: 留空
- Output Directory: `docs`
- Install Command: 留空

**环境变量:**
添加以下环境变量:
- `GNEWS_API_KEY`: `c3cb6fef0f86251ada2b515017b97143`
- `SILICONFLOW_API_KEY`: `sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa`

### 第四步：部署设置
1. 确认 Production Branch 设置为 `main`
2. 启用 Auto-deploy from Git
3. 点击 `Deploy` 开始首次部署

### 第五步：验证部署
1. 等待部署完成（通常2-5分钟）
2. 访问生成的URL验证内容
3. 确认与GitHub Pages内容一致
4. 测试自动同步功能

## 预期结果
- ✅ 全新的GitHub-Vercel集成
- ✅ 正常的自动部署功能
- ✅ 内容与GitHub Pages同步
- ✅ 未来提交自动触发部署

## 备用方案
如果重建后仍有问题:
1. 检查GitHub仓库的Webhook设置
2. 确认Vercel的GitHub App权限
3. 尝试使用不同的Vercel账号
4. 联系Vercel技术支持

## 重要提醒
- 删除项目前确保已备份所有配置
- 重建后域名可能会改变
- 需要重新配置所有环境变量
- 首次部署可能需要更长时间

## 系统特性确认
重建完成后确认以下功能正常:
- 🤖 AI新闻翻译系统
- ✅ 硅基流动API集成
- 🎯 智能质量评估
- 📱 响应式H5界面
- ⏰ 自动更新机制
"""
    
    with open("VERCEL_RECREATION_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ 重建指南已创建: VERCEL_RECREATION_GUIDE.md")
    return True

def commit_preparation_files():
    """提交准备文件"""
    print("\n📤 提交准备文件...")
    
    try:
        subprocess.run(["git", "add", "."], check=True)
        
        commit_msg = f"📋 准备Vercel项目重建 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(["git", "commit", "-m", commit_msg], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 提交成功")
            
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
                print("ℹ️ 没有新的更改")
                return True
            else:
                print(f"❌ 提交失败: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Git操作失败: {str(e)}")
        return False

def provide_next_steps():
    """提供后续步骤"""
    print("\n🎯 立即行动计划:")
    print("=" * 60)
    
    print("📋 推荐操作顺序:")
    print("   1. ✅ 阅读重建指南 (VERCEL_RECREATION_GUIDE.md)")
    print("   2. 🗑️ 删除现有Vercel项目")
    print("   3. 🆕 重新创建项目连接")
    print("   4. ⚙️ 配置项目设置")
    print("   5. 🚀 执行首次部署")
    print("   6. ✅ 验证同步功能")
    
    print("\n⏰ 预计时间:")
    print("   • 删除项目: 2分钟")
    print("   • 重新创建: 5分钟")
    print("   • 配置设置: 3分钟")
    print("   • 首次部署: 5分钟")
    print("   • 总计时间: 15分钟")
    
    print("\n💡 重建优势:")
    print("   ✅ 全新的集成连接")
    print("   ✅ 清除所有缓存问题")
    print("   ✅ 重置所有配置状态")
    print("   ✅ 建立正常的同步机制")
    
    print("\n🔗 重要链接:")
    print("   📱 Vercel控制台: https://vercel.com/dashboard")
    print("   📊 GitHub仓库: https://github.com/velist/ai-news-pusher")
    print("   📋 重建指南: ./VERCEL_RECREATION_GUIDE.md")

def main():
    """主重建准备流程"""
    print("🚀 Vercel项目重建准备")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 分析问题
    analyze_current_issue()
    
    # 2. 准备重建
    config_backup = prepare_for_recreation()
    
    # 3. 创建指南
    guide_created = create_recreation_guide()
    
    # 4. 提交文件
    git_success = commit_preparation_files()
    
    # 5. 提供后续步骤
    provide_next_steps()
    
    # 总结
    print("\n📊 准备工作总结:")
    print("=" * 60)
    print("✅ 问题分析: 完成")
    print("✅ 配置备份: 完成")
    print("✅ 重建指南: 完成")
    print(f"✅ Git操作: {'成功' if git_success else '失败'}")
    
    print("\n🎯 结论:")
    print("   基于当前症状，重建Vercel项目是最佳解决方案")
    print("   这将彻底解决GitHub-Vercel集成问题")
    print("   重建后应该能恢复正常的自动同步功能")
    
    print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🚀 请按照 VERCEL_RECREATION_GUIDE.md 指南进行重建！")

if __name__ == "__main__":
    import os
    main()