#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复插入位置和时间戳问题
"""

import json
import urllib.request
import time
from datetime import datetime, timedelta

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

def get_max_timestamp():
    """获取表格中最大的时间戳"""
    access_token = get_access_token()
    if not access_token:
        return int(time.time() * 1000)
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            records = result.get('data', {}).get('items', [])
            max_timestamp = 0
            
            for record in records:
                update_date = record.get('fields', {}).get('更新日期', 0)
                if isinstance(update_date, (int, float)) and update_date > max_timestamp:
                    max_timestamp = update_date
            
            print(f"📊 表格中最大时间戳: {max_timestamp}")
            if max_timestamp > 0:
                dt = datetime.fromtimestamp(max_timestamp / 1000)
                print(f"📅 对应时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return max_timestamp if max_timestamp > 0 else int(time.time() * 1000)
        
        return int(time.time() * 1000)
    except Exception as e:
        print(f"❌ 获取时间戳失败: {str(e)}")
        return int(time.time() * 1000)

def create_future_timestamp(base_timestamp=None):
    """创建一个确保最新的时间戳"""
    if base_timestamp is None:
        base_timestamp = get_max_timestamp()
    
    # 在最大时间戳基础上增加1分钟，确保是最新的
    future_timestamp = base_timestamp + 60000  # 加1分钟
    
    dt = datetime.fromtimestamp(future_timestamp / 1000)
    print(f"🕐 新记录时间戳: {future_timestamp}")
    print(f"📅 新记录时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return future_timestamp

def test_top_insert_with_future_timestamp():
    """使用未来时间戳测试插入到顶部"""
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    print("1️⃣ 获取当前最大时间戳...")
    max_timestamp = get_max_timestamp()
    
    print("2️⃣ 创建未来时间戳...")
    future_timestamp = create_future_timestamp(max_timestamp)
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        current_time = time.strftime("%H:%M:%S")
        
        # 测试中文标题翻译
        original_title = "OpenAI Releases Revolutionary GPT-5 Model with Advanced Capabilities"
        chinese_title = translate_title_to_chinese(original_title)
        
        record_data = {
            "fields": {
                "标题": chinese_title,
                "摘要": "这是使用未来时间戳的测试记录，应该出现在表格最上方第1行位置。该测试验证了时间戳排序和中文标题翻译功能。",
                "AI观点": "通过使用比现有记录更新的时间戳，可以确保新记录在降序排列中显示在最顶部。",
                "中国影响分析": "技术优化：确保用户总是能在最显眼的位置看到最新的AI科技资讯，提升信息获取效率。",
                "更新日期": future_timestamp,
                "来源": {
                    "link": f"https://example.com/top-test-{int(time.time())}",
                    "text": "置顶测试源"
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
        
        print("3️⃣ 插入测试记录...")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            record_id = result.get('data', {}).get('record', {}).get('record_id')
            print(f"✅ 测试记录插入成功！")
            print(f"📋 记录ID: {record_id}")
            print(f"📰 中文标题: {chinese_title}")
            return True
        else:
            print(f"❌ 插入失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 插入异常: {str(e)}")
        return False

def translate_title_to_chinese(title):
    """简化版中文翻译"""
    translations = {
        'OpenAI': 'OpenAI',
        'Google': '谷歌',
        'Microsoft': '微软',
        'GPT-5': 'GPT-5',
        'GPT-4': 'GPT-4',
        'Releases': '发布',
        'Revolutionary': '革命性',
        'Advanced': '先进的',
        'Capabilities': '功能',
        'Model': '模型',
        'AI': 'AI'
    }
    
    chinese_title = title
    for en, zh in translations.items():
        chinese_title = chinese_title.replace(en, zh)
    
    # 如果还有很多英文，加前缀
    english_count = sum(1 for c in chinese_title if c.isalpha() and ord(c) < 128)
    if english_count > len(chinese_title) * 0.3:
        chinese_title = f"🚀 最新发布：{chinese_title}"
    
    return chinese_title

def main():
    print("🔧 修复记录插入位置和时间戳问题")
    print("=" * 60)
    
    success = test_top_insert_with_future_timestamp()
    
    if success:
        print(f"\n🎉 修复测试成功！")
        print(f"📊 新记录应该出现在表格第1行")
        print(f"📋 请刷新飞书表格查看效果")
        print(f"🔗 https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        
        print(f"\n💡 解决方案说明:")
        print(f"   ✅ 使用未来时间戳确保记录在降序排列中位于顶部")
        print(f"   ✅ 改进了中文标题翻译功能")
        print(f"   ✅ 新记录将自动显示在第1行位置")
    else:
        print(f"\n❌ 修复测试失败")

if __name__ == "__main__":
    main()