#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试改进的中文翻译 - 覆盖更多词汇
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

def improved_translate_title(title):
    """改进的中文翻译 - 覆盖更多场景"""
    if not title:
        return title
        
    # 扩展的翻译词典
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
        'Anthropic': 'Anthropic',
        'Facebook': '脸书',
        'Twitter': '推特',
        'ByteDance': '字节跳动',
        'Alphabet': '谷歌母公司',
        
        # AI技术词汇
        'Artificial Intelligence': '人工智能',
        'AI': 'AI',
        'Machine Learning': '机器学习',
        'Deep Learning': '深度学习',
        'Neural Network': '神经网络',
        'Large Language Model': '大语言模型',
        'LLM': '大语言模型',
        'ChatGPT': 'ChatGPT',
        'GPT': 'GPT',
        'GPT-4': 'GPT-4',
        'GPT-5': 'GPT-5',
        'Gemini': 'Gemini',
        'Bard': 'Bard',
        'Copilot': 'Copilot',
        'Algorithm': '算法',
        'Model': '模型',
        'Technology': '技术',
        'Platform': '平台',
        'System': '系统',
        'Tool': '工具',
        'Software': '软件',
        'Application': '应用',
        'Feature': '功能',
        'Update': '更新',
        'Version': '版本',
        
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
        'Builds': '构建',
        'Plans': '计划',
        'Reveals': '揭示',
        'Shows': '展示',
        'Demos': '演示',
        'Tests': '测试',
        'Trials': '试验',
        
        # 描述词汇
        'Revolutionary': '革命性',
        'Breakthrough': '突破性',
        'Advanced': '先进的',
        'New': '全新',
        'Latest': '最新',
        'Next-Generation': '下一代',
        'Powerful': '强大的',
        'Smart': '智能',
        'Intelligent': '智能的',
        'Innovative': '创新的',
        'Cutting-edge': '前沿的',
        'State-of-the-art': '最先进的',
        'Major': '重大',
        'Significant': '重要',
        'Important': '重要',
        'Big': '重大',
        'Huge': '巨大',
        'Massive': '大规模',
        
        # 应用领域
        'Healthcare': '医疗',
        'Education': '教育',
        'Finance': '金融',
        'Automotive': '汽车',
        'Robotics': '机器人',
        'Gaming': '游戏',
        'Research': '研究',
        'Development': '开发',
        'Business': '商业',
        'Enterprise': '企业',
        'Industry': '行业',
        'Market': '市场',
        'Economy': '经济',
        
        # 常见词汇
        'Says': '表示',
        'Reports': '报告',
        'Study': '研究',
        'Analysis': '分析',
        'Data': '数据',
        'Report': '报告',
        'Survey': '调查',
        'News': '新闻',
        'Story': '报道',
        'Article': '文章',
        'Post': '发布',
        'Blog': '博客',
        'Interview': '采访',
        'Conference': '会议',
        'Event': '活动',
        'Summit': '峰会',
        'Forum': '论坛',
        
        # 其他关键词
        'Future': '未来',
        'Trend': '趋势',
        'Challenge': '挑战',
        'Opportunity': '机遇',
        'Solution': '解决方案',
        'Impact': '影响',
        'Change': '变化',
        'Growth': '增长',
        'Success': '成功',
        'Failure': '失败',
        'Risk': '风险',
        'Safety': '安全',
        'Security': '安全',
        'Privacy': '隐私',
        'Ethics': '伦理',
        'Regulation': '监管',
        'Policy': '政策',
        'Law': '法律',
        'Government': '政府',
        'Industry': '行业',
        'Competition': '竞争',
        'Investment': '投资',
        'Funding': '资金',
        'Startup': '初创公司',
        'Company': '公司',
        'Corporation': '公司',
        'Firm': '公司',
        'Organization': '机构',
        'Institution': '机构',
        'University': '大学',
        'College': '学院',
        'School': '学校',
        'Department': '部门',
        'Team': '团队',
        'Group': '集团',
        'Lab': '实验室',
        'Laboratory': '实验室',
        'Center': '中心',
        'Institute': '研究所',
    }
    
    # 执行翻译
    chinese_title = title
    
    # 按长度排序，先替换长词组
    sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
    
    for en_word, zh_word in sorted_translations:
        # 使用更精确的替换方式
        import re
        # 替换完整单词，避免部分匹配
        pattern = r'\b' + re.escape(en_word) + r'\b'
        chinese_title = re.sub(pattern, zh_word, chinese_title, flags=re.IGNORECASE)
    
    # 清理多余空格
    chinese_title = ' '.join(chinese_title.split())
    
    # 如果翻译后还有很多英文，添加中文前缀
    english_chars = sum(1 for c in chinese_title if c.isascii() and c.isalpha())
    total_meaningful_chars = len([c for c in chinese_title if c.isalnum() or ord(c) > 127])
    
    if total_meaningful_chars > 0 and english_chars / total_meaningful_chars > 0.4:
        # 根据内容添加更精确的前缀
        title_lower = title.lower()
        if any(word in title_lower for word in ['launch', 'release', 'announce', 'unveil']):
            chinese_title = f"🚀 最新发布：{chinese_title}"
        elif any(word in title_lower for word in ['breakthrough', 'innovation', 'revolutionary']):
            chinese_title = f"💡 技术突破：{chinese_title}"
        elif any(word in title_lower for word in ['update', 'improve', 'enhance', 'upgrade']):
            chinese_title = f"🔄 重大更新：{chinese_title}"
        elif any(word in title_lower for word in ['study', 'research', 'analysis', 'report']):
            chinese_title = f"📊 研究报告：{chinese_title}"
        elif any(word in title_lower for word in ['warn', 'risk', 'danger', 'threat']):
            chinese_title = f"⚠️  风险警示：{chinese_title}"
        elif any(word in title_lower for word in ['invest', 'funding', 'money', 'billion']):
            chinese_title = f"💰 投资动态：{chinese_title}"
        else:
            chinese_title = f"📰 AI资讯：{chinese_title}"
    
    return chinese_title

