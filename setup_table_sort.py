#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置表格默认排序，确保最新记录显示在顶部
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

def get_datetime_field_id():
    """获取更新日期字段的ID"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            fields = result.get('data', {}).get('items', [])
            for field in fields:
                if field.get('field_name') == '更新日期' and field.get('type') == 5:  # 日期时间类型
                    field_id = field.get('field_id')
                    print(f"📅 找到更新日期字段ID: {field_id}")
                    return field_id
        
        print("❌ 未找到更新日期字段")
        return None
    except Exception as e:
        print(f"❌ 获取字段失败: {str(e)}")
        return None

def set_table_sort():
    """尝试设置表格排序"""
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    # 获取日期字段ID
    date_field_id = get_datetime_field_id()
    if not date_field_id:
        return False
    
    try:
        # 尝试创建视图，设置默认排序
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/views"
        
        view_data = {
            "view_name": "最新优先视图",
            "view_type": "grid",  # 网格视图
            "property": {
                "sort_info": [{
                    "field_id": date_field_id,
                    "desc": True  # 降序排列
                }]
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(view_data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            view_id = result.get('data', {}).get('view', {}).get('view_id')
            print(f"✅ 创建排序视图成功！视图ID: {view_id}")
            return True
        else:
            print(f"❌ 创建视图失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 设置排序异常: {str(e)}")
        return False

def add_test_record_with_timestamp():
    """添加一条带时间戳的测试记录，验证排序效果"""
    access_token = get_access_token()
    if not access_token:
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        current_time = time.strftime("%H:%M:%S")
        # 使用未来时间戳确保是最新的
        future_timestamp = int(time.time() * 1000) + 60000  # 加1分钟
        
        request_data = {
            "fields": {
                "标题": f"⭐ [最新] 排序测试 - {current_time}",
                "摘要": "这条记录使用了最新的时间戳，应该出现在按时间排序的表格顶部。",
                "AI观点": "正确的时间戳排序确保用户总是先看到最新、最重要的新闻。",
                "中国影响分析": "优化用户体验：最新信息优先显示，提高阅读效率和信息获取价值。",
                "更新日期": future_timestamp,
                "来源": {
                    "link": f"https://example.com/sort-test-{int(time.time())}",
                    "text": "排序测试源"
                }
            }
        }
        
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
            print("✅ 最新时间戳记录添加成功！")
            return True
        else:
            print(f"❌ 添加记录失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 添加记录异常: {str(e)}")
        return False

def main():
    print("🔧 设置表格排序，确保最新记录显示在顶部")
    print("=" * 60)
    
    print("1️⃣ 尝试设置表格默认排序...")
    sort_success = set_table_sort()
    
    print("2️⃣ 添加最新时间戳测试记录...")
    record_success = add_test_record_with_timestamp()
    
    print("\n" + "=" * 60)
    
    if sort_success:
        print("✅ 排序视图创建成功！")
    else:
        print("⚠️  自动排序设置失败")
    
    if record_success:
        print("✅ 最新记录添加成功！")
    
    print("\n📋 重要提醒：请在飞书表格中手动设置排序")
    print("🔗 打开表格: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
    print("\n👇 手动设置步骤：")
    print("   1. 点击 '更新日期' 列标题")
    print("   2. 选择 '降序排列' (↓)")  
    print("   3. 最新记录将显示在第1行")
    print("   4. 可以设置为默认视图保存排序")
    
    print("\n💡 这样每天8点推送的新AI新闻都会自动出现在最上方！")

if __name__ == "__main__":
    main()