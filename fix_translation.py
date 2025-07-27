#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复翻译问题 - 使用多翻译服务重新翻译新闻
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from translation.services.siliconflow_translator import SiliconFlowTranslator
except ImportError as e:
    print(f"⚠️ 无法导入SiliconFlowTranslator: {e}")
    SiliconFlowTranslator = None

try:
    from translation.services.baidu_translator import BaiduTranslator
except ImportError as e:
    print(f"⚠️ 无法导入BaiduTranslator: {e}")
    BaiduTranslator = None

try:
    from translation.services.tencent_translator import TencentTranslator
except ImportError as e:
    print(f"⚠️ 无法导入TencentTranslator: {e}")
    TencentTranslator = None

class TranslationFixer:
    def __init__(self):
        self.translators = []
        self._init_translators()
        
    def _init_translators(self):
        """初始化多个翻译服务"""
        print("🔧 开始初始化翻译服务...")
        
        # 1. 尝试初始化硅基流动翻译器
        if SiliconFlowTranslator:
            try:
                siliconflow_key = os.getenv('SILICONFLOW_API_KEY')
                if siliconflow_key:
                    translator = SiliconFlowTranslator(
                        api_key=siliconflow_key,
                        model="Qwen/Qwen2.5-7B-Instruct"
                    )
                    self.translators.append(('SiliconFlow', translator))
                    print("✅ 硅基流动翻译器初始化成功")
                else:
                    print("⚠️ 缺少SILICONFLOW_API_KEY")
            except Exception as e:
                print(f"⚠️ 硅基流动翻译器初始化失败: {e}")
        
        # 2. 尝试初始化百度翻译器
        if BaiduTranslator:
            try:
                baidu_app_id = os.getenv('BAIDU_APP_ID')
                baidu_secret = os.getenv('BAIDU_SECRET_KEY')
                if baidu_app_id and baidu_secret:
                    translator = BaiduTranslator(app_id=baidu_app_id, secret_key=baidu_secret)
                    self.translators.append(('Baidu', translator))
                    print("✅ 百度翻译器初始化成功")
                else:
                    print("⚠️ 缺少百度翻译API配置")
            except Exception as e:
                print(f"⚠️ 百度翻译器初始化失败: {e}")
        
        # 3. 尝试初始化腾讯翻译器
        if TencentTranslator:
            try:
                tencent_id = os.getenv('TENCENT_SECRET_ID')
                tencent_key = os.getenv('TENCENT_SECRET_KEY')
                if tencent_id and tencent_key:
                    translator = TencentTranslator(secret_id=tencent_id, secret_key=tencent_key)
                    self.translators.append(('Tencent', translator))
                    print("✅ 腾讯翻译器初始化成功")
                else:
                    print("⚠️ 缺少腾讯翻译API配置")
            except Exception as e:
                print(f"⚠️ 腾讯翻译器初始化失败: {e}")
        
        print(f"📊 总共初始化了 {len(self.translators)} 个翻译服务")
    
    def translate_text_with_fallback(self, text, source_lang='en', target_lang='zh'):
        """使用降级策略翻译文本"""
        if not text or not text.strip():
            return None
        
        for service_name, translator in self.translators:
            try:
                print(f"🔄 尝试使用 {service_name} 翻译...")
                result = translator.translate_text(text, source_lang, target_lang)
                
                if result and not result.error_message and result.translated_text:
                    print(f"✅ {service_name} 翻译成功")
                    return {
                        'translated_text': result.translated_text,
                        'confidence_score': result.confidence_score,
                        'service_name': service_name,
                        'translation_time': datetime.now().isoformat()
                    }
                else:
                    print(f"⚠️ {service_name} 翻译失败: {result.error_message if result else '无结果'}")
                    
            except Exception as e:
                print(f"❌ {service_name} 翻译异常: {e}")
                continue
        
        print("❌ 所有翻译服务都失败了")
        return None
    
    def fix_news_translation(self):
        """修复新闻翻译"""
        print("🚀 开始修复新闻翻译...")
        
        # 读取现有新闻数据
        try:
            with open('docs/enhanced_news_data.json', 'r', encoding='utf-8') as f:
                articles = json.load(f)
            print(f"📖 读取到 {len(articles)} 条新闻")
        except Exception as e:
            print(f"❌ 读取新闻数据失败: {e}")
            return False
        
        # 统计需要翻译的新闻
        need_translation = []
        for article in articles:
            ai_translation = article.get('ai_translation', {})
            if not ai_translation.get('translated_title'):
                need_translation.append(article)
        
        print(f"📊 需要翻译的新闻: {len(need_translation)} 条")
        
        if not need_translation:
            print("✅ 所有新闻都已翻译完成")
            return True
        
        # 开始翻译
        success_count = 0
        for i, article in enumerate(need_translation[:10], 1):  # 限制翻译前10条
            print(f"\n📰 翻译第 {i}/{min(10, len(need_translation))} 条新闻...")
            
            title = article.get('title', '')
            description = article.get('description', '')
            
            # 翻译标题
            title_translation = None
            if title:
                print(f"📝 翻译标题: {title[:50]}...")
                title_translation = self.translate_text_with_fallback(title)
            
            # 翻译描述
            desc_translation = None
            if description:
                print(f"📄 翻译描述: {description[:50]}...")
                desc_translation = self.translate_text_with_fallback(description)
            
            # 更新文章翻译信息
            if title_translation or desc_translation:
                article['ai_translation'] = {
                    'translated_title': title_translation['translated_text'] if title_translation else '',
                    'translated_description': desc_translation['translated_text'] if desc_translation else '',
                    'translation_confidence': {
                        'title': title_translation['confidence_score'] if title_translation else 0.0,
                        'description': desc_translation['confidence_score'] if desc_translation else 0.0
                    },
                    'translation_service': title_translation['service_name'] if title_translation else 'none',
                    'translation_time': datetime.now().isoformat(),
                    'original_title': title,
                    'original_description': description
                }
                success_count += 1
                print(f"✅ 翻译完成")
            else:
                print(f"❌ 翻译失败")
        
        # 保存更新后的数据
        try:
            with open('docs/enhanced_news_data.json', 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            print(f"\n💾 新闻数据已保存")
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False
        
        print(f"\n🎉 翻译修复完成!")
        print(f"📊 成功翻译: {success_count} 条新闻")
        
        return True

def main():
    print("🚀 启动翻译修复程序...")
    try:
        fixer = TranslationFixer()
        if fixer.translators:
            fixer.fix_news_translation()
        else:
            print("❌ 没有可用的翻译服务")
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()