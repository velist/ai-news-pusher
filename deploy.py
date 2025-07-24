#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI新闻翻译系统部署脚本
"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description}成功")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {description}失败")
            if result.stderr.strip():
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description}异常: {str(e)}")
        return False

def main():
    """主部署流程"""
    print("🚀 开始AI新闻翻译系统部署")
    print("=" * 60)
    
    # 1. 生成最新新闻内容
    print("📰 步骤1: 生成最新新闻内容")
    if not run_command("python enhanced_news_accumulator.py", "运行增强版新闻系统"):
        print("⚠️ 新闻生成失败，但继续部署现有内容")
    
    # 2. 检查关键文件
    print("\n📋 步骤2: 检查关键文件")
    required_files = [
        "docs/index.html",
        "docs/enhanced_news_data.json",
        "enhanced_news_accumulator.py",
        "translation/services/siliconflow_translator.py"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 缺失")
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️ 缺失关键文件: {missing_files}")
        print("请确保所有文件都已正确生成")
    
    # 3. Git提交
    print("\n📤 步骤3: 提交到GitHub")
    
    # 添加所有文件
    run_command("git add .", "添加所有文件")
    
    # 提交更改
    commit_message = f"🚀 部署增强版AI新闻翻译系统 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    commit_command = f'git commit -m "{commit_message}"'
    
    if run_command(commit_command, "提交更改"):
        # 推送到GitHub
        if run_command("git push", "推送到GitHub"):
            print("✅ 代码已成功推送到GitHub")
        else:
            print("❌ 推送失败，请检查网络连接和权限")
    else:
        print("ℹ️ 没有新的更改需要提交")
    
    # 4. 部署说明
    print("\n🌐 步骤4: Vercel部署说明")
    print("请按以下步骤完成Vercel部署:")
    print("1. 访问 https://vercel.com")
    print("2. 使用GitHub账号登录")
    print("3. 点击 'New Project'")
    print("4. 选择您的GitHub仓库")
    print("5. 配置环境变量:")
    print("   - GNEWS_API_KEY: c3cb6fef0f86251ada2b515017b97143")
    print("   - SILICONFLOW_API_KEY: sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa")
    print("6. 点击 'Deploy'")
    
    print("\n🎉 部署准备完成!")
    print("📊 系统特性:")
    print("   🤖 硅基流动AI翻译 - 成本降低80-95%")
    print("   ✅ 真实新闻中文翻译 - 告别模板内容")
    print("   🎯 智能质量评估 - 置信度评分")
    print("   📱 响应式H5界面 - 完美移动体验")
    print("   ⏰ 自动更新机制 - 每小时获取最新资讯")

if __name__ == "__main__":
    main()