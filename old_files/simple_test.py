#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版测试推送 - 不依赖外部包
"""

import json
import urllib.request
import urllib.parse
import time
from datetime import datetime

# 配置信息
FEISHU_APP_ID = "cli_a8f4efb90f3a1013"
FEISHU_APP_SECRET = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
FEISHU_TABLE_URL = "https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

def get_app_token_from_url(url):
    """从URL中提取app_token"""
    if '/base/' in url:
        return url.split('/base/')[1].split('/')[0]
    return None

def get_access_token():
    """获取飞书访问令牌"""
    try:
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        data = {
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET
        }
        
        # 创建请求
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        # 发送请求
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('code') == 0:
            print("✅ 成功获取飞书访问令牌")
            return result.get('tenant_access_token')
        else:
            print(f"❌ 获取访问令牌失败: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 获取访问令牌异常: {str(e)}")
        return None

def get_table_info(access_token, app_token):
    """获取表格信息"""
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables"
        
        req = urllib.request.Request(
            url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('code') == 0:
            tables = result.get('data', {}).get('items', [])
            if tables:
                print(f"✅ 成功获取表格信息，找到 {len(tables)} 个表格")
                return tables[0]  # 返回第一个表格
        
        print(f"❌ 获取表格信息失败: {result}")
        return {}
        
    except Exception as e:
        print(f"❌ 获取表格信息异常: {str(e)}")
        return {}

def add_test_record(access_token, app_token, table_id):
    """添加测试记录"""
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        # 测试数据
        test_data = {
            "fields": {
                "标题": "🚀 [测试] OpenAI发布GPT-4 Turbo最新版本",
                "摘要": "最新发布的GPT-4 Turbo版本在推理能力、多模态理解方面都有显著改进。",
                "图片": "https://cdn.openai.com/API/gpt4-turbo.png",
                "点评": "这次升级体现了OpenAI在大语言模型领域的持续创新能力。",
                "中国影响分析": "技术追赶：促进国内大模型技术发展，推动相关产品迭代升级。",
                "来源链接": "https://openai.com/blog/gpt-4-turbo",
                "发布时间": int(time.time() * 1000),  # 当前时间戳（毫秒）
                "来源": "OpenAI官方博客"
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(test_data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('code') == 0:
            print("✅ 测试记录添加成功！")
            return True
        else:
            print(f"❌ 添加记录失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 添加记录异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试推送到飞书多维表格...")
    print(f"🔗 目标表格: {FEISHU_TABLE_URL}")
    print("-" * 60)
    
    # 1. 获取访问令牌
    print("1️⃣ 获取飞书访问令牌...")
    access_token = get_access_token()
    if not access_token:
        return False
    
    # 2. 解析app_token
    app_token = get_app_token_from_url(FEISHU_TABLE_URL)
    if not app_token:
        print("❌ 无法从URL中解析app_token")
        return False
    print(f"📋 App Token: {app_token}")
    
    # 3. 获取表格信息
    print("2️⃣ 获取表格信息...")
    table_info = get_table_info(access_token, app_token)
    if not table_info:
        return False
    
    table_id = table_info.get('table_id')
    table_name = table_info.get('name', '未知')
    print(f"📊 表格名称: {table_name}")
    print(f"🆔 Table ID: {table_id}")
    
    # 4. 添加测试记录
    print("3️⃣ 添加测试记录...")
    success = add_test_record(access_token, app_token, table_id)
    
    if success:
        print("\n🎉 测试推送完成！")
        print("📋 请检查您的飞书多维表格，应该能看到测试新闻记录")
        print(f"🔗 表格链接: {FEISHU_TABLE_URL}")
    else:
        print("\n❌ 测试推送失败")
        print("💡 可能的原因:")
        print("   1. 飞书应用权限配置不正确")
        print("   2. 表格字段名称不匹配")
        print("   3. 网络连接问题")
    
    return success

if __name__ == "__main__":
    main()