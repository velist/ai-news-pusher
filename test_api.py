#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的API连接测试
"""

import os
import json
import urllib.request

def load_env_file():
    """加载环境变量"""
    env_path = '.env'
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            return True
        except Exception as e:
            print(f"环境变量加载失败: {e}")
            return False
    return False

def test_siliconflow_api():
    """测试硅基流动API"""
    load_env_file()
    
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 缺少SILICONFLOW_API_KEY")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...")
    
    try:
        payload = {
            "model": "Qwen/Qwen2.5-7B-Instruct",
            "messages": [{"role": "user", "content": "请将'Hello World'翻译成中文"}],
            "temperature": 0.3,
            "max_tokens": 100
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = json.dumps(payload).encode('utf-8')
        request = urllib.request.Request(
            "https://api.siliconflow.cn/v1/chat/completions", 
            data=data, 
            headers=headers
        )
        
        print("📡 发送API请求...")
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        print("✅ API响应成功:")
        if 'choices' in result and result['choices']:
            content = result['choices'][0]['message']['content']
            print(f"🤖 回复: {content}")
            return True
        else:
            print(f"❌ 响应格式异常: {result}")
            return False
            
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        return False

if __name__ == "__main__":
    test_siliconflow_api()