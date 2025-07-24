#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试带缓存的翻译服务
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translation.services.cached_translation_service import CachedTranslationService


def test_cached_translation_service():
    """测试带缓存的翻译服务"""
    
    print("=== 带缓存的翻译服务测试 ===")
    
    # 创建临时目录用于缓存
    temp_dir = tempfile.mkdtemp()
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    try:
        # 配置信息
        translation_config = {
            'siliconflow': {
                'api_key': 'sk-test-key'  # 测试用的API密钥
            }
        }
        
        cache_config = {
            'memory_cache_size': 100,
            'file_cache_dir': temp_dir,
            'db_cache_path': temp_db.name,
            'cache_ttl_days': 7,
            'auto_cleanup': False
        }
        
        # 初始化服务
        service = CachedTranslationService(translation_config, cache_config)
        
        print(f"翻译服务已初始化")
        print(f"缓存目录: {temp_dir}")
        print(f"数据库路径: {temp_db.name}")
        
        # 测试文本
        test_texts = [
            "OpenAI has released ChatGPT, a revolutionary AI chatbot.",
            "Apple reported record revenue in the latest quarter.",
            "Tesla's autonomous driving technology continues to advance."
        ]
        
        print("\n=== 第一次翻译（缓存未命中）===")
        
        first_round_results = []
        for i, text in enumerate(test_texts, 1):
            print(f"\n--- 测试 {i} ---")
            print(f"原文: {text}")
            
            result = service.translate(text, use_quality_optimization=True)
            first_round_results.append(result)
            
            if result['success']:
                translation_result = result['translation_result']
                print(f"翻译: {translation_result.translated_text}")
                print(f"服务: {translation_result.service_name}")
                print(f"质量评分: {result.get('quality_score', 'N/A'):.3f}")
                print(f"来源: {result['source']}")
                print(f"响应时间: {result['response_time_ms']:.1f}ms")
                
                if 'cache_info' in result:
                    print(f"缓存状态: {'已缓存' if result['cache_info'].get('cached', False) else '未缓存'}")
            else:
                print(f"翻译失败: {result.get('error', '未知错误')}")
        
        print("\n=== 第二次翻译（缓存命中）===")
        
        second_round_results = []
        for i, text in enumerate(test_texts, 1):
            print(f"\n--- 测试 {i} ---")
            print(f"原文: {text}")
            
            result = service.translate(text)
            second_round_results.append(result)
            
            if result['success']:
                translation_result = result['translation_result']
                print(f"翻译: {translation_result.translated_text}")
                print(f"来源: {result['source']}")
                print(f"响应时间: {result['response_time_ms']:.1f}ms")
                
                if 'cache_info' in result:
                    cache_info = result['cache_info']
                    if 'usage_count' in cache_info:
                        print(f"缓存使用次数: {cache_info['usage_count']}")
                        print(f"缓存创建时间: {cache_info['created_at']}")
            else:
                print(f"翻译失败: {result.get('error', '未知错误')}")
        
        # 验证缓存效果
        print("\n=== 缓存效果验证 ===")
        cache_hits = sum(1 for result in second_round_results if result.get('source') == 'cache')
        print(f"第二轮缓存命中数: {cache_hits}/{len(test_texts)}")
        
        # 比较响应时间
        first_avg_time = sum(r['response_time_ms'] for r in first_round_results if r['success']) / len([r for r in first_round_results if r['success']])
        second_avg_time = sum(r['response_time_ms'] for r in second_round_results if r['success']) / len([r for r in second_round_results if r['success']])
        
        print(f"第一轮平均响应时间: {first_avg_time:.1f}ms")
        print(f"第二轮平均响应时间: {second_avg_time:.1f}ms")
        print(f"性能提升: {((first_avg_time - second_avg_time) / first_avg_time * 100):.1f}%")
        
        # 测试批量翻译
        print("\n=== 批量翻译测试 ===")
        batch_texts = [
            "Artificial intelligence is transforming industries.",
            "Machine learning algorithms improve over time.",
            "Deep learning models require large datasets."
        ]
        
        batch_results = service.batch_translate(batch_texts)
        print(f"批量翻译完成，处理了 {len(batch_results)} 个文本")
        
        for i, result in enumerate(batch_results, 1):
            if result['success']:
                print(f"{i}. {result['translation_result'].translated_text} (来源: {result['source']})")
        
        # 获取性能统计
        print("\n=== 性能统计 ===")
        stats = service.get_performance_statistics()
        
        service_perf = stats['service_performance']
        cache_perf = stats['cache_performance']
        overall_metrics = stats['overall_metrics']
        
        print(f"总请求数: {service_perf['total_requests']}")
        print(f"缓存命中数: {service_perf['cache_hits']}")
        print(f"缓存未命中数: {service_perf['cache_misses']}")
        print(f"缓存命中率: {overall_metrics['cache_hit_rate']:.2%}")
        print(f"平均响应时间: {overall_metrics['average_response_time_ms']:.1f}ms")
        
        print(f"\n缓存统计:")
        print(f"内存缓存大小: {cache_perf['memory_cache_size']}")
        print(f"内存缓存命中率: {cache_perf['memory_hit_rate']:.2%}")
        print(f"数据库缓存项数: {cache_perf['database_stats']['valid_items']}")
        
        # 测试性能优化
        print("\n=== 性能优化测试 ===")
        optimization_result = service.optimize_performance()
        
        print("优化建议:")
        for recommendation in optimization_result['recommendations']:
            print(f"- {recommendation}")
        
        if not optimization_result['recommendations']:
            print("- 当前性能良好，无需特别优化")
        
        # 测试健康检查
        print("\n=== 健康检查 ===")
        health = service.health_check()
        print(f"服务状态: {health['status']}")
        print(f"可用服务数: {health.get('service_count', 0)}")
        print(f"缓存命中率: {health.get('cache_hit_rate', 0):.2%}")
        print(f"测试翻译成功: {health.get('test_translation_success', False)}")
        
        # 测试用户反馈
        print("\n=== 用户反馈测试 ===")
        if first_round_results and first_round_results[0]['success']:
            feedback_result = service.submit_feedback(
                request_id=first_round_results[0]['request_id'],
                original_text=test_texts[0],
                translated_text=first_round_results[0]['translation_result'].translated_text,
                service_name=first_round_results[0]['translation_result'].service_name,
                feedback_type='quality_rating',
                rating=4.5,
                comments="翻译质量很好，术语准确"
            )
            print(f"反馈提交{'成功' if feedback_result else '失败'}")
        
        # 测试强制刷新缓存
        print("\n=== 强制刷新缓存测试 ===")
        refresh_result = service.translate(test_texts[0], force_refresh=True)
        if refresh_result['success']:
            print(f"强制刷新翻译: {refresh_result['translation_result'].translated_text}")
            print(f"来源: {refresh_result['source']}")
        
        print("\n=== 测试完成 ===")
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir, ignore_errors=True)
        if os.path.exists(temp_db.name):
            os.unlink(temp_db.name)


if __name__ == "__main__":
    test_cached_translation_service()