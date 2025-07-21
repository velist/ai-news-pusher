#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置飞书多维表格字段
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
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('code') == 0:
            return result.get('tenant_access_token')
        else:
            print(f"❌ 获取访问令牌失败: {result}")
            return None
            
    except Exception as e:
        print(f"❌ 获取访问令牌异常: {str(e)}")
        return None

def get_table_fields(access_token, app_token, table_id):
    """获取表格现有字段"""
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        
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
            fields = result.get('data', {}).get('items', [])
            print(f"📋 表格现有字段 ({len(fields)} 个):")
            for field in fields:
                field_name = field.get('field_name', '未知')
                field_type = field.get('type', 0)
                field_id = field.get('field_id', '')
                print(f"   - {field_name} (类型:{field_type}, ID:{field_id})")
            return fields
        else:
            print(f"❌ 获取字段失败: {result}")
            return []
            
    except Exception as e:
        print(f"❌ 获取字段异常: {str(e)}")
        return []

def create_field(access_token, app_token, table_id, field_name, field_type):
    """创建新字段"""
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        
        data = {
            "field_name": field_name,
            "type": field_type
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('code') == 0:
            print(f"✅ 成功创建字段: {field_name}")
            return True
        else:
            print(f"❌ 创建字段失败 {field_name}: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 创建字段异常 {field_name}: {str(e)}")
        return False

def setup_table_fields(access_token, app_token, table_id):
    """设置表格所需字段"""
    # 定义需要的字段
    required_fields = [
        ("标题", 1),          # 文本
        ("摘要", 1),          # 文本  
        ("图片", 17),         # URL
        ("点评", 1),          # 文本
        ("中国影响分析", 1),    # 文本
        ("来源链接", 17),      # URL
        ("发布时间", 5),       # 日期时间
        ("来源", 1)           # 文本
    ]
    
    # 获取现有字段
    existing_fields = get_table_fields(access_token, app_token, table_id)
    existing_field_names = [field.get('field_name', '') for field in existing_fields]
    
    print(f"\n🔧 开始设置所需字段...")
    
    # 创建缺失的字段
    for field_name, field_type in required_fields:
        if field_name not in existing_field_names:
            print(f"📝 创建字段: {field_name}")
            create_field(access_token, app_token, table_id, field_name, field_type)
            time.sleep(0.5)  # 避免频率限制
        else:
            print(f"✅ 字段已存在: {field_name}")
    
    print("\n🎉 字段设置完成！")

def add_test_record_with_existing_fields(access_token, app_token, table_id):
    """使用现有字段添加测试记录"""
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        # 获取现有字段
        fields = get_table_fields(access_token, app_token, table_id)
        field_names = [field.get('field_name', '') for field in fields]
        
        # 构建记录数据，只使用存在的字段
        record_fields = {}
        
        test_data = {
            "标题": "🚀 [测试] OpenAI发布GPT-4 Turbo最新版本",
            "摘要": "最新发布的GPT-4 Turbo版本在推理能力、多模态理解方面都有显著改进。",
            "图片": "https://cdn.openai.com/API/gpt4-turbo.png",
            "点评": "这次升级体现了OpenAI在大语言模型领域的持续创新能力。",
            "中国影响分析": "技术追赶：促进国内大模型技术发展，推动相关产品迭代升级。",
            "来源链接": "https://openai.com/blog/gpt-4-turbo",
            "发布时间": int(time.time() * 1000),
            "来源": "OpenAI官方博客"
        }
        
        # 只添加存在的字段
        for key, value in test_data.items():
            if key in field_names:
                record_fields[key] = value
        
        request_data = {"fields": record_fields}
        
        req = urllib.request.Request(
            url,
            data=json.dumps(request_data).encode('utf-8'),
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
    """主函数"""
    print("🔧 设置飞书多维表格字段...")
    print(f"🔗 目标表格: {FEISHU_TABLE_URL}")
    print("-" * 60)
    
    # 1. 获取访问令牌
    print("1️⃣ 获取飞书访问令牌...")
    access_token = get_access_token()
    if not access_token:
        return False
    print("✅ 访问令牌获取成功")
    
    # 2. 解析app_token
    app_token = get_app_token_from_url(FEISHU_TABLE_URL)
    if not app_token:
        print("❌ 无法从URL中解析app_token")
        return False
    
    # 3. 获取表格ID
    table_id = "tblyPOJ4k9DxJuKc"  # 从之前的测试中获得
    
    # 4. 设置字段
    print("2️⃣ 设置表格字段...")
    setup_table_fields(access_token, app_token, table_id)
    
    # 5. 添加测试记录
    print("3️⃣ 添加测试记录...")
    success = add_test_record_with_existing_fields(access_token, app_token, table_id)
    
    if success:
        print("\n🎉 设置和测试完成！")
        print("📋 请检查您的飞书多维表格，应该能看到:")
        print("   1. 新创建的字段")
        print("   2. 一条测试新闻记录")
        print(f"🔗 表格链接: {FEISHU_TABLE_URL}")
    else:
        print("\n❌ 设置失败")
    
    return success

if __name__ == "__main__":
    main()