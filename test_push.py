#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试推送单条新闻到飞书多维表格
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from feishu_client import FeishuClient
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_single_push():
    """测试推送单条新闻"""
    
    # 创建飞书客户端
    feishu_client = FeishuClient()
    
    # 构造测试新闻数据
    test_news = [{
        'title': '🚀 [测试] OpenAI发布GPT-4 Turbo最新版本，性能大幅提升',
        'description': '最新发布的GPT-4 Turbo版本在推理能力、多模态理解和代码生成方面都有显著改进，同时降低了API调用成本。该版本支持更长的上下文窗口，能够处理更复杂的任务。',
        'image': 'https://cdn.openai.com/API/gpt4-turbo-announcement.png',
        'commentary': '这次GPT-4 Turbo的升级体现了OpenAI在大语言模型领域的持续创新能力。性能提升的同时成本降低，将进一步推动AI技术的普及和商业化应用，对整个AI行业具有重要的引领作用。',
        'china_impact_analysis': '''对中国影响：
1. 技术追赶：促进国内大模型技术发展，推动百度文心一言、阿里通义千问等产品迭代升级
2. 商业机会：为国内AI应用开发者提供新的技术参考，催生更多创新应用场景
3. 竞争格局：加剧国际AI技术竞争，推动中国加大AI研发投入和人才培养力度''',
        'url': 'https://openai.com/blog/gpt-4-turbo-preview',
        'publishedAt': datetime.now().isoformat(),
        'source': 'OpenAI官方博客'
    }]
    
    print("🔄 开始测试推送到飞书多维表格...")
    print(f"📰 测试新闻: {test_news[0]['title']}")
    print(f"🔗 飞书表格: {feishu_client.config.FEISHU_TABLE_URL}")
    print("-" * 60)
    
    # 执行推送
    success = feishu_client.push_news_to_table(test_news)
    
    if success:
        print("✅ 测试推送成功！")
        print("📋 请检查您的飞书多维表格，应该能看到测试新闻记录")
        print(f"🔗 表格链接: {feishu_client.config.FEISHU_TABLE_URL}")
    else:
        print("❌ 测试推送失败")
        print("💡 请检查:")
        print("   1. 飞书应用权限是否正确配置")
        print("   2. APP ID和Secret是否正确")
        print("   3. 网络连接是否正常")
    
    return success

if __name__ == "__main__":
    test_single_push()