#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的Vercel部署修复脚本
解决 "This deployment can not be redeployed" 错误
"""

import os
import json
import subprocess
from datetime import datetime

def create_deployment_trigger():
    """创建部署触发器"""
    print("🔧 创建Vercel部署触发器...")
    
    # 创建简单的触发文件
    trigger_file = "docs/.vercel-trigger"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    trigger_content = f"""# Vercel部署触发器

时间: {current_time}
目的: 解决Vercel重新部署错误
状态: 创建新提交触发自动部署

## 问题
Vercel显示: "This deployment can not be redeployed. Please try again from a fresh commit."

## 解决方案
创建新的提交内容，让Vercel检测到变化并重新部署。

## 系统特性
- AI新闻翻译系统
- 硅基流动API集成
- 响应式H5界面
- 自动更新机制
"""
    
    with open(trigger_file, 'w', encoding='utf-8') as f:
        f.write(trigger_content)
    
    print(f"✅ 创建触发文件: {trigger_file}")
    
    # 更新vercel.json时间戳
    if os.path.exists("vercel.json"):
        with open("vercel.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        config["_last_update"] = current_time
        config["_deployment_fix"] = "Fresh commit to resolve redeploy error"
        
        with open("vercel.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ 更新vercel.json配置")
    
    return True

def commit_and_push():
    """提交并推送更改"""
    print("\n📤 提交并推送更改...")
    
    try:
        # 添加文件
        subprocess.run(["git", "add", "."], check=True)
        print("✅ 文件已添加")
        
        # 创建提交
        commit_msg = f"🔧 修复Vercel部署 - 新提交触发 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = subprocess.run(["git", "commit", "-m", commit_msg], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 提交成功")
            
            # 推送
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

def main():
    """主函数"""
    print("🚀 简单Vercel部署修复")
    print("=" * 50)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建部署触发器
    create_deployment_trigger()
    
    # 提交推送
    success = commit_and_push()
    
    print("\n📊 操作结果:")
    print("=" * 50)
    
    if success:
        print("✅ 修复成功！")
        print("💡 新的提交已推送到GitHub")
        print("🔄 Vercel应该会自动检测并重新部署")
        print("⏰ 预计3-5分钟完成部署")
        
        print("\n🌐 验证链接:")
        print("   📱 Vercel网站: https://ai-news-pusher.vercel.app")
        print("   📊 GitHub Pages: https://velist.github.io/ai-news-pusher/docs/")
        print("   🔧 Vercel控制台: https://vercel.com/dashboard")
        
        print("\n🎯 如果仍有问题:")
        print("   1. 访问Vercel控制台")
        print("   2. 找到ai-news-pusher项目")
        print("   3. 检查最新部署状态")
        print("   4. 查看部署日志")
    else:
        print("❌ 修复失败")
        print("💡 请检查错误信息并重试")
    
    print(f"\n⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()