#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速运行测试脚本 - 仅处理少量文章测试翻译和AI点评
"""

import os
import json
import urllib.request
from datetime import datetime
import time

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
        except Exception:
            return False
    return False

class SiliconFlowTranslator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        
    def translate_text(self, text):
        try:
            prompt = f"请将以下英文新闻翻译成中文，只返回翻译结果：{text}"
            
            payload = {
                "model": "Qwen/Qwen2.5-7B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 512
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = json.dumps(payload).encode('utf-8')
            request = urllib.request.Request(self.base_url, data=data, headers=headers)
            
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'choices' in result and result['choices']:
                return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"翻译失败: {e}")
        
        return text

def test_quick_translation():
    """快速翻译测试"""
    print("🚀 快速翻译功能测试")
    print("=" * 40)
    
    load_env_file()
    api_key = os.getenv('SILICONFLOW_API_KEY')
    
    if not api_key:
        print("❌ 缺少API密钥")
        return False
    
    translator = SiliconFlowTranslator(api_key)
    
    # 测试样本
    test_cases = [
        "OpenAI raises $8.3 billion as paid ChatGPT users reach 5 million",
        "Google rolls out Gemini Deep Think AI"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {text}")
        translated = translator.translate_text(text)
        print(f"🌐 翻译: {translated}")
        time.sleep(1)
    
    print("\n✅ 快速测试完成!")
    return True

def update_sample_with_translation():
    """为示例文章添加翻译"""
    print("\n🔄 更新示例文章...")
    
    # 读取现有数据
    try:
        with open('docs/news_data.json', 'r', encoding='utf-8') as f:
            news_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取数据失败: {e}")
        return False
    
    articles = news_data.get('articles', [])
    if not articles:
        print("❌ 没有文章数据")
        return False
    
    # 初始化翻译器
    load_env_file()
    api_key = os.getenv('SILICONFLOW_API_KEY')
    if not api_key:
        print("❌ 缺少API密钥")
        return False
    
    translator = SiliconFlowTranslator(api_key)
    
    # 只处理前3条文章作为示例
    updated_count = 0
    for i, article in enumerate(articles[:3]):
        if article.get('translated_title'):
            continue  # 已经翻译过的跳过
            
        print(f"处理文章 {i+1}: {article.get('title', '')[:50]}...")
        
        # 翻译标题
        translated_title = translator.translate_text(article.get('title', ''))
        if translated_title != article.get('title', ''):
            article['translated_title'] = translated_title
            print(f"  ✅ 标题翻译完成")
            updated_count += 1
        
        time.sleep(1)  # 避免API调用过快
    
    if updated_count > 0:
        # 更新统计信息
        news_data['translated_count'] = len([a for a in articles if a.get('translated_title')])
        news_data['last_updated'] = datetime.now().isoformat()
        
        # 保存更新后的数据
        with open('docs/news_data.json', 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 已翻译 {updated_count} 条文章")
        print(f"📊 总翻译数: {news_data.get('translated_count', 0)}")
    else:
        print("ℹ️ 示例文章已翻译，无需更新")
    
    return True

def main():
    """主函数"""
    print("🚀 快速翻译测试程序")
    print("=" * 50)
    
    # 1. 基础翻译测试
    if not test_quick_translation():
        return False
    
    # 2. 更新示例文章
    if not update_sample_with_translation():
        return False
    
    print("\n🎉 快速测试完成!")
    print("🌐 访问地址: https://velist.github.io/ai-news-pusher/docs/")
    
    return True

if __name__ == "__main__":
    main()