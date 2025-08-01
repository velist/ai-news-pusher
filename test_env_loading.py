#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def load_env_file():
    """手动加载.env文件中的环境变量"""
    env_path = '.env'
    print(f"正在查找.env文件: {os.path.abspath(env_path)}")
    
    if os.path.exists(env_path):
        print("✅ 找到.env文件")
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"文件共有 {len(lines)} 行")
            
            for i, line in enumerate(lines, 1):
                line = line.strip()
                print(f"第{i}行: '{line}'")
                
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
                    print(f"  设置环境变量: {key} = {value[:10]}...")
        
        print("✅ 已加载.env文件中的环境变量")
    else:
        print("⚠️ 未找到.env文件")

def main():
    print("🧪 测试环境变量加载...")
    
    # 加载环境变量
    load_env_file()
    
    # 检查API密钥
    api_key = os.getenv('GNEWS_API_KEY')
    print(f"\n检查GNEWS_API_KEY: {api_key}")
    
    if api_key:
        print("✅ 环境变量加载成功！")
    else:
        print("❌ 环境变量加载失败！")
        
    # 显示所有环境变量中包含API的
    print("\n所有包含'API'的环境变量:")
    for key, value in os.environ.items():
        if 'API' in key:
            print(f"  {key} = {value[:20]}...")

if __name__ == "__main__":
    main()