#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务使用示例
"""

import os
from translation.services.baidu_translator import BaiduTranslator
from translation.services.tencent_translator import TencentTranslator
from translation.services.google_translator import GoogleTranslator
from translation.core.interfaces import ServiceStatus


def demo_translation_services():
    """演示翻译服务的使用"""
    
    print("=== 翻译服务演示 ===\n")
    
    # 示例文本
    test_texts = [
        "Hello, world!",
        "Artificial Intelligence is transforming the world.",
        "OpenAI releases new ChatGPT model with improved capabilities."
    ]
    
    # 演示百度翻译
    print("1. 百度翻译服务演示")
    print("-" * 30)
    try:
        # 注意：需要设置环境变量 BAIDU_TRANSLATE_APP_ID 和 BAIDU_TRANSLATE_SECRET_KEY
        baidu = BaiduTranslator()
        print(f"服务状态: {baidu.get_service_status().value}")
        
        for text in test_texts:
            result = baidu.translate_text(text, "en", "zh")
            if result.error_message:
                print(f"❌ 翻译失败: {result.error_message}")
            else:
                print(f"✅ {text} -> {result.translated_text}")
        
        # 批量翻译演示
        print("\n批量翻译演示:")
        batch_results = baidu.translate_batch(test_texts[:2], "en", "zh")
        for result in batch_results:
            if not result.error_message:
                print(f"✅ {result.original_text} -> {result.translated_text}")
                
    except ValueError as e:
        print(f"⚠️ 百度翻译配置错误: {e}")
    except Exception as e:
        print(f"❌ 百度翻译错误: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 演示腾讯翻译
    print("2. 腾讯翻译服务演示")
    print("-" * 30)
    try:
        # 注意：需要设置环境变量 TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY
        tencent = TencentTranslator()
        print(f"服务状态: {tencent.get_service_status().value}")
        
        for text in test_texts:
            result = tencent.translate_text(text, "en", "zh")
            if result.error_message:
                print(f"❌ 翻译失败: {result.error_message}")
            else:
                print(f"✅ {text} -> {result.translated_text}")
        
        # 健康检查演示
        print("\n健康检查演示:")
        health = tencent.check_health()
        print(f"服务: {health['service']}")
        print(f"状态: {health['status']}")
        print(f"响应时间: {health.get('response_time', 'N/A')}秒")
        
    except ValueError as e:
        print(f"⚠️ 腾讯翻译配置错误: {e}")
    except Exception as e:
        print(f"❌ 腾讯翻译错误: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 演示Google翻译
    print("3. Google翻译服务演示")
    print("-" * 30)
    try:
        # 注意：需要设置环境变量 GOOGLE_TRANSLATE_API_KEY
        google = GoogleTranslator()
        print(f"服务状态: {google.get_service_status().value}")
        
        # 语言检测演示
        detected = google.detect_language("Hello world")
        print(f"语言检测: 'Hello world' -> {detected}")
        
        for text in test_texts:
            result = google.translate_text(text, "en", "zh")
            if result.error_message:
                print(f"❌ 翻译失败: {result.error_message}")
            else:
                print(f"✅ {text} -> {result.translated_text} (置信度: {result.confidence_score:.2f})")
        
        # 获取支持的语言
        print("\n支持的语言 (前5个):")
        languages = google.get_supported_languages()
        for lang in languages[:5]:
            print(f"  {lang.get('language', 'N/A')}: {lang.get('name', 'N/A')}")
            
    except ValueError as e:
        print(f"⚠️ Google翻译配置错误: {e}")
    except Exception as e:
        print(f"❌ Google翻译错误: {e}")


def demo_service_comparison():
    """演示多个翻译服务的比较"""
    
    print("\n" + "="*50)
    print("=== 翻译服务比较演示 ===")
    print("="*50 + "\n")
    
    test_text = "Artificial Intelligence is revolutionizing the technology industry."
    
    services = []
    
    # 尝试初始化各个服务
    try:
        services.append(("百度翻译", BaiduTranslator()))
    except:
        print("⚠️ 百度翻译服务不可用")
    
    try:
        services.append(("腾讯翻译", TencentTranslator()))
    except:
        print("⚠️ 腾讯翻译服务不可用")
    
    try:
        services.append(("Google翻译", GoogleTranslator()))
    except:
        print("⚠️ Google翻译服务不可用")
    
    if not services:
        print("❌ 没有可用的翻译服务，请检查API配置")
        return
    
    print(f"原文: {test_text}\n")
    
    for service_name, service in services:
        try:
            result = service.translate_text(test_text, "en", "zh")
            if result.error_message:
                print(f"{service_name}: ❌ {result.error_message}")
            else:
                print(f"{service_name}: ✅ {result.translated_text}")
                print(f"  置信度: {result.confidence_score:.2f}")
                print(f"  响应时间: {result.timestamp}")
        except Exception as e:
            print(f"{service_name}: ❌ 异常 - {str(e)}")
        print()


if __name__ == "__main__":
    # 设置示例环境变量（实际使用时应该通过系统环境变量设置）
    print("注意：请确保已设置以下环境变量：")
    print("- BAIDU_TRANSLATE_APP_ID 和 BAIDU_TRANSLATE_SECRET_KEY")
    print("- TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY") 
    print("- GOOGLE_TRANSLATE_API_KEY")
    print("\n如果没有设置，相应的服务将显示配置错误。\n")
    
    demo_translation_services()
    demo_service_comparison()