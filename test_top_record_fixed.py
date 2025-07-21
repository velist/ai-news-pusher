#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试在表格顶部插入记录 - 修复版本
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

def add_record_at_top():
    """在表格顶部插入新记录"""
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        # 测试数据 - 使用正确的URL字段格式
        record_data = {
            "fields": {
                "标题": "🆕 [最新测试] AI新闻置顶测试 - " + time.strftime("%H:%M:%S"),
                "摘要": "这是一条测试记录，用于验证新记录是否会出现在表格最上方。时间戳确保每次都是最新的。",
                "AI观点": "测试成功表明系统能够正确地将最新新闻放置在表格顶部，符合用户阅读习惯。",
                "中国影响分析": "技术验证：确保自动化新闻推送系统的用户体验优化功能正常工作，提升信息获取效率。",
                "更新日期": int(time.time() * 1000),
                "来源": {
                    "link": "https://example.com/test-news-" + str(int(time.time())),
                    "text": "测试新闻源"
                }
            }
        }
        
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
            return True
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
        print("\n✅ 测试完成！新记录已添加到表格")
        print("🔗 https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        print("\n💡 重要提醒:")
        print("   为确保最新记录显示在顶部，请在飞书表格中:")
        print("   1. 点击'更新日期'列标题")
        print("   2. 选择降序排列（最新在上）") 
        print("   3. 设置为默认排序")
    else:
        print("\n❌ 测试失败")

if __name__ == "__main__":
    main()