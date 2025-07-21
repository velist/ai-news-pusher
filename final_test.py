#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终测试推送 - 使用现有字段映射
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
        return None
    except:
        return None

def add_test_record():
    """添加测试记录"""
    access_token = get_access_token()
    if not access_token:
        print("❌ 无法获取访问令牌")
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        # 使用现有字段结构，根据之前看到的字段映射
        record_data = {
            "fields": {
                "标题": "🚀 [测试] OpenAI发布GPT-4 Turbo最新版本，性能大幅提升",
                "摘要": "最新发布的GPT-4 Turbo版本在推理能力、多模态理解和代码生成方面都有显著改进，同时降低了API调用成本。该版本支持更长的上下文窗口，能够处理更复杂的任务。",
                "来源链接": "https://openai.com/blog/gpt-4-turbo-preview",
                "点评": "这次GPT-4 Turbo的升级体现了OpenAI在大语言模型领域的持续创新能力。性能提升的同时成本降低，将进一步推动AI技术的普及和商业化应用。",
                "中国影响分析": "技术追赶：促进国内大模型技术发展，推动百度文心一言、阿里通义千问等产品迭代升级\\n商业机会：为国内AI应用开发者提供新的技术参考\\n竞争格局：加剧国际AI技术竞争",
                "发布时间": int(time.time() * 1000)  # 当前时间戳（毫秒）
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
            print("✅ 测试记录推送成功！")
            print(f"📋 记录ID: {result.get('data', {}).get('record', {}).get('record_id', '未知')}")
            return True
        else:
            print(f"❌ 推送失败: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 推送异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 最终测试：推送AI新闻到飞书多维表格")
    print(f"🔗 目标表格: {FEISHU_TABLE_URL}")
    print("-" * 60)
    
    success = add_test_record()
    
    if success:
        print("\n🎉 测试成功！AI新闻已成功推送到您的飞书多维表格！")
        print("\n📋 请检查您的飞书表格，您应该能看到:")
        print("   ✅ 标题: 🚀 [测试] OpenAI发布GPT-4 Turbo最新版本")
        print("   ✅ 完整的摘要内容")
        print("   ✅ AI生成的点评")
        print("   ✅ 中国影响分析")
        print("   ✅ 来源链接")
        print("   ✅ 发布时间")
        print(f"\n🔗 立即查看: {FEISHU_TABLE_URL}")
        print("\n🤖 系统已准备就绪，可以开始自动化部署了！")
    else:
        print("\n❌ 测试失败，请检查配置")
    
    return success

if __name__ == "__main__":
    main()