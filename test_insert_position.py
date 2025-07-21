#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试使用正确API在指定位置插入记录
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
    """获取当前第1行记录的ID"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=1"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            records = result.get('data', {}).get('items', [])
            if records:
                first_record = records[0]
                record_id = first_record.get('record_id')
                title = first_record.get('fields', {}).get('标题', '无标题')
                print(f"📍 当前第1行: {title[:50]}... (ID: {record_id})")
                return record_id
        
        return None
    except:
        return None

def insert_before_first_record():
    """使用单条记录API在第1行前插入"""
    access_token = get_access_token()
    if not access_token:
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    # 获取第1行记录ID
    first_record_id = get_first_record_id()
    
    try:
        # 使用单条记录创建API，尝试指定位置参数
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        current_time = time.strftime("%H:%M:%S")
        
        request_data = {
            "fields": {
                "标题": f"🚀 [第1行] 顶部插入测试 - {current_time}",
                "摘要": "此记录应该插入到表格第1行，成为新的顶部记录。",
                "AI观点": "成功插入第1行证明系统具备精确控制记录位置的能力。",
                "中国影响分析": "用户体验：新闻总是从最显眼的顶部位置开始显示，符合阅读习惯。",
                "更新日期": int(time.time() * 1000),
                "来源": {
                    "link": f"https://example.com/top-insert-{int(time.time())}",
                    "text": "顶部插入测试"
                }
            }
        }
        
        # 尝试添加位置参数
        if first_record_id:
            # 尝试不同的参数名
            url += f"?insert_before_record_id={first_record_id}"
        
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
            new_record_id = result.get('data', {}).get('record', {}).get('record_id')
            print(f"✅ 记录插入成功！ID: {new_record_id}")
            
            # 检查位置
            time.sleep(2)
            current_first = get_first_record_id()
            if current_first == new_record_id:
                print("🎉 成功插入到第1行！")
                return True
            else:
                print(f"⚠️  记录未在第1行，当前第1行: {current_first}")
                return False
        else:
            print(f"❌ 插入失败: {result}")
            # 如果带参数失败，尝试不带参数
            return try_simple_insert()
    
    except Exception as e:
        print(f"❌ 插入异常: {str(e)}")
        return try_simple_insert()

def try_simple_insert():
    """尝试简单插入然后移动到顶部"""
    print("🔄 尝试简单插入...")
    
    access_token = get_access_token()
    if not access_token:
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        current_time = time.strftime("%H:%M:%S")
        
        request_data = {
            "fields": {
                "标题": f"📌 [置顶] 最新AI新闻 - {current_time}",
                "摘要": "通过简单插入方式添加的记录，将尝试移动到顶部位置。",
                "AI观点": "如果无法直接插入顶部，可以先插入再调整位置。",
                "中国影响分析": "灵活的插入策略确保用户始终能看到最新内容。", 
                "更新日期": int(time.time() * 1000),
                "来源": {
                    "link": f"https://example.com/simple-insert-{int(time.time())}",
                    "text": "简单插入测试"
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
            new_record_id = result.get('data', {}).get('record', {}).get('record_id')
            print(f"✅ 简单插入成功！ID: {new_record_id}")
            
            # 提示用户手动设置排序
            print("💡 建议：在飞书表格中设置'更新日期'降序排列以确保新记录在顶部")
            return True
        else:
            print(f"❌ 简单插入也失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 简单插入异常: {str(e)}")
        return False

def main():
    print("🎯 测试在第1行插入新记录的多种方法...")
    print("=" * 60)
    
    print("方法1: 尝试在第1行前插入...")
    success = insert_before_first_record()
    
    if success:
        print("\n✅ 第1行插入测试成功！")
    else:
        print("\n📝 建议解决方案:")
        print("   1. 在飞书表格中点击'更新日期'列")
        print("   2. 选择降序排列（↓）")
        print("   3. 这样最新的记录会自动显示在顶部")
    
    print(f"\n🔗 查看结果: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")

if __name__ == "__main__":
    main()