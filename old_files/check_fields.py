#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查表格字段详情
"""

import json
import urllib.request

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

def check_fields():
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {access_token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            fields = result.get('data', {}).get('items', [])
            
            print(f"📋 表格字段详情 ({len(fields)} 个):")
            print("-" * 80)
            
            field_types = {
                1: "文本", 2: "数字", 3: "单选", 4: "多选", 5: "日期时间",
                7: "复选框", 11: "人员", 13: "电话", 15: "URL链接", 
                17: "附件", 18: "关联", 20: "公式", 21: "创建时间",
                22: "修改时间", 23: "创建人", 24: "修改人"
            }
            
            text_fields = []
            url_fields = []
            datetime_fields = []
            
            for field in fields:
                name = field.get('field_name', '')
                field_type = field.get('type', 0)
                field_id = field.get('field_id', '')
                type_name = field_types.get(field_type, f"未知类型({field_type})")
                
                print(f"   {name:<15} | 类型: {type_name:<8} | ID: {field_id}")
                
                # 分类字段
                if field_type == 1:  # 文本
                    text_fields.append(name)
                elif field_type == 15:  # URL
                    url_fields.append(name)
                elif field_type == 5:  # 日期时间
                    datetime_fields.append(name)
            
            print("\n📝 字段分类:")
            print(f"   文本字段: {text_fields}")
            print(f"   URL字段: {url_fields}")
            print(f"   日期字段: {datetime_fields}")
            
            # 建议字段映射
            print("\n💡 建议的字段映射:")
            mapping = {
                "标题": "标题",
                "摘要": "摘要", 
                "AI点评": "AI观点" if "AI观点" in text_fields else "点评",
                "影响分析": "中国影响分析",
                "发布时间": "更新日期" if "更新日期" in datetime_fields else "发布时间",
                "来源": "来源"
            }
            
            for key, value in mapping.items():
                print(f"   {key} -> {value}")
        
    except Exception as e:
        print(f"❌ 检查字段异常: {str(e)}")

def test_with_correct_fields():
    """使用正确的字段进行测试"""
    access_token = get_access_token()
    if not access_token:
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        # 使用原有字段进行映射
        record_data = {
            "fields": {
                "标题": "🚀 [测试] OpenAI发布GPT-4 Turbo最新版本",
                "摘要": "最新版本在推理能力和多模态理解方面显著改进，成本降低。",
                "AI观点": "这次升级体现了OpenAI持续创新能力，将推动AI技术普及和商业化应用。",
                "更新日期": int(time.time() * 1000)
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
            print("\n✅ 测试推送成功！")
            print(f"📋 记录ID: {result.get('data', {}).get('record', {}).get('record_id', '未知')}")
            return True
        else:
            print(f"\n❌ 测试推送失败: {result}")
            return False
    
    except Exception as e:
        print(f"\n❌ 推送异常: {str(e)}")
        return False

if __name__ == "__main__":
    import time
    
    print("🔍 检查飞书表格字段详情...")
    print("=" * 80)
    
    check_fields()
    
    print("\n" + "=" * 80)
    print("🧪 使用正确字段进行测试推送...")
    
    success = test_with_correct_fields()
    
    if success:
        print("\n🎉 测试完成！AI新闻成功推送到飞书表格！")
        print("🔗 请查看您的表格: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
    else:
        print("\n❌ 测试失败")