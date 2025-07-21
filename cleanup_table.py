#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
清理飞书表格 - 删除不需要的字段
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

def get_table_fields(access_token):
    """获取表格字段"""
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            return result.get('data', {}).get('items', [])
        return []
    except:
        return []

def delete_field(access_token, field_id, field_name):
    """删除字段"""
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        req.get_method = lambda: 'DELETE'
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            print(f"✅ 成功删除字段: {field_name}")
            return True
        else:
            print(f"❌ 删除字段失败 {field_name}: {result}")
            return False
    except Exception as e:
        print(f"❌ 删除字段异常 {field_name}: {str(e)}")
        return False

def cleanup_table():
    """清理表格字段"""
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return False
    
    # 获取所有字段
    fields = get_table_fields(access_token)
    if not fields:
        print("❌ 无法获取字段信息")
        return False
    
    print(f"📋 当前表格字段 ({len(fields)} 个):")
    for field in fields:
        name = field.get('field_name', '')
        field_type = field.get('type', 0)
        field_id = field.get('field_id', '')
        print(f"   - {name} (类型:{field_type}, ID:{field_id})")
    
    # 定义需要保留的字段
    keep_fields = {
        "标题": "新闻标题",
        "摘要": "新闻摘要", 
        "AI观点": "AI生成的点评",
        "中国影响分析": "对中国行业影响分析",
        "来源": "新闻来源URL",
        "更新日期": "发布时间"
    }
    
    # 定义需要删除的字段（重复或不需要的）
    fields_to_delete = [
        "新闻图片",    # 重复，我们有"图片"
        "图片",       # 附件类型，用不上
        "点评",       # 重复，我们有"AI观点"
        "来源链接",    # 重复，我们有"来源"
        "发布时间",    # 重复，我们有"更新日期"
        "板块"        # 单选字段，用不上
    ]
    
    print(f"\n🧹 开始清理不需要的字段...")
    print(f"📝 保留字段: {list(keep_fields.keys())}")
    print(f"🗑️  删除字段: {fields_to_delete}")
    
    deleted_count = 0
    for field in fields:
        field_name = field.get('field_name', '')
        field_id = field.get('field_id', '')
        
        if field_name in fields_to_delete:
            print(f"\n🗑️  删除字段: {field_name}")
            if delete_field(access_token, field_id, field_name):
                deleted_count += 1
            time.sleep(0.5)  # 避免频率限制
    
    print(f"\n✅ 清理完成！删除了 {deleted_count} 个不需要的字段")
    
    # 再次获取字段确认
    final_fields = get_table_fields(access_token)
    print(f"\n📋 清理后的字段 ({len(final_fields)} 个):")
    for field in final_fields:
        name = field.get('field_name', '')
        field_type = field.get('type', 0)
        print(f"   ✅ {name} (类型:{field_type})")
    
    return True

if __name__ == "__main__":
    print("🧹 开始清理飞书表格字段...")
    print("=" * 60)
    
    success = cleanup_table()
    
    if success:
        print("\n🎉 表格字段清理完成！")
        print("现在表格只保留必要的字段，结构更清晰。")
    else:
        print("\n❌ 清理失败")