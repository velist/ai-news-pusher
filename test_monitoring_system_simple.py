#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译监控系统简化测试
验证监控系统的核心功能
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.getcwd())

def test_translation_monitor():
    """测试翻译监控器基本功能"""
    print("🧪 测试翻译监控器...")
    
    try:
        from translation.monitoring.translation_monitor import (
            TranslationMonitor, TranslationMetrics, record_translation_metrics
        )
        
        # 创建临时数据库
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "test_metrics.db"
        
        # 初始化监控器
        monitor = TranslationMonitor(str(db_path))
        
        # 测试记录指标
        metrics = TranslationMetrics(
            timestamp=datetime.now().isoformat(),
            service_name="siliconflow",
            operation_type="translate_text",
            success=True,
            response_time=1.5,
            input_length=100,
            output_length=80,
            confidence_score=0.95,
            cost_estimate=0.001
        )
        
        monitor.record_translation(metrics)
        
        # 验证数据记录
        assert len(monitor.recent_metrics) == 1
        assert monitor.recent_metrics[0].service_name == "siliconflow"
        
        # 测试服务健康状态
        health = monitor.get_service_health("siliconflow")
        assert health.service_name == "siliconflow"
        assert health.total_requests == 1
        assert health.success_rate == 1.0
        
        # 测试每日统计
        today = datetime.now().strftime('%Y-%m-%d')
        stats = monitor.get_daily_statistics(today)
        assert stats['date'] == today
        
        # 清理
        shutil.rmtree(temp_dir)
        
        print("✅ 翻译监控器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 翻译监控器测试失败: {e}")
        return False

def test_cost_analyzer():
    """测试成本分析器"""
    print("🧪 测试成本分析器...")
    
    try:
        from translation.monitoring.cost_analyzer import TranslationCostAnalyzer
        
        analyzer = TranslationCostAnalyzer()
        
        # 测试成本估算
        cost = analyzer._estimate_cost('siliconflow', 1000, 800, 'Qwen/Qwen2.5-7B-Instruct')
        expected_cost = (1000/1000) * 0.0007 + (800/1000) * 0.0007
        assert abs(cost - expected_cost) < 0.000001
        
        # 测试定价获取
        input_price = analyzer._get_input_price('siliconflow')
        assert input_price == 0.0007
        
        output_price = analyzer._get_output_price('baidu')
        assert output_price == 0.012
        
        print("✅ 成本分析器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 成本分析器测试失败: {e}")
        return False

def test_report_generator():
    """测试报告生成器"""
    print("🧪 测试报告生成器...")
    
    try:
        from translation.monitoring.report_generator import TranslationReportGenerator
        
        # 创建临时输出目录
        temp_dir = tempfile.mkdtemp()
        generator = TranslationReportGenerator(temp_dir)
        
        # 测试每日摘要生成
        daily_stats = {
            'overall': {
                'total_requests': 100,
                'success_rate': 0.95,
                'avg_response_time': 2.5,
                'total_cost': 1.5
            },
            'by_service': {
                'siliconflow': {'success_rate': 0.95},
                'baidu': {'success_rate': 0.88}
            }
        }
        
        summary = generator._generate_daily_summary(daily_stats)
        assert summary['total_requests'] == 100
        assert summary['success_rate'] == 0.95
        assert summary['service_count'] == 2
        
        # 测试建议生成
        recommendations = generator._generate_daily_recommendations(daily_stats, [])
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # 清理
        shutil.rmtree(temp_dir)
        
        print("✅ 报告生成器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 报告生成器测试失败: {e}")
        return False

def test_dashboard_basic():
    """测试仪表板基本功能"""
    print("🧪 测试仪表板基本功能...")
    
    try:
        from translation.monitoring.dashboard import app
        
        # 创建测试客户端
        client = app.test_client()
        client.testing = True
        
        # 测试主页
        response = client.get('/')
        assert response.status_code == 200
        assert '翻译服务监控仪表板'.encode('utf-8') in response.data
        
        print("✅ 仪表板基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 仪表板测试失败: {e}")
        return False

def test_integration_scenario():
    """测试集成场景"""
    print("🧪 测试集成场景...")
    
    try:
        from translation.monitoring.translation_monitor import (
            TranslationMonitor, TranslationMetrics
        )
        
        # 创建临时数据库
        temp_dir = tempfile.mkdtemp()
        db_path = Path(temp_dir) / "integration_test.db"
        monitor = TranslationMonitor(str(db_path))
        
        # 模拟多个服务的翻译记录
        services = ['siliconflow', 'baidu', 'tencent']
        
        for service in services:
            for i in range(5):
                success = i < 4  # 80%成功率
                metrics = TranslationMetrics(
                    timestamp=datetime.now().isoformat(),
                    service_name=service,
                    operation_type="translate_text",
                    success=success,
                    response_time=1.0 + i * 0.1,
                    input_length=100 + i * 10,
                    output_length=80 + i * 8,
                    confidence_score=0.9 if success else 0.0,
                    error_message=None if success else "API Error",
                    cost_estimate=0.001 * (1 + i * 0.1)
                )
                monitor.record_translation(metrics)
        
        # 验证数据记录
        assert len(monitor.recent_metrics) == 15  # 3个服务 * 5次请求
        
        # 验证服务健康状态
        for service in services:
            health = monitor.get_service_health(service)
            assert health.service_name == service
            assert health.total_requests == 5
            assert health.success_rate == 0.8
        
        # 验证每日统计
        today = datetime.now().strftime('%Y-%m-%d')
        stats = monitor.get_daily_statistics(today)
        assert stats['overall']['total_requests'] == 15
        assert stats['overall']['success_count'] == 12  # 3个服务 * 4次成功
        
        # 清理
        shutil.rmtree(temp_dir)
        
        print("✅ 集成场景测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 集成场景测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始运行翻译监控系统测试")
    print("=" * 50)
    
    tests = [
        test_translation_monitor,
        test_cost_analyzer,
        test_report_generator,
        test_dashboard_basic,
        test_integration_scenario
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！监控系统功能正常")
        return True
    else:
        print(f"⚠️  有 {total - passed} 个测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)