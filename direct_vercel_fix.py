#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接修复Vercel同步问题
强制触发新的部署
"""

import subprocess
import os
from datetime import datetime

def create_unique_trigger():
    """创建唯一的触发文件"""
    print("🔧 创建唯一的Vercel部署触发器...")
    
    current_time = datetime.now()
    timestamp = current_time.strftime('%Y%m%d_%H%M%S')
    
    # 创建多个触发文件确保有变化
    trigger_files = []
    
    # 1. 主触发文件
    main_trigger = f"docs/.vercel-deploy-{timestamp}"
    with open(main_trigger, 'w', encoding='utf-8') as f:
        f.write(f"""# Vercel部署强制触发器

时间戳: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
唯一ID: {timestamp}
目的: 强制Vercel检测变化并重新部署

## 问题分析
- GitHub Pages内容: 134,596 字符 (最新)
- Vercel内容: 49,757 字符 (旧版本)
- 内容差异: 84,839 字符
- 同步状态: 严重不同步

## 解决方案
创建新的唯一内容触发Vercel重新部署，
确保Vercel获取并部署最新的GitHub内容。

## 系统特性
- AI新闻翻译系统
- 硅基流动API集成
- 真实新闻中文翻译
- 响应式H5界面
- 自动更新机制
""")
    trigger_files.append(main_trigger)
    
    # 2. 时间戳文件
    timestamp_file = "docs/.last-deploy-attempt"
    with open(timestamp_file, 'w', encoding='utf-8') as f:
        f.write(f"{current_time.isoformat()}\n")
        f.write(f"Attempt: Force Vercel sync\n")
        f.write(f"Unique: {timestamp}\n")
    trigger_files.append(timestamp_file)
    
    # 3. 版本文件
    version_file = "docs/.deploy-version"
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(f"version: {timestamp}\n")
        f.write(f"type: force-sync\n")
        f.write(f"target: vercel\n")
        f.write(f"source: github-pages\n")
    trigger_files.append(version_file)
    
    print(f"✅ 创建了 {len(trigger_files)} 个触发文件:")
    for file in trigger_files:
        print(f"   📄 {file}")
    
    return trigger_files

def update_vercel_config_comment():
    """在vercel.json中添加注释（通过临时文件）"""
    print("\n📝 更新vercel.json相关文件...")
    
    # 创建vercel配置说明文件
    config_note = "vercel-config-note.md"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(config_note, 'w', encoding='utf-8') as f:
        f.write(f"""# Vercel配置说明

## 更新时间
{current_time}

## 配置状态
- vercel.json: 符合schema规范
- 路由配置: 正常
- GitHub集成: 已启用
- 自动部署: 应该触发

## 部署目标
确保Vercel部署与GitHub Pages内容一致：
- GitHub Pages: 134,596 字符 (最新内容)
- Vercel目标: 同步到最新内容

## 触发原因
手动创建新提交强制Vercel检测变化并重新部署。
""")
    
    print(f"✅ 创建配置说明: {config_note}")
    return config_note

def force_commit_and_push():
    """强制提交并推送"""
    print("\n📤 强制提交并推送所有更改...")
    
    try:
        # 显示当前状态
        status_result = subprocess.run(["git", "status", "--porcelain"], 
                                     capture_output=True, text=True)
        if status_result.stdout.strip():
            print("📋 检测到以下更改:")
            for line in status_result.stdout.strip().split('\n'):
                print(f"   {line}")
        
        # 添加所有文件
        subprocess.run(["git", "add", "."], check=True)
        print("✅ 所有文件已添加")
        
        # 创建强制提交
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_msg = f"🚀 强制Vercel同步 - 解决内容差异 {timestamp}"
        
        result = subprocess.run(["git", "commit", "-m", commit_msg], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 提交成功")
            print(f"   📝 提交信息: {commit_msg}")
            
            # 强制推送
            push_result = subprocess.run(["git", "push"], 
                                       capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("✅ 推送成功")
                print("🔄 GitHub已接收新提交，Vercel应该会检测到")
                return True
            else:
                print(f"❌ 推送失败: {push_result.stderr}")
                return False
        else:
            if "nothing to commit" in result.stdout:
                print("ℹ️ 没有新的更改需要提交")
                # 即使没有更改，也尝试创建一个空提交
                empty_commit = subprocess.run([
                    "git", "commit", "--allow-empty", "-m", 
                    f"🔄 空提交触发Vercel部署 - {timestamp}"
                ], capture_output=True, text=True)
                
                if empty_commit.returncode == 0:
                    print("✅ 创建空提交成功")
                    push_result = subprocess.run(["git", "push"], 
                                               capture_output=True, text=True)
                    if push_result.returncode == 0:
                        print("✅ 空提交推送成功")
                        return True
                    else:
                        print(f"❌ 空提交推送失败: {push_result.stderr}")
                        return False
                else:
                    print(f"❌ 创建空提交失败: {empty_commit.stderr}")
                    return False
            else:
                print(f"❌ 提交失败: {result.stderr}")
                return False
                
    except Exception as e:
        print(f"❌ Git操作异常: {str(e)}")
        return False

def provide_immediate_actions():
    """提供立即行动指南"""
    print("\n🎯 立即行动指南:")
    print("=" * 60)
    
    print("📋 新提交已创建，现在需要:")
    print("   1. 等待1-2分钟让GitHub处理提交")
    print("   2. Vercel应该自动检测到新提交")
    print("   3. 如果5分钟内仍未自动部署，执行手动操作")
    
    print("\n🔧 手动操作步骤:")
    print("   1. 访问: https://vercel.com/dashboard")
    print("   2. 找到: ai-news-pusher 项目")
    print("   3. 点击: 项目名称进入详情页")
    print("   4. 查看: Deployments 标签")
    print("   5. 确认: 是否有新的部署正在进行")
    print("   6. 如果没有: 点击右上角 'Redeploy' 按钮")
    print("   7. 选择: 最新的commit (刚才推送的)")
    print("   8. 点击: 'Redeploy' 确认")
    
    print("\n⏰ 时间预期:")
    print("   • 自动检测: 1-3分钟")
    print("   • 构建时间: 2-4分钟")
    print("   • 总计时间: 3-7分钟")
    
    print("\n🔍 验证方法:")
    print("   • 等待部署完成后访问两个网站")
    print("   • 对比内容长度和更新时间")
    print("   • 确认内容一致性")

def main():
    """主修复流程"""
    print("🚀 直接修复Vercel同步问题")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📊 问题分析:")
    print("   • GitHub Pages: 134,596 字符 (最新)")
    print("   • Vercel: 49,757 字符 (旧版本)")
    print("   • 差异: 84,839 字符 (63%内容缺失)")
    print("   • 状态: 严重不同步")
    
    # 1. 创建唯一触发器
    trigger_files = create_unique_trigger()
    
    # 2. 更新配置说明
    config_file = update_vercel_config_comment()
    
    # 3. 强制提交推送
    git_success = force_commit_and_push()
    
    # 4. 提供行动指南
    provide_immediate_actions()
    
    # 总结
    print("\n📊 操作结果总结:")
    print("=" * 60)
    print(f"✅ 触发文件: 创建了 {len(trigger_files)} 个")
    print(f"✅ 配置说明: 已创建")
    print(f"✅ Git操作: {'成功' if git_success else '失败'}")
    
    if git_success:
        print("\n🎉 强制触发成功！")
        print("💡 新的唯一提交已推送到GitHub")
        print("🔄 Vercel现在应该能检测到变化")
        print("⏰ 请等待3-7分钟观察结果")
        
        print("\n🌐 监控链接:")
        print("   📱 Vercel网站: https://ai-news-pusher.vercel.app")
        print("   📊 GitHub Pages: https://velist.github.io/ai-news-pusher/docs/")
        print("   🔧 Vercel控制台: https://vercel.com/dashboard")
        
        print("\n💡 如果仍然不同步:")
        print("   这可能是Vercel的GitHub集成问题")
        print("   需要在Vercel控制台手动触发部署")
    else:
        print("\n❌ 强制触发失败")
        print("💡 请检查Git配置和权限")
    
    print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()