#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自动部署到GitHub并设置Secrets
"""

import os
import subprocess
import json
import urllib.request
import urllib.parse
import sys

class GitHubDeployer:
    def __init__(self):
        self.repo_name = "ai-news-pusher"
        self.repo_description = "AI新闻自动推送系统 - 每日8点自动推送AI科技新闻到飞书多维表格"
        
        # GitHub配置
        self.github_token = None
        self.username = None
        
        # Secrets配置
        self.secrets = {
            "GNEWS_API_KEY": "c3cb6fef0f86251ada2b515017b97143",
            "FEISHU_APP_ID": "cli_a8f4efb90f3a1013", 
            "FEISHU_APP_SECRET": "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8",
            "FEISHU_TABLE_URL": "https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b"
        }
    
    def check_git_installed(self):
        """检查Git是否安装"""
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Git已安装: {result.stdout.strip()}")
                return True
            else:
                print("❌ Git未安装")
                return False
        except FileNotFoundError:
            print("❌ Git未找到，请先安装Git")
            return False
    
    def check_gh_cli_installed(self):
        """检查GitHub CLI是否安装"""
        try:
            result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ GitHub CLI已安装: {result.stdout.strip()}")
                return True
            else:
                print("❌ GitHub CLI未安装")
                return False
        except FileNotFoundError:
            print("❌ GitHub CLI未找到")
            print("💡 请安装GitHub CLI: https://cli.github.com/")
            return False
    
    def get_github_credentials(self):
        """获取GitHub凭据"""
        try:
            # 尝试从gh CLI获取用户信息
            result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ GitHub CLI已认证")
                
                # 获取用户名
                user_result = subprocess.run(['gh', 'api', 'user'], capture_output=True, text=True)
                if user_result.returncode == 0:
                    user_data = json.loads(user_result.stdout)
                    self.username = user_data.get('login')
                    print(f"📱 GitHub用户: {self.username}")
                    return True
            else:
                print("❌ GitHub CLI未认证")
                print("💡 请运行: gh auth login")
                return False
        except Exception as e:
            print(f"❌ 获取GitHub凭据失败: {str(e)}")
            return False
    
    def create_git_repo(self):
        """创建本地Git仓库"""
        try:
            print("📁 初始化本地Git仓库...")
            
            # 检查是否已经是Git仓库
            if os.path.exists('.git'):
                print("✅ 已经是Git仓库")
            else:
                subprocess.run(['git', 'init'], check=True)
                print("✅ Git仓库初始化完成")
            
            # 添加所有文件
            subprocess.run(['git', 'add', '.'], check=True)
            
            # 检查是否有提交
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.stdout.strip():
                subprocess.run(['git', 'commit', '-m', '🚀 初始化AI新闻自动推送系统'], check=True)
                print("✅ 初始提交完成")
            else:
                print("ℹ️  没有需要提交的更改")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git操作失败: {str(e)}")
            return False
    
    def create_github_repo(self):
        """创建GitHub仓库"""
        try:
            print(f"🌐 创建GitHub仓库: {self.repo_name}")
            
            cmd = [
                'gh', 'repo', 'create', self.repo_name,
                '--description', self.repo_description,
                '--public',
                '--source=.',
                '--remote=origin',
                '--push'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ GitHub仓库创建并推送成功")
                repo_url = f"https://github.com/{self.username}/{self.repo_name}"
                print(f"🔗 仓库URL: {repo_url}")
                return repo_url
            else:
                if "already exists" in result.stderr.lower():
                    print("⚠️  仓库已存在，尝试推送到现有仓库...")
                    # 添加远程仓库并推送
                    try:
                        subprocess.run(['git', 'remote', 'add', 'origin', f'https://github.com/{self.username}/{self.repo_name}.git'], check=True)
                    except:
                        subprocess.run(['git', 'remote', 'set-url', 'origin', f'https://github.com/{self.username}/{self.repo_name}.git'], check=True)
                    
                    subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
                    print("✅ 推送到现有仓库成功")
                    return f"https://github.com/{self.username}/{self.repo_name}"
                else:
                    print(f"❌ 创建GitHub仓库失败: {result.stderr}")
                    return None
                    
        except Exception as e:
            print(f"❌ 创建GitHub仓库异常: {str(e)}")
            return None
    
    def set_github_secrets(self):
        """设置GitHub Secrets"""
        try:
            print("🔐 设置GitHub Secrets...")
            
            for secret_name, secret_value in self.secrets.items():
                print(f"   设置 {secret_name}...")
                
                cmd = [
                    'gh', 'secret', 'set', secret_name,
                    '--body', secret_value,
                    '--repo', f'{self.username}/{self.repo_name}'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"   ✅ {secret_name} 设置成功")
                else:
                    print(f"   ❌ {secret_name} 设置失败: {result.stderr}")
                    return False
            
            print("✅ 所有Secrets设置完成")
            return True
            
        except Exception as e:
            print(f"❌ 设置Secrets异常: {str(e)}")
            return False
    
    def enable_actions(self):
        """启用GitHub Actions"""
        try:
            print("⚙️  启用GitHub Actions...")
            
            # GitHub Actions默认启用，这里主要是确认
            result = subprocess.run([
                'gh', 'api', f'repos/{self.username}/{self.repo_name}/actions/permissions',
                '--method', 'PUT',
                '--field', 'enabled=true',
                '--field', 'allowed_actions=all'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ GitHub Actions已启用")
                return True
            else:
                print(f"⚠️  Actions启用可能失败: {result.stderr}")
                return True  # 不阻塞流程
                
        except Exception as e:
            print(f"⚠️  启用Actions异常: {str(e)}")
            return True  # 不阻塞流程
    
    def deploy(self):
        """执行完整部署流程"""
        print("🚀 开始自动部署到GitHub...")
        print("=" * 60)
        
        # 1. 检查工具
        if not self.check_git_installed():
            return False
        
        if not self.check_gh_cli_installed():
            return False
        
        # 2. 获取GitHub凭据
        if not self.get_github_credentials():
            return False
        
        # 3. 创建本地Git仓库
        if not self.create_git_repo():
            return False
        
        # 4. 创建GitHub仓库
        repo_url = self.create_github_repo()
        if not repo_url:
            return False
        
        # 5. 设置Secrets
        if not self.set_github_secrets():
            return False
        
        # 6. 启用Actions
        self.enable_actions()
        
        print("\n" + "=" * 60)
        print("🎉 部署完成！AI新闻推送系统已成功部署到GitHub")
        print(f"🔗 仓库地址: {repo_url}")
        print(f"⚙️  Actions地址: {repo_url}/actions")
        print("\n📋 接下来会发生什么:")
        print("   1. ✅ 每天北京时间8点自动运行")
        print("   2. ✅ 获取最新AI科技新闻") 
        print("   3. ✅ 生成AI分析和点评")
        print("   4. ✅ 推送到您的飞书多维表格")
        print(f"   5. 🔗 查看结果: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        print("\n🤖 您可以随时在Actions页面查看运行日志和状态！")
        
        return True

def main():
    deployer = GitHubDeployer()
    
    print("欢迎使用AI新闻推送系统GitHub部署工具！")
    print("这将会:")
    print("1. 📁 创建Git仓库")
    print("2. 🌐 推送代码到GitHub") 
    print("3. 🔐 设置API密钥")
    print("4. ⚙️  启用自动化工作流")
    print("\n是否继续？(y/n): ", end='')
    
    if input().lower() != 'y':
        print("操作已取消")
        return
    
    success = deployer.deploy()
    
    if success:
        print("\n✨ 恭喜！您的AI新闻推送系统已经完全部署完成！")
        sys.exit(0)
    else:
        print("\n❌ 部署失败，请检查错误信息")
        sys.exit(1)

if __name__ == "__main__":
    main()