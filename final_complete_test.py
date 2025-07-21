#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整系统测试 - 不依赖外部包
"""

import json
import urllib.request
import time

# 直接配置信息
GNEWS_API_KEY = "c3cb6fef0f86251ada2b515017b97143"
FEISHU_APP_ID = "cli_a8f4efb90f3a1013"
FEISHU_APP_SECRET = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
GNEWS_BASE_URL = "https://gnews.io/api/v4"

def test_gnews_api():
    """测试GNews API连接"""
    print("1️⃣ 测试GNews API连接...")
    try:
        params = {
            'apikey': GNEWS_API_KEY,
            'q': 'artificial intelligence',
            'lang': 'en',
            'country': 'us',
            'max': 3
        }
        
        # 构建URL
        url = f"{GNEWS_BASE_URL}/search?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'articles' in result and len(result['articles']) > 0:
            print(f"   ✅ GNews API正常，获取到 {len(result['articles'])} 条新闻")
            return True, result['articles']
        else:
            print(f"   ❌ GNews API异常: {result}")
            return False, []
            
    except Exception as e:
        print(f"   ❌ GNews API连接失败: {str(e)}")
        return False, []

def get_feishu_token():
    """获取飞书访问令牌"""
    try:
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        return result.get('tenant_access_token') if result.get('code') == 0 else None
    except:
        return None

def test_feishu_api():
    """测试飞书API连接"""
    print("2️⃣ 测试飞书API连接...")
    
    token = get_feishu_token()
    if not token:
        print("   ❌ 飞书API认证失败")
        return False
        
    print("   ✅ 飞书API认证成功")
    return True

def generate_ai_analysis(article):
    """生成AI分析"""
    title = article.get('title', '')
    description = article.get('description', '')
    
    # 简单的关键词分析
    text = (title + ' ' + description).lower()
    
    if 'openai' in text or 'gpt' in text:
        commentary = "这项OpenAI的技术进展体现了大语言模型领域的持续创新能力。"
        impact = "技术追赶：推动国内AI企业如百度、阿里加速大模型研发\\n商业机遇：为相关应用开发提供新的技术参考"
    elif 'ai' in text or 'artificial intelligence' in text:
        commentary = "该AI技术发展值得行业关注，可能会带来新的应用场景。"
        impact = "产业升级：推动传统行业智能化转型\\n投资热点：可能成为新的投资方向"
    else:
        commentary = "这一技术动向值得持续关注，可能对行业产生重要影响。"
        impact = "行业观察：需要评估对现有技术格局的潜在影响\\n发展机遇：为相关企业带来新的发展机会"
    
    return commentary, impact

def test_complete_workflow():
    """测试完整工作流程"""
    print("3️⃣ 测试完整工作流程...")
    
    # 1. 获取新闻
    gnews_success, articles = test_gnews_api()
    if not gnews_success or not articles:
        return False
    
    # 2. 测试飞书连接
    feishu_success = test_feishu_api()
    if not feishu_success:
        return False
    
    # 3. 处理第一条新闻
    article = articles[0]
    commentary, impact_analysis = generate_ai_analysis(article)
    
    # 4. 推送到飞书
    token = get_feishu_token()
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        current_time = time.strftime("%H:%M:%S")
        
        record_data = {
            "fields": {
                "标题": f"🧪 [完整测试] {article.get('title', '')[:50]}",
                "摘要": article.get('description', '')[:200] + "...",
                "AI观点": commentary,
                "中国影响分析": impact_analysis,
                "更新日期": int(time.time() * 1000),
                "来源": {
                    "link": article.get('url', ''),
                    "text": article.get('source', {}).get('name', '新闻源')
                }
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(record_data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            print("   ✅ 完整工作流程测试成功！")
            print(f"   📰 测试新闻: {article.get('title', '')[:60]}...")
            print(f"   🤖 AI分析: {commentary[:60]}...")
            return True
        else:
            print(f"   ❌ 推送失败: {result}")
            return False
    
    except Exception as e:
        print(f"   ❌ 工作流程异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🧪 AI新闻推送系统 - 完整功能测试")
    print("=" * 60)
    
    all_tests_passed = True
    
    # 测试GNews API
    gnews_success, _ = test_gnews_api()
    if not gnews_success:
        all_tests_passed = False
    
    # 测试飞书API
    feishu_success = test_feishu_api()
    if not feishu_success:
        all_tests_passed = False
    
    # 测试完整流程
    workflow_success = test_complete_workflow()
    if not workflow_success:
        all_tests_passed = False
    
    print("\n" + "=" * 60)
    
    if all_tests_passed:
        print("🎉 所有测试通过！系统完全就绪")
        print("\n📊 系统状态:")
        print("   ✅ GNews API - 新闻获取正常")
        print("   ✅ 飞书API - 数据推送正常")
        print("   ✅ AI分析 - 内容生成正常")
        print("   ✅ 完整流程 - 端到端测试通过")
        
        print("\n🚀 现在可以部署到GitHub了！")
        print("📋 部署步骤: 参考 MANUAL_DEPLOY.md")
        print("🔗 查看测试结果: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        
        print("\n⚠️  重要提醒:")
        print("   请在飞书表格中设置'更新日期'降序排列")
        print("   这样新记录会自动显示在第1行顶部！")
        
    else:
        print("❌ 部分测试失败，请检查配置")
        
    return all_tests_passed

if __name__ == "__main__":
    main()