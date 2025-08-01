#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户体验最终版测试 - 专注于翻译和AI点评功能测试
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
import sys
import time
import hashlib

def load_env_file():
    """加载环境变量"""
    env_path = '.env'
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            return True
        except Exception as e:
            print(f"环境变量加载失败: {e}")
            return False
    return False

class SiliconFlowTranslator:
    """硅基流动翻译服务"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
    def translate_text(self, text, target_lang='zh'):
        """翻译文本"""
        if not text or not text.strip():
            return ""
            
        try:
            # 针对新闻标题优化的翻译提示
            if len(text) < 100:  # 短文本，可能是标题
                prompt = f"""请将以下英文新闻标题翻译成中文，要求：
1. 保持新闻的准确性和时效性
2. 使用符合中文表达习惯的语言
3. 突出关键信息，适合中文读者理解
4. 只返回翻译结果，不要解释

英文标题：{text}

中文翻译："""
            else:  # 长文本，可能是摘要
                prompt = f"""请将以下英文新闻摘要翻译成中文，要求：
1. 保持新闻的客观性和准确性
2. 使用流畅自然的中文表达
3. 保留重要的人名、地名和专业术语
4. 只返回翻译结果，不要解释

英文摘要：{text}

中文翻译："""
            
            payload = {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 1024
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(self.base_url, data=data, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'choices' in result and result['choices']:
                translated = result['choices'][0]['message']['content'].strip()
                # 清理可能的格式问题
                if translated.startswith('中文翻译：'):
                    translated = translated[5:].strip()
                return translated
            
        except Exception as e:
            print(f"翻译失败: {e}")
            
        return text  # 翻译失败返回原文

class AICommentator:
    """AI点评生成器"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
    def generate_commentary(self, title, summary, category="AI科技"):
        """生成AI点评"""
        try:
            prompt = f"""作为AI行业专家，请为以下新闻撰写一段专业点评，要求：

1. 分析新闻的行业意义和影响
2. 指出技术发展趋势或商业价值
3. 对普通读者提供易懂的解读
4. 控制在80-120字以内
5. 语言要专业但不晦涩

新闻分类：{category}
新闻标题：{title}
新闻摘要：{summary}

专家点评："""
            
            payload = {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 512
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(self.base_url, data=data, headers=headers)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'choices' in result and result['choices']:
                commentary = result['choices'][0]['message']['content'].strip()
                if commentary.startswith('专家点评：'):
                    commentary = commentary[5:].strip()
                return commentary
                
        except Exception as e:
            print(f"AI点评生成失败: {e}")
            
        return ""

def test_translation_and_commentary():
    """测试翻译和AI点评功能"""
    print("🧪 测试翻译和AI点评功能")
    print("=" * 50)
    
    # 加载环境变量
    load_env_file()
    
    siliconflow_api_key = os.getenv('SILICONFLOW_API_KEY')
    if not siliconflow_api_key:
        print("❌ 缺少SILICONFLOW_API_KEY")
        return False
    
    # 初始化服务
    translator = SiliconFlowTranslator(siliconflow_api_key)
    commentator = AICommentator(siliconflow_api_key)
    
    # 测试文章
    test_articles = [
        {
            "title": "OpenAI raises $8.3 billion as paid ChatGPT users reach 5 million",
            "summary": "OpenAI's competition with Anthropic and other AI model makers is driving record investor demand.",
            "category": "热门"
        },
        {
            "title": "Google rolls out Gemini Deep Think AI",
            "summary": "Google released its first publicly available multi-agent AI system, which uses more computational resources, but produces better answers.",
            "category": "公司动态"
        }
    ]
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n🔍 测试第 {i} 条新闻:")
        print(f"原标题: {article['title']}")
        
        # 测试翻译
        print("🌐 翻译标题...")
        translated_title = translator.translate_text(article['title'])
        print(f"中文标题: {translated_title}")
        
        print("🌐 翻译摘要...")
        translated_summary = translator.translate_text(article['summary'])
        print(f"中文摘要: {translated_summary}")
        
        # 测试AI点评
        print("🤖 生成AI点评...")
        commentary = commentator.generate_commentary(
            translated_title, 
            translated_summary, 
            article['category']
        )
        print(f"AI点评: {commentary}")
        
        print("-" * 40)
        time.sleep(2)  # 避免过于频繁的API调用
    
    print("\n✅ 翻译和AI点评功能测试完成!")
    return True

def enhance_existing_articles():
    """增强现有文章（添加翻译和AI点评）"""
    print("\n🚀 开始增强现有文章...")
    
    # 读取现有数据
    try:
        with open('docs/news_data.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取现有数据失败: {e}")
        return False
    
    articles = news_data.get('articles', [])
    if not articles:
        print("❌ 没有找到现有文章")
        return False
    
    # 加载环境变量
    load_env_file()
    siliconflow_api_key = os.getenv('SILICONFLOW_API_KEY')
    if not siliconflow_api_key:
        print("❌ 缺少SILICONFLOW_API_KEY")
        return False
    
    # 初始化服务
    translator = SiliconFlowTranslator(siliconflow_api_key)
    commentator = AICommentator(siliconflow_api_key)
    
    # 只处理前10条文章（避免API调用过多）
    enhanced_articles = []
    for i, article in enumerate(articles[:10], 1):
        print(f"\n处理第 {i}/10 条: {article.get('title', '')[:50]}...")
        
        try:
            # 翻译标题
            if article.get('title'):
                translated_title = translator.translate_text(article['title'])
                if translated_title != article['title']:
                    article['translated_title'] = translated_title
                    print(f"  ✅ 标题翻译: {translated_title}")
            
            # 翻译摘要
            if article.get('summary'):
                translated_summary = translator.translate_text(article['summary'])
                if translated_summary != article['summary']:
                    article['translated_summary'] = translated_summary
                    print(f"  ✅ 摘要翻译完成")
            
            # 生成AI点评
            commentary = commentator.generate_commentary(
                article.get('translated_title', article.get('title', '')),
                article.get('translated_summary', article.get('summary', '')),
                article.get('category', 'AI科技')
            )
            if commentary:
                article['ai_commentary'] = commentary
                print(f"  ✅ AI点评: {commentary}")
            
            enhanced_articles.append(article)
            
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            enhanced_articles.append(article)
        
        time.sleep(1)  # 避免API调用过快
    
    # 保留其他未处理的文章
    enhanced_articles.extend(articles[10:])
    
    # 更新数据
    news_data['articles'] = enhanced_articles
    news_data['translated_count'] = len([a for a in enhanced_articles if a.get('translated_title')])
    news_data['commentary_count'] = len([a for a in enhanced_articles if a.get('ai_commentary')])
    news_data['last_updated'] = datetime.now().isoformat()
    
    # 保存增强后的数据
    with open('docs/enhanced_news_data.json', 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n🎉 文章增强完成!")
    print(f"📰 总文章数: {len(enhanced_articles)}")
    print(f"🌐 翻译文章: {news_data['translated_count']}")
    print(f"🤖 AI点评: {news_data['commentary_count']}")
    
    return True

def main():
    """主函数"""
    print("🚀 翻译和AI点评功能测试程序")
    print("=" * 60)
    
    # 1. 基础功能测试
    success = test_translation_and_commentary()
    if not success:
        return False
    
    # 2. 增强现有文章
    success = enhance_existing_articles()
    if not success:
        return False
    
    print("\n🎉 所有测试完成!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)