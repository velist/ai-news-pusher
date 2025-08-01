#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署监控脚本 - 实时跟踪Vercel部署状态和日志
"""

import subprocess
import time
import json
import requests
from datetime import datetime

def run_command(cmd):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def get_deployment_status():
    """获取部署状态"""
    print(f"\n{'='*60}")
    print(f"部署状态检查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 获取部署列表
    stdout, stderr, code = run_command("vercel ls")
    if code == 0:
        print("\n📋 部署列表:")
        print(stdout)
    else:
        print(f"❌ 获取部署列表失败: {stderr}")
    
    return stdout

def check_url_accessibility(url):
    """检查URL可访问性"""
    print(f"\n🌐 检查URL可访问性: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ HTTP状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ 网站可正常访问")
            print(f"📄 页面大小: {len(response.content)} bytes")
            return True
        else:
            print(f"⚠️ 网站返回状态码: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误")
        return False
    except Exception as e:
        print(f"❌ 访问失败: {str(e)}")
        return False

def get_deployment_logs(deployment_url):
    """获取部署日志"""
    print(f"\n📋 获取部署日志...")
    
    # 提取部署ID
    if 'vercel.app' in deployment_url:
        deployment_id = deployment_url.split('//')[1].split('-')[0]
        log_cmd = f"vercel inspect {deployment_url} --logs"
        
        stdout, stderr, code = run_command(log_cmd)
        if code == 0:
            print("\n📝 部署日志:")
            print(stdout)
        else:
            print(f"❌ 获取日志失败: {stderr}")

def monitor_deployment():
    """监控部署状态"""
    print("🚀 开始监控Vercel部署状态...")
    print("按 Ctrl+C 停止监控")
    
    # 目标URL
    target_url = "https://docs-3fdkydhgu-velists-projects.vercel.app"
    
    try:
        while True:
            # 获取部署状态
            deployment_info = get_deployment_status()
            
            # 检查URL可访问性
            is_accessible = check_url_accessibility(target_url)
            
            if is_accessible:
                print("\n🎉 部署成功！网站可正常访问")
                print(f"🔗 访问地址: {target_url}")
                break
            else:
                print("\n⏳ 网站暂时无法访问，继续监控...")
                
                # 获取部署日志
                get_deployment_logs(target_url)
            
            print(f"\n⏰ 等待30秒后重新检查...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
    except Exception as e:
        print(f"\n❌ 监控过程中出现错误: {str(e)}")

def main():
    """主函数"""
    print("\n" + "="*80)
    print("🔍 Vercel部署监控工具")
    print("="*80)
    
    # 首先检查当前部署状态
    monitor_deployment()
    
    print("\n" + "="*80)
    print("📊 部署监控完成")
    print("="*80)

if __name__ == "__main__":
    main()