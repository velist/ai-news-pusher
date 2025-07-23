#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试在第1行（顶部）插入新记录
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
                print(f"📍 当前第1行记录: {title[:30]}... (ID: {record_id})")
                return record_id
        
        print("📋 表格中没有记录")
        return None
    except Exception as e:
        print(f"❌ 获取第1行记录失败: {str(e)}")
        return None

def insert_at_first_row():
    """在第1行位置插入新记录"""
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    # 获取当前第1行记录ID作为插入位置参考
    first_record_id = get_first_record_id()
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create"
        
        current_time = time.strftime("%H:%M:%S")
        
        # 构建批量创建请求，指定插入位置
        request_data = {
            "records": [{
                "fields": {
                    "标题": f"🥇 [第1行测试] 置顶新闻测试 - {current_time}",
                    "摘要": "这条新闻应该出现在表格的第1行（最顶部位置），用于验证插入位置功能。",
                    "AI观点": "成功插入第1行说明系统能够正确控制新闻在表格中的显示位置。",
                    "中国影响分析": "用户体验优化：确保最新新闻总是显示在最显眼的顶部位置。",
                    "更新日期": int(time.time() * 1000),
                    "来源": {
                        "link": f"https://example.com/first-row-test-{int(time.time())}",
                        "text": "第1行测试源"
                    }
                }
            }]
        }
        
        # 如果存在第1行记录，指定在其前面插入
        if first_record_id:
            request_data["insert_mode"] = "insert_before"
            request_data["insert_record_id"] = first_record_id
        
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
            records = result.get('data', {}).get('records', [])
            if records:
                new_record_id = records[0].get('record_id', '未知')
                print(f"✅ 新记录插入成功！记录ID: {new_record_id}")
                
                # 验证是否在第1行
                print("🔍 验证新记录是否在第1行...")
                time.sleep(2)  # 等待数据更新
                
                current_first = get_first_record_id()
                if current_first == new_record_id:
                    print("🎉 验证成功！新记录已出现在第1行！")
                    return True
                else:
                    print("⚠️  新记录未在第1行")
                    return False
        else:
            print(f"❌ 批量插入失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 插入异常: {str(e)}")
        return False

def main():
    print("🥇 测试在第1行（最顶部）插入新记录...")
    print("=" * 60)
    
    success = insert_at_first_row()
    
    if success:
        print("\n✅ 测试完成！新记录已插入到第1行")
        print("🔗 请查看您的飞书表格验证效果")
        print("📊 https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
    else:
        print("\n❌ 第1行插入测试失败，尝试其他方法")

if __name__ == "__main__":
    main()