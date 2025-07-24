#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
弹性翻译管理器使用示例
演示多级降级策略和错误处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translation.services.resilient_translation_manager import ResilientTranslationManager


def main():
    """演示弹性翻译管理器的使用"""
    print("=== 弹性翻译管理器演示 ===\n")
    
    # 创建弹性翻译管理器（没有外部API配置，将直接使用规则翻译器）
    config = {
        'max_retries': 3,
        'retry_delay': 1.0,
        'exponential_backoff': True
    }
    
    manager = ResilientTranslationManager(config)
    
    # 测试新闻标题翻译
    test_texts = [
        "OpenAI announced ChatGPT new features with advanced AI capabilities",
        "Google released breakthrough machine learning technology for developers",
        "Microsoft developed innovative cloud computing platform with AI integration",
        "Tesla launched new electric vehicle model with autonomous driving features",
        "Apple announced latest iPhone with enhanced artificial intelligence"
    ]
    
    print("新闻翻译降级策略测试:")
    print("-" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n第{i}条新闻:")
        print(f"原文: {text}")
        
        # 使用降级策略翻译
        result = manager.translate_with_fallback(text)
        
        print(f"译文: {result['result'].translated_text}")
        print(f"使用服务: {result['service_used']}")
        print(f"降级级别: {result['fallback_level']}")
        print(f"成功: {'是' if result['success'] else '否'}")
        
        if 'warning' in result:
            print(f"警告: {result['warning']}")
        
        if 'error' in result:
            print(f"错误: {result['error']}")
    
    print("\n" + "=" * 60)
    
    # 显示翻译统计信息
    print("\n翻译统计信息:")
    print("-" * 30)
    stats = manager.get_translation_statistics()
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功翻译: {stats['successful_translations']}")
    print(f"失败翻译: {stats['failed_translations']}")
    print(f"成功率: {stats['success_rate']:.1f}%")
    print(f"使用降级: {stats['fallback_used']}")
    print(f"规则翻译器使用: {stats['rule_translator_used']}")
    print(f"平均响应时间: {stats['average_response_time']:.3f}秒")
    
    # 显示服务使用统计
    if stats['service_usage']:
        print("\n服务使用统计:")
        for service_name, service_stats in stats['service_usage'].items():
            print(f"  {service_name}:")
            print(f"    使用次数: {service_stats['count']}")
            print(f"    成功次数: {service_stats['success_count']}")
            print(f"    成功率: {service_stats.get('success_rate', 0):.1f}%")
            print(f"    平均响应时间: {service_stats.get('average_response_time', 0):.3f}秒")
    
    print("\n" + "=" * 60)
    
    # 显示降级链状态
    print("\n降级链状态:")
    print("-" * 30)
    chain_status = manager.get_fallback_chain_status()
    for status in chain_status:
        print(f"优先级{status['priority']}: {status['service_name']} ({status['type']}) - {status['status']}")
    
    print("\n" + "=" * 60)
    
    # 测试降级链
    print("\n测试降级链:")
    print("-" * 30)
    test_result = manager.test_fallback_chain("Hello AI world")
    print(f"测试文本: {test_result['test_text']}")
    print(f"可用降级级别: {test_result['available_fallback_levels']}")
    
    for result in test_result['results']:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {result['service_name']}: {result.get('translated_text', 'N/A')} "
              f"({result['response_time']:.3f}s)")
        if result.get('error'):
            print(f"    错误: {result['error']}")
    
    print("\n" + "=" * 60)
    
    # 显示服务健康摘要
    print("\n服务健康摘要:")
    print("-" * 30)
    health_summary = manager.get_service_health_summary()
    print(f"可用服务: {health_summary['available_services']}")
    print(f"规则翻译器可用: {'是' if health_summary['rule_translator_available'] else '否'}")
    print(f"总服务数: {health_summary['total_services']}")
    
    # 关闭管理器
    manager.shutdown()
    
    print("\n=== 演示完成 ===")
    print("\n关键特性:")
    print("✓ 多级降级策略 (外部API → 规则翻译器 → 原文)")
    print("✓ 自动重试机制 (指数退避)")
    print("✓ 错误处理和恢复")
    print("✓ 翻译统计和监控")
    print("✓ 服务健康检查")
    print("✓ 用户友好的错误提示")


if __name__ == "__main__":
    main()