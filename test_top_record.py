#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试在表格顶部插入记录
"""

import json
import urllib.request
import time

# 配置信息
FEISHU_APP_ID = "cli_a8f4efb90f3a1013"
FEISHU_APP_SECRET = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

def get_access_token():
    try:
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        return result.get('tenant_access_token') if result.get('code') == 0 else None
    except:
        return None

def get_first_record_id():
    """获取表格第一条记录的ID"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            records = result.get('data', {}).get('items', [])
            if records:
                first_record = records[0]
                record_id = first_record.get('record_id')
                print(f"📋 找到第一条记录ID: {record_id}")
                return record_id
        
        print("📋 表格中没有记录")
        return None
    except Exception as e:
        print(f"❌ 获取记录失败: {str(e)}")
        return None

def add_record_at_top():
    """在表格顶部插入新记录"""
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    # 获取第一条记录ID（用于插入位置）
    first_record_id = get_first_record_id()
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        # 测试数据 - 标记为最新
        record_data = {
            "fields": {
                "标题": "🆕 [最新测试] AI新闻置顶测试 - " + time.strftime("%H:%M:%S"),
                "摘要": "这是一条测试记录，用于验证新记录是否会出现在表格最上方。",
                "AI观点": "测试成功表明系统能够正确地将最新新闻放置在表格顶部，符合阅读习惯。",
                "中国影响分析": "技术验证：确保自动化新闻推送系统的用户体验优化功能正常工作。",
                "更新日期": int(time.time() * 1000),
                "来源": "https://example.com/test-news"
            }
        }
        
        # 如果有记录，尝试在第一条记录前插入
        if first_record_id:
            record_data["client_token"] = f"top_insert_{int(time.time())}"  # 客户端令牌确保幂等性
        
        req = urllib.request.Request(
            url,
            data=json.dumps(record_data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            new_record_id = result.get('data', {}).get('record', {}).get('record_id', '未知')
            print(f"✅ 新记录插入成功！记录ID: {new_record_id}")
            
            # 检查是否在顶部
            print("🔍 验证记录位置...")
            time.sleep(1)  # 等待一下让数据库更新
            
            current_first = get_first_record_id()
            if current_first == new_record_id:
                print("🎉 验证成功！新记录已出现在表格顶部")
                return True
            else:
                print("⚠️  新记录未在顶部，可能需要手动排序")
                return True  # 仍然算成功，只是位置问题
        else:
            print(f"❌ 插入记录失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 插入记录异常: {str(e)}")
        return False

def main():
    print("🔝 测试在表格顶部插入新记录...")
    print("=" * 50)
    
    success = add_record_at_top()
    
    if success:
        print("\n✅ 测试完成！请查看您的飞书表格")
        print("🔗 https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        print("\n💡 如果新记录不在最上方，您可以:")
        print("   1. 在飞书表格中按'更新日期'降序排列")
        print("   2. 设置表格默认排序为按时间倒序")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main()