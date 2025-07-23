#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最终修复测试 - 验证中文标题和顶部插入
"""

import json
import urllib.request
import urllib.parse
import time

# 配置
GNEWS_API_KEY = "c3cb6fef0f86251ada2b515017b97143"
FEISHU_APP_ID = "cli_a8f4efb90f3a1013"
FEISHU_APP_SECRET = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
GNEWS_BASE_URL = "https://gnews.io/api/v4"

def get_feishu_token():
    try:
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        return result.get('tenant_access_token') if result.get('code') == 0 else None
    except:
        return None

def get_latest_news():
    """获取最新AI新闻"""
    try:
        params = {
            'apikey': GNEWS_API_KEY,
            'q': 'AI OR OpenAI OR "artificial intelligence"',
            'lang': 'en',
            'max': '1'  # 只获取1条最新的
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{GNEWS_BASE_URL}/search?{query_string}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'articles' in result and len(result['articles']) > 0:
            return result['articles'][0]
        return None
    except Exception as e:
        print(f"❌ 获取新闻失败: {str(e)}")
        return None

def translate_title_to_chinese(title):
    """改进的中文翻译"""
    if not title:
        return title
        
    translations = {
        # 公司名称
        'OpenAI': 'OpenAI',
        'Google': '谷歌',
        'Microsoft': '微软',
        'Meta': 'Meta',
        'Apple': '苹果',
        'Amazon': '亚马逊',
        'Tesla': '特斯拉',
        'NVIDIA': '英伟达',
        
        # AI技术词汇
        'Artificial Intelligence': '人工智能',
        'AI': 'AI',
        'Machine Learning': '机器学习',
        'Deep Learning': '深度学习',
        'Neural Network': '神经网络',
        'Large Language Model': '大语言模型',
        'ChatGPT': 'ChatGPT',
        'GPT-4': 'GPT-4',
        'GPT-5': 'GPT-5',
        'Gemini': 'Gemini',
        'Bard': 'Bard',
        'Copilot': 'Copilot',
        
        # 动作词汇
        'Launches': '发布',
        'Releases': '发布',
        'Announces': '宣布',
        'Introduces': '推出',
        'Unveils': '揭晓',
        'Updates': '更新',
        'Improves': '改进',
        'Enhances': '增强',
        'Develops': '开发',
        'Creates': '创建',
        'Revolutionary': '革命性',
        'Advanced': '先进的',
        'New': '全新',
        'Latest': '最新',
        'Powerful': '强大的',
        'Smart': '智能',
    }
    
    # 执行翻译
    chinese_title = title
    for en_word, zh_word in translations.items():
        chinese_title = chinese_title.replace(en_word, zh_word)
        chinese_title = chinese_title.replace(en_word.lower(), zh_word)
    
    # 如果还有很多英文，添加中文前缀
    english_chars = sum(1 for c in chinese_title if c.isascii() and c.isalpha())
    total_chars = len(chinese_title.replace(' ', ''))
    
    if total_chars > 0 and english_chars / total_chars > 0.5:
        if any(word in title.lower() for word in ['release', 'launch', 'announce']):
            chinese_title = f"🚀 最新发布：{chinese_title}"
        elif any(word in title.lower() for word in ['breakthrough', 'innovation']):
            chinese_title = f"💡 技术突破：{chinese_title}"
        elif any(word in title.lower() for word in ['update', 'improve', 'enhance']):
            chinese_title = f"🔄 重大更新：{chinese_title}"
        else:
            chinese_title = f"📰 AI资讯：{chinese_title}"
    
    return chinese_title

def get_max_timestamp():
    """获取表格最大时间戳"""
    token = get_feishu_token()
    if not token:
        return int(time.time() * 1000)
    
    try:
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('code') == 0:
            records = result.get('data', {}).get('items', [])
            max_timestamp = int(time.time() * 1000)
            
            for record in records:
                update_date = record.get('fields', {}).get('更新日期', 0)
                if isinstance(update_date, (int, float)) and update_date > max_timestamp:
                    max_timestamp = int(update_date)
            
            return max_timestamp
        
        return int(time.time() * 1000)
    except:
        return int(time.time() * 1000)

def push_news_with_fixes(article):
    """使用修复后的逻辑推送新闻"""
    token = get_feishu_token()
    if not token:
        print("❌ 无法获取飞书令牌")
        return False
    
    # 翻译标题
    chinese_title = translate_title_to_chinese(article.get('title', ''))
    print(f"📰 原标题: {article.get('title', '')}")
    print(f"🇨🇳 中文标题: {chinese_title}")
    
    # 获取最大时间戳并创建更新的时间戳
    max_timestamp = get_max_timestamp()
    future_timestamp = max_timestamp + 120000  # 加2分钟，确保是最新的
    
    print(f"⏰ 使用时间戳: {future_timestamp}")
    print(f"📅 对应时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(future_timestamp/1000))}")
    
    try:
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        record_data = {
            "fields": {
                "标题": chinese_title,
                "摘要": (article.get('description', '') or article.get('content', ''))[:200] + "...",
                "AI观点": "该AI技术发展值得行业关注，可能会带来新的应用场景和商业机会。",
                "中国影响分析": "技术发展：推动国内相关产业升级\\n市场机遇：为企业提供新的发展方向\\n竞争格局：需要评估对现有技术格局的影响",
                "更新日期": future_timestamp,
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
            record_id = result.get('data', {}).get('record', {}).get('record_id')
            print(f"✅ 推送成功！记录ID: {record_id}")
            return True
        else:
            print(f"❌ 推送失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 推送异常: {str(e)}")
        return False

def main():
    print("🔧 最终修复测试 - 中文标题 + 顶部插入")
    print("=" * 60)
    
    # 1. 获取最新新闻
    print("1️⃣ 获取最新AI新闻...")
    article = get_latest_news()
    
    if not article:
        print("❌ 无法获取新闻，使用模拟数据测试")
        article = {
            'title': 'OpenAI Announces Major Breakthrough in Artificial Intelligence Research',
            'description': 'OpenAI has revealed significant advances in AI capabilities...',
            'url': 'https://example.com/openai-breakthrough',
            'source': {'name': 'Tech News Today'}
        }
    
    # 2. 推送新闻
    print("2️⃣ 推送到飞书表格...")
    success = push_news_with_fixes(article)
    
    if success:
        print(f"\n🎉 最终修复测试成功！")
        print(f"📊 新记录应该:")
        print(f"   ✅ 显示在表格第1行（顶部）")
        print(f"   ✅ 标题已翻译为中文")
        print(f"   ✅ 时间戳比现有记录更新")
        print(f"\n🔗 请查看: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
    else:
        print(f"\n❌ 测试失败")

if __name__ == "__main__":
    main()