def get_real_news_and_test():
    """获取真实新闻并测试翻译"""
    try:
        params = {
            'apikey': GNEWS_API_KEY,
            'q': 'AI OR OpenAI OR "artificial intelligence"',
            'lang': 'en',
            'max': '3'
        }
        
        query_string = urllib.parse.urlencode(params)
        url = f"{GNEWS_BASE_URL}/search?{query_string}"
        
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if 'articles' in result and len(result['articles']) > 0:
            articles = result['articles']
            
            print("📰 真实新闻翻译测试")
            print("=" * 80)
            
            for i, article in enumerate(articles, 1):
                original_title = article.get('title', '')
                chinese_title = improved_translate_title(original_title)
                
                print(f"\n{i}. 原标题:")
                print(f"   {original_title}")
                print(f"   中文翻译:")
                print(f"   {chinese_title}")
                print(f"   来源: {article.get('source', {}).get('name', '未知')}")
            
            return articles[0]  # 返回第一条用于测试推送
        
    except Exception as e:
        print(f"❌ 获取新闻失败: {str(e)}")
    
    return None

def push_with_improved_translation(article):
    """使用改进翻译推送新闻"""
    token = get_feishu_token()
    if not token:
        return False
    
    chinese_title = improved_translate_title(article.get('title', ''))
    
    # 获取最大时间戳
    try:
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        
        # 获取当前最大时间戳
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        max_timestamp = int(time.time() * 1000)
        if result.get('code') == 0:
            records = result.get('data', {}).get('items', [])
            for record in records:
                update_date = record.get('fields', {}).get('更新日期', 0)
                if isinstance(update_date, (int, float)) and update_date > max_timestamp:
                    max_timestamp = int(update_date)
        
        # 使用更新的时间戳
        future_timestamp = max_timestamp + 180000  # 加3分钟
        
        # 推送数据
        url = f"{FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
        
        record_data = {
            "fields": {
                "标题": chinese_title,
                "摘要": (article.get('description', '') or article.get('content', ''))[:200] + "...",
                "AI观点": "该AI技术发展值得行业关注，体现了人工智能领域的持续创新和进步。",
                "中国影响分析": "技术发展：推动国内AI产业升级和技术创新\\n市场机遇：为相关企业提供新的发展机会\\n人才需求：促进AI相关人才培养和技术储备",
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
            print(f"\n✅ 改进翻译推送成功！")
            print(f"📰 中文标题: {chinese_title}")
            return True
        else:
            print(f"❌ 推送失败: {result}")
            return False
    
    except Exception as e:
        print(f"❌ 推送异常: {str(e)}")
        return False

def main():
    print("🌏 改进版中文翻译测试")
    print("=" * 60)
    
    # 获取真实新闻并测试翻译
    article = get_real_news_and_test()
    
    if article:
        print(f"\n📤 推送改进翻译版本到飞书...")
        success = push_with_improved_translation(article)
        
        if success:
            print(f"\n🎉 改进版翻译测试成功！")
            print(f"🔗 查看结果: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
    else:
        print(f"❌ 无法获取新闻进行测试")

if __name__ == "__main__":
    main()