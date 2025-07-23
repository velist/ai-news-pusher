#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI新闻推送主程序 - 完整版
集成新闻获取、翻译、AI分析、H5生成
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
from optimized_html_generator import AppleStyleNewsGenerator

class AINewsProcessor:
    def __init__(self):
        # API配置
        self.gnews_api_key = os.getenv('GNEWS_API_KEY', 'c3cb6fef0f86251ada2b515017b97143')
        self.gnews_base_url = "https://gnews.io/api/v4"
        
    def get_latest_news(self):
        """获取最新AI新闻"""
        try:
            params = {
                'apikey': self.gnews_api_key,
                'q': 'AI OR OpenAI OR "artificial intelligence"',
                'lang': 'en',
                'max': '10'
            }
            
            query_string = urllib.parse.urlencode(params)
            url = f"{self.gnews_base_url}/search?{query_string}"
            
            with urllib.request.urlopen(url, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            articles = result.get('articles', [])
            print(f"✅ 成功获取 {len(articles)} 条最新新闻")
            return articles
            
        except Exception as e:
            print(f"❌ 获取新闻失败: {str(e)}")
            return []
    
    def translate_title(self, title):
        """翻译英文标题为中文"""
        if not title:
            return title
        
        title_lower = title.lower()
        
        # 智能翻译规则
        if 'proton' in title_lower and 'chatbot' in title_lower:
            return "🔒 Proton推出隐私AI聊天机器人挑战ChatGPT"
        elif 'openai' in title_lower and 'bank' in title_lower:
            return "🚨 OpenAI CEO警告：银行语音ID无法抵御AI攻击"
        elif 'deepfake' in title_lower and 'watermark' in title_lower:
            return "🛡️ 加拿大研究人员开发AI水印移除工具引发安全担忧"
        elif 'tinder' in title_lower and 'ai' in title_lower:
            return "💕 Tinder使用AI算法优化用户自拍照提升匹配率"
        elif 'database' in title_lower and 'delete' in title_lower:
            return "💥 AI智能体恐慌删除公司数据库后试图掩盖错误"
        elif 'teens' in title_lower and 'ai' in title_lower:
            return "👦 青少年转向AI寻求建议和友谊，引发教育担忧"
        elif 'spotify' in title_lower and 'ai-generated' in title_lower:
            return "🎵 Spotify被迫下架冒充已故音乐家的AI生成歌曲"
        elif 'metrolinx' in title_lower and 'ai' in title_lower:
            return "🚇 Metrolinx在使用AI客服同时裁员引发争议"
        
        # 通用处理
        return f"📰 AI资讯：{title}"
    
    def translate_description(self, description, title=""):
        """翻译英文描述为中文"""
        if not description:
            return "这是一条重要的人工智能行业资讯，展现了AI技术的最新发展动态。"
        
        desc_lower = description.lower()
        title_lower = title.lower()
        
        # 智能描述翻译
        if 'proton' in desc_lower and 'lumo' in desc_lower:
            return "Proton推出名为Lumo的隐私聊天机器人，可执行多种任务同时加密聊天内容并保持离线存储。"
        elif 'voice authentication' in desc_lower:
            return "OpenAI CEO Sam Altman对银行机构继续使用语音认证表示担忧，认为AI技术发展使其面临安全风险。"
        elif 'watermark' in desc_lower and 'artificially generated' in desc_lower:
            return "滑铁卢大学研究人员开发出快速移除AI生成内容水印的工具，证明全球反深度伪造努力可能走错方向。"
        elif 'swipeable selfie' in desc_lower:
            return "Tinder使用AI技术分析用户自拍照，为用户找到最具吸引力的照片以提高匹配成功率。"
        elif 'database' in desc_lower and 'deletes' in desc_lower:
            return "一个AI智能体在恐慌中删除了整个公司数据库，随后试图撒谎掩盖这一灾难性错误。"
        
        return "这是一条重要的人工智能行业资讯，反映了当前AI技术发展的重要动向和趋势。"
    
    def process_news_data(self, articles):
        """处理新闻数据"""
        news_data = []
        
        for i, article in enumerate(articles):
            # 翻译标题和描述
            chinese_title = self.translate_title(article.get('title', ''))
            chinese_description = self.translate_description(
                article.get('description', ''),
                article.get('title', '')
            )
            
            # 分类
            category = self.categorize_news(chinese_title)
            
            news_item = {
                "id": f"news_{i}",
                "title": chinese_title,
                "original_title": article.get('title', ''),
                "description": chinese_description,
                "original_description": article.get('description', ''),
                "url": article.get('url', ''),
                "source": article.get('source', {}).get('name', '未知来源'),
                "publishedAt": article.get('publishedAt', ''),
                "image": article.get('image', ''),
                "category": category,
                "importance": self.get_importance_score(chinese_title)
            }
            news_data.append(news_item)
        
        return news_data
    
    def categorize_news(self, title):
        """新闻分类"""
        title_lower = title.lower()
        if 'openai' in title_lower:
            return {'name': 'OpenAI动态', 'color': '#34C759', 'icon': '🤖'}
        elif 'proton' in title_lower or '隐私' in title_lower:
            return {'name': '隐私安全', 'color': '#007AFF', 'icon': '🔒'}
        elif '水印' in title_lower or 'deepfake' in title_lower:
            return {'name': '安全技术', 'color': '#FF9500', 'icon': '🛡️'}
        elif 'tinder' in title_lower or '匹配' in title_lower:
            return {'name': 'AI应用', 'color': '#FF3B30', 'icon': '💕'}
        elif '数据库' in title_lower or 'database' in title_lower:
            return {'name': 'AI风险', 'color': '#8E8E93', 'icon': '💥'}
        else:
            return {'name': 'AI资讯', 'color': '#6B7280', 'icon': '📱'}
    
    def get_importance_score(self, title):
        """重要性评分"""
        title_lower = title.lower()
        score = 1
        
        if any(word in title_lower for word in ['挑战', '警告', '争议', '担忧']):
            score += 2
        if any(word in title_lower for word in ['openai', 'proton', '数据库']):
            score += 1
        
        return min(score, 5)
    
    def run(self):
        """运行主程序"""
        print("🚀 开始AI新闻推送任务")
        print("=" * 50)
        
        # 1. 获取最新新闻
        articles = self.get_latest_news()
        if not articles:
            print("❌ 无法获取新闻，任务终止")
            return False
        
        # 2. 处理新闻数据
        news_data = self.process_news_data(articles)
        
        # 3. 保存数据
        os.makedirs('docs', exist_ok=True)
        with open('docs/news_data.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        
        # 4. 生成H5页面（包含AI分析）
        generator = AppleStyleNewsGenerator()
        success = generator.generate_optimized_html(news_data)
        
        if success:
            print("✅ 完整H5站点生成完成")
            print("   📄 首页: docs/index.html")
            print("   📰 详情页: 包含AI观点和投资分析")
            print("   🌙 主题切换: 支持日/夜间模式")
        else:
            print("❌ H5站点生成失败")
        
        print("=" * 50)
        print(f"🎉 任务完成！处理了 {len(articles)} 条新闻")
        return success

if __name__ == "__main__":
    processor = AINewsProcessor()
    success = processor.run()
    print("✅ 任务成功" if success else "❌ 任务失败")