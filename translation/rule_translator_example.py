#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则翻译器使用示例
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translation.services.rule_based_translator import RuleBasedTranslator


def main():
    """演示规则翻译器的使用"""
    print("=== 规则翻译器演示 ===\n")
    
    # 创建规则翻译器实例
    translator = RuleBasedTranslator()
    
    # 测试新闻标题翻译
    test_texts = [
        "OpenAI announced ChatGPT new features",
        "Google released advanced AI technology",
        "Microsoft developed innovative machine learning platform",
        "Tesla launched new electric vehicle model",
        "Apple announced latest iPhone with AI capabilities"
    ]
    
    print("新闻标题翻译测试:")
    print("-" * 50)
    
    for text in test_texts:
        result = translator.translate_text(text)
        print(f"原文: {result.original_text}")
        print(f"译文: {result.translated_text}")
        print(f"置信度: {result.confidence_score:.2f}")
        print(f"服务: {result.service_name}")
        print()
    
    # 测试批量翻译
    print("批量翻译测试:")
    print("-" * 50)
    
    batch_results = translator.translate_batch(test_texts[:3])
    for i, result in enumerate(batch_results, 1):
        print(f"第{i}条: {result.translated_text} (置信度: {result.confidence_score:.2f})")
    
    print()
    
    # 测试添加自定义术语
    print("自定义术语测试:")
    print("-" * 50)
    
    translator.add_custom_term("kiro", "Kiro助手", is_tech_term=True)
    custom_text = "Kiro is an advanced AI assistant"
    custom_result = translator.translate_text(custom_text)
    print(f"原文: {custom_result.original_text}")
    print(f"译文: {custom_result.translated_text}")
    print(f"置信度: {custom_result.confidence_score:.2f}")
    
    print()
    
    # 测试服务状态
    print("服务状态:")
    print("-" * 50)
    print(f"服务名称: {translator.get_service_name()}")
    print(f"服务状态: {translator.get_service_status().value}")
    
    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    main()