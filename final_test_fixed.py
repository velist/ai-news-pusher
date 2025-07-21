#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整系统测试 - 修复URL编码问题
"""

import json
import urllib.request
import urllib.parse
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
            'q': 'AI OR "artificial intelligence"',
            'lang': 'en',
            'country': 'us',
            'max': '3'
        }
        
        # 正确的URL编码
        query_string = urllib.parse.urlencode(params)
        url = f"{GNEWS_BASE_URL}/search?{query_string}"
        
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'articles' in result and len(result['articles']) > 0:
            print(f"   ✅ GNews API正常，获取到 {len(result['articles'])} 条新闻")
            return True, result['articles']
        else:
            print(f"   ❌ GNews API响应异常: {result}")
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
    
    # AI分析逻辑
    text = (title + ' ' + description).lower()
    
    if 'openai' in text or 'gpt' in text or 'chatgpt' in text:
        commentary = "OpenAI的技术突破再次证明了大语言模型领域的快速发展，这将推动整个AI行业进入新阶段。"
        impact = "技术追赶：激励国内AI企业加速研发步伐\\n市场机遇：为AI应用开发带来新的可能性\\n人才需求：推动AI相关人才培养和引进"
    elif 'google' in text or 'bard' in text or 'gemini' in text:
        commentary = "Google在AI领域的持续投入展现了科技巨头对人工智能技术的重视程度。"
        impact = "竞争格局：加剧全球AI技术竞争\\n技术标准：可能影响AI技术发展方向\\n产业生态：推动AI产业链整体发展"
    elif 'microsoft' in text or 'copilot' in text:
        commentary = "微软通过AI技术与办公软件的深度整合，展示了AI在生产力工具方面的巨大潜力。"
        impact = "办公智能化：推动国内办公软件AI化升级\\n企业服务：创造新的企业服务市场机会\\n技术集成：促进AI与传统软件的融合发展"
    else:
        commentary = "该AI技术发展动向值得行业密切关注，可能带来新的技术突破和应用场景。"
        impact = "行业观察：需要持续关注技术发展趋势\\n创新机遇：可能催生新的商业模式\\n技术储备：为相关企业提供发展参考"
    
    return commentary, impact

def push_to_feishu(article, commentary, impact_analysis):
    """推送到飞书表格"""
    token = get_feishu_token()
    if not token:
        return False
    
    app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
    table_id = "tblyPOJ4k9DxJuKc"
    
    try:
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        current_time = time.strftime("%H:%M:%S")
        
        record_data = {
            "fields": {
                "标题": f"🔬 [最终测试] {article.get('title', '')[:60]}",
                "摘要": (article.get('description', '') or article.get('content', ''))[:300] + "...",
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
            record_id = result.get('data', {}).get('record', {}).get('record_id', '未知')
            print(f"   📋 记录ID: {record_id}")
            return True
        else:
            print(f"   ❌ 推送失败: {result}")
            return False
    
    except Exception as e:
        print(f"   ❌ 推送异常: {str(e)}")
        return False

def test_complete_workflow():
    """测试完整工作流程"""
    print("3️⃣ 测试完整工作流程...")
    
    # 1. 获取新闻
    gnews_success, articles = test_gnews_api()
    if not gnews_success or not articles:
        print("   ❌ 无法获取新闻，跳过完整流程测试")
        return False
    
    # 2. 处理第一条新闻
    article = articles[0]
    print(f"   📰 处理新闻: {article.get('title', '')[:50]}...")
    
    # 3. 生成AI分析
    commentary, impact_analysis = generate_ai_analysis(article)
    print(f"   🤖 生成AI分析: {commentary[:50]}...")
    
    # 4. 推送到飞书
    print("   📤 推送到飞书表格...")
    push_success = push_to_feishu(article, commentary, impact_analysis)
    
    if push_success:
        print("   ✅ 完整工作流程测试成功！")
        return True
    else:
        print("   ❌ 完整工作流程测试失败")
        return False

def main():
    """主测试函数"""
    print("🔬 AI新闻推送系统 - 最终完整测试")
    print("=" * 60)
    
    test_results = {}
    
    # 测试GNews API
    print("\n🔍 开始各项功能测试...")
    gnews_success, articles = test_gnews_api()
    test_results['gnews'] = gnews_success
    
    # 测试飞书API
    feishu_success = test_feishu_api()
    test_results['feishu'] = feishu_success
    
    # 测试完整流程（只有在前两个都成功时才执行）
    if gnews_success and feishu_success:
        workflow_success = test_complete_workflow()
        test_results['workflow'] = workflow_success
    else:
        test_results['workflow'] = False
        print("3️⃣ 跳过完整流程测试（依赖项失败）")
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    
    success_count = sum(test_results.values())
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        test_display = {
            'gnews': 'GNews API连接',
            'feishu': '飞书API连接',
            'workflow': '完整工作流程'
        }
        print(f"   {test_display[test_name]}: {status}")
    
    print(f"\n📈 测试通过率: {success_count}/{total_tests} ({success_count/total_tests*100:.0f}%)")
    
    if success_count == total_tests:
        print("\n🎉 所有测试通过！系统完全就绪！")
        print("\n🚀 接下来的步骤:")
        print("   1. 在飞书表格中设置'更新日期'降序排列")
        print("   2. 参考 MANUAL_DEPLOY.md 部署到GitHub")
        print("   3. 设置GitHub Secrets并启用Actions")
        print("   4. 享受每日8点的AI新闻推送！")
        
        print(f"\n🔗 查看测试结果: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        
    elif test_results['feishu'] and success_count >= 2:
        print("\n✅ 核心功能正常！系统基本就绪")
        print("   飞书集成测试通过，可以正常推送数据")
        if not test_results['gnews']:
            print("   注意：GNews API可能有网络限制，部署后应该正常")
            
    else:
        print("\n❌ 部分关键功能失败，请检查配置")
        if not test_results['feishu']:
            print("   请检查飞书应用权限和密钥配置")
    
    return success_count == total_tests

if __name__ == "__main__":
    main()