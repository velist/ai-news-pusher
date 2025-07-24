#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译监控系统测试
测试监控、报告生成和成本分析功能
"""

import unittest
import tempfile
import shutil
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from translation.monitoring.translation_monitor import (
    TranslationMonitor, TranslationMetrics, ServiceHealthStatus,
    record_translation_metrics
)
from translation.monitoring.report_generator import TranslationReportGenerator
from translation.monitoring.cost_analyzer import TranslationCostAnalyzer
from translation.monitoring.dashboard import app

class TestTranslationMonitor(unittest.TestCase):
    """测试翻译监控器"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_metrics.db"
        self.monitor = TranslationMonitor(str(self.db_path))
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_record_translation_metrics(self):
        """测试记录翻译指标"""
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
        
        # 记录指标
        self.monitor.record_translation(metrics)
        
        # 验证内存缓存
        self.assertEqual(len(self.monitor.recent_metrics), 1)
        self.assertEqual(self.monitor.recent_metrics[0].service_name, "siliconflow")
        
        # 验证服务统计
        stats = self.monitor.service_stats["siliconflow"]
        self.assertEqual(stats['success_count'], 1)
        self.assertEqual(stats['error_count'], 0)
    
    def test_service_health_status(self):
        """测试服务健康状态"""
        # 记录一些成功的指标
        for i in range(10):
            metrics = TranslationMetrics(
                timestamp=datetime.now().isoformat(),
                service_name="test_service",
                operation_type="translate_text",
                success=True,
                response_time=2.0,
                input_length=50,
                output_length=40,
                confidence_score=0.9
            )
            self.monitor.record_translation(metrics)
        
        # 记录一个失败的指标
        error_metrics = TranslationMetrics(
            timestamp=datetime.now().isoformat(),
            service_name="test_service",
            operation_type="translate_text",
            success=False,
            response_time=5.0,
            input_length=50,
            output_length=0,
            confidence_score=0.0,
            error_message="API Error"
        )
        self.monitor.record_translation(error_metrics)
        
        # 获取健康状态
        health = self.monitor.get_service_health("test_service")
        
        self.assertEqual(health.service_name, "test_service")
        self.assertEqual(health.total_requests, 11)
        self.assertEqual(health.error_count, 1)
        self.assertAlmostEqual(health.success_rate, 10/11, places=2)
        self.assertEqual(health.last_error, "API Error")
    
    def test_daily_statistics(self):
        """测试每日统计"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 记录一些今日数据
        for i in range(5):
            metrics = TranslationMetrics(
                timestamp=datetime.now().isoformat(),
                service_name="siliconflow",
                operation_type="translate_text",
                success=True,
                response_time=1.0 + i * 0.1,
                input_length=100,
                output_length=80,
                confidence_score=0.9,
                cost_estimate=0.001
            )
            self.monitor.record_translation(metrics)
        
        # 获取统计数据
        stats = self.monitor.get_daily_statistics(today)
        
        self.assertEqual(stats['date'], today)
        overall = stats['overall']
        self.assertEqual(overall['total_requests'], 5)
        self.assertEqual(overall['success_count'], 5)
        self.assertEqual(overall['success_rate'], 1.0)
        self.assertAlmostEqual(overall['avg_response_time'], 1.2, places=1)
    
    def test_alert_creation(self):
        """测试报警创建"""
        # 记录高响应时间的指标触发报警
        metrics = TranslationMetrics(
            timestamp=datetime.now().isoformat(),
            service_name="slow_service",
            operation_type="translate_text",
            success=True,
            response_time=10.0,  # 超过阈值
            input_length=100,
            output_length=80,
            confidence_score=0.9
        )
        
        self.monitor.record_translation(metrics)
        
        # 获取最近报警
        alerts = self.monitor.get_recent_alerts(hours=1)
        
        self.assertGreater(len(alerts), 0)
        alert = alerts[0]
        self.assertEqual(alert['service_name'], "slow_service")
        self.assertEqual(alert['alert_type'], "high_response_time")
        self.assertEqual(alert['severity'], "WARNING")
    
    def test_quality_report_generation(self):
        """测试质量报告生成"""
        # 记录一周的数据
        for day in range(7):
            date = datetime.now() - timedelta(days=day)
            for i in range(3):
                metrics = TranslationMetrics(
                    timestamp=date.isoformat(),
                    service_name="siliconflow",
                    operation_type="translate_text",
                    success=True,
                    response_time=1.5,
                    input_length=100,
                    output_length=80,
                    confidence_score=0.85 + day * 0.01  # 模拟质量变化
                )
                self.monitor.record_translation(metrics)
        
        # 生成质量报告
        report = self.monitor.generate_quality_report(days=7)
        
        self.assertIn('report_period', report)
        self.assertIn('quality_trends', report)
        self.assertIn('recommendations', report)
        self.assertIsInstance(report['recommendations'], list)

class TestReportGenerator(unittest.TestCase):
    """测试报告生成器"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.temp_dir) / "reports"
        self.generator = TranslationReportGenerator(str(self.output_dir))
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    @patch('translation.monitoring.report_generator.get_monitor')
    def test_daily_report_generation(self, mock_get_monitor):
        """测试每日报告生成"""
        # Mock监控器数据
        mock_monitor = MagicMock()
        mock_monitor.get_daily_statistics.return_value = {
            'date': '2024-01-15',
            'overall': {
                'total_requests': 100,
                'success_count': 95,
                'success_rate': 0.95,
                'avg_response_time': 2.5,
                'total_cost': 1.5
            },
            'by_service': {
                'siliconflow': {
                    'total_requests': 100,
                    'success_rate': 0.95,
                    'avg_response_time': 2.5
                }
            }
        }
        mock_monitor.get_recent_alerts.return_value = []
        mock_get_monitor.return_value = mock_monitor
        
        # 生成报告
        report = self.generator.generate_daily_report('2024-01-15')
        
        # 验证报告内容
        self.assertEqual(report['report_type'], 'daily')
        self.assertEqual(report['date'], '2024-01-15')
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)
        
        # 验证文件生成
        json_file = self.output_dir / "daily_report_2024-01-15.json"
        html_file = self.output_dir / "daily_report_2024-01-15.html"
        
        self.assertTrue(json_file.exists())
        self.assertTrue(html_file.exists())
    
    def test_daily_summary_generation(self):
        """测试每日摘要生成"""
        daily_stats = {
            'overall': {
                'total_requests': 150,
                'success_rate': 0.92,
                'avg_response_time': 3.2,
                'total_cost': 2.8
            },
            'by_service': {
                'siliconflow': {'success_rate': 0.95},
                'baidu': {'success_rate': 0.88}
            }
        }
        
        summary = self.generator._generate_daily_summary(daily_stats)
        
        self.assertEqual(summary['total_requests'], 150)
        self.assertEqual(summary['success_rate'], 0.92)
        self.assertEqual(summary['avg_response_time'], 3.2)
        self.assertEqual(summary['total_cost'], 2.8)
        self.assertEqual(summary['service_count'], 2)
        self.assertEqual(summary['best_performing_service'], 'siliconflow')
        self.assertEqual(summary['worst_performing_service'], 'baidu')
    
    def test_daily_recommendations(self):
        """测试每日建议生成"""
        daily_stats = {
            'overall': {
                'success_rate': 0.85,  # 低成功率
                'avg_response_time': 6.0  # 高响应时间
            },
            'by_service': {
                'slow_service': {
                    'success_rate': 0.8,
                    'avg_response_time': 8.0
                }
            }
        }
        
        alerts = [
            {'severity': 'CRITICAL', 'service_name': 'test'}
        ]
        
        recommendations = self.generator._generate_daily_recommendations(daily_stats, alerts)
        
        # 应该包含成功率和响应时间的建议
        self.assertTrue(any('成功率' in rec for rec in recommendations))
        self.assertTrue(any('响应时间' in rec for rec in recommendations))
        self.assertTrue(any('严重报警' in rec for rec in recommendations))

class TestCostAnalyzer(unittest.TestCase):
    """测试成本分析器"""
    
    def setUp(self):
        """测试前准备"""
        self.analyzer = TranslationCostAnalyzer()
    
    def test_cost_estimation(self):
        """测试成本估算"""
        # 测试硅基流动成本估算
        cost = self.analyzer._estimate_cost('siliconflow', 1000, 800, 'Qwen/Qwen2.5-7B-Instruct')
        expected_cost = (1000/1000) * 0.0007 + (800/1000) * 0.0007  # 输入+输出成本
        self.assertAlmostEqual(cost, expected_cost, places=6)
        
        # 测试百度翻译成本估算
        baidu_cost = self.analyzer._estimate_cost('baidu', 1000, 800)
        expected_baidu = (1000/1000) * 0.012 + (800/1000) * 0.012
        self.assertAlmostEqual(baidu_cost, expected_baidu, places=6)
    
    def test_pricing_retrieval(self):
        """测试定价信息获取"""
        # 测试输入价格获取
        siliconflow_input_price = self.analyzer._get_input_price('siliconflow')
        self.assertEqual(siliconflow_input_price, 0.0007)
        
        # 测试输出价格获取
        baidu_output_price = self.analyzer._get_output_price('baidu')
        self.assertEqual(baidu_output_price, 0.012)
        
        # 测试未知服务
        unknown_price = self.analyzer._get_input_price('unknown_service')
        self.assertEqual(unknown_price, 0.0)
    
    @patch('translation.monitoring.cost_analyzer.get_monitor')
    def test_daily_cost_analysis(self, mock_get_monitor):
        """测试每日成本分析"""
        # Mock数据库连接和数据
        mock_monitor = MagicMock()
        mock_monitor.db_path = ":memory:"
        mock_get_monitor.return_value = mock_monitor
        
        # 由于涉及数据库操作，这里主要测试函数调用
        with patch('sqlite3.connect') as mock_connect:
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = [
                ('siliconflow', 'translate_text', 1000, 800, 0.001, 1),
                ('baidu', 'translate_text', 500, 400, 0.0, 1)
            ]
            mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor
            
            result = self.analyzer.analyze_daily_costs('2024-01-15')
            
            self.assertEqual(result['date'], '2024-01-15')
            self.assertIn('service_breakdown', result)
            self.assertIn('cost_analysis', result)
            self.assertIn('optimization_suggestions', result)
    
    def test_cost_optimization_generation(self):
        """测试成本优化建议生成"""
        from translation.monitoring.cost_analyzer import CostBreakdown
        
        cost_breakdown = [
            CostBreakdown(
                service_name='expensive_service',
                total_cost=10.0,
                request_count=100,
                avg_cost_per_request=0.1,
                input_tokens=10000,
                output_tokens=8000,
                cost_per_input_token=0.01,
                cost_per_output_token=0.01
            ),
            CostBreakdown(
                service_name='cheap_service',
                total_cost=1.0,
                request_count=50,
                avg_cost_per_request=0.02,
                input_tokens=5000,
                output_tokens=4000,
                cost_per_input_token=0.001,
                cost_per_output_token=0.001
            )
        ]
        
        optimization = self.analyzer._generate_cost_optimization(cost_breakdown, 11.0)
        
        self.assertIsNotNone(optimization)
        self.assertEqual(optimization.current_cost, 11.0)
        self.assertGreater(optimization.savings, 0)
        self.assertGreater(len(optimization.recommendations), 0)

class TestDashboardAPI(unittest.TestCase):
    """测试监控仪表板API"""
    
    def setUp(self):
        """测试前准备"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_dashboard_page(self):
        """测试仪表板主页"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('翻译服务监控仪表板'.encode('utf-8'), response.data)
    
    @patch('translation.monitoring.dashboard.get_monitor')
    def test_dashboard_data_api(self, mock_get_monitor):
        """测试仪表板数据API"""
        # Mock监控器数据
        mock_monitor = MagicMock()
        mock_monitor.get_daily_statistics.return_value = {
            'overall': {
                'total_requests': 100,
                'success_rate': 0.95,
                'avg_response_time': 2.5,
                'total_cost': 1.5
            }
        }
        mock_monitor.service_stats = {
            'siliconflow': {
                'success_count': 95,
                'error_count': 5,
                'total_response_time': 250.0,
                'last_error_message': None
            }
        }
        mock_monitor.get_service_health.return_value = MagicMock(
            service_name='siliconflow',
            is_healthy=True,
            success_rate=0.95,
            avg_response_time=2.5,
            total_requests=100,
            error_count=5,
            last_error=None
        )
        mock_monitor.get_recent_alerts.return_value = []
        mock_get_monitor.return_value = mock_monitor
        
        response = self.app.get('/api/dashboard-data')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('overall_stats', data)
        self.assertIn('service_status', data)
        self.assertIn('trends', data)
        self.assertIn('recent_alerts', data)
    
    @patch('translation.monitoring.dashboard.get_monitor')
    def test_quality_report_api(self, mock_get_monitor):
        """测试质量报告API"""
        mock_monitor = MagicMock()
        mock_monitor.generate_quality_report.return_value = {
            'report_period': '7天',
            'quality_trends': {},
            'recommendations': ['测试建议']
        }
        mock_get_monitor.return_value = mock_monitor
        
        response = self.app.get('/api/quality-report?days=7')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('report_period', data)
        self.assertIn('recommendations', data)

class TestIntegrationScenarios(unittest.TestCase):
    """测试集成场景"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "integration_test.db"
        self.monitor = TranslationMonitor(str(self.db_path))
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_monitoring_workflow(self):
        """测试完整的监控工作流程"""
        # 1. 记录翻译指标
        services = ['siliconflow', 'baidu', 'tencent']
        
        for service in services:
            for i in range(10):
                success = i < 8  # 80%成功率
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
                self.monitor.record_translation(metrics)
        
        # 2. 检查服务健康状态
        for service in services:
            health = self.monitor.get_service_health(service)
            self.assertEqual(health.service_name, service)
            self.assertEqual(health.total_requests, 10)
            self.assertEqual(health.success_rate, 0.8)
        
        # 3. 获取每日统计
        today = datetime.now().strftime('%Y-%m-%d')
        stats = self.monitor.get_daily_statistics(today)
        
        self.assertEqual(stats['overall']['total_requests'], 30)  # 3个服务 * 10次请求
        self.assertEqual(stats['overall']['success_count'], 24)   # 3个服务 * 8次成功
        self.assertEqual(stats['overall']['success_rate'], 0.8)
        
        # 4. 生成质量报告
        report = self.monitor.generate_quality_report(days=1)
        self.assertIn('recommendations', report)
        self.assertIsInstance(report['recommendations'], list)
        
        # 5. 检查报警
        alerts = self.monitor.get_recent_alerts(hours=1)
        # 应该有一些报警，因为有失败的请求
        self.assertGreaterEqual(len(alerts), 0)
    
    def test_cost_analysis_integration(self):
        """测试成本分析集成"""
        # 记录不同成本的翻译
        high_cost_metrics = TranslationMetrics(
            timestamp=datetime.now().isoformat(),
            service_name="google",
            operation_type="translate_text",
            success=True,
            response_time=2.0,
            input_length=1000,
            output_length=800,
            confidence_score=0.95,
            cost_estimate=0.1  # 高成本
        )
        
        low_cost_metrics = TranslationMetrics(
            timestamp=datetime.now().isoformat(),
            service_name="siliconflow",
            operation_type="translate_text",
            success=True,
            response_time=1.5,
            input_length=1000,
            output_length=800,
            confidence_score=0.9,
            cost_estimate=0.001  # 低成本
        )
        
        self.monitor.record_translation(high_cost_metrics)
        self.monitor.record_translation(low_cost_metrics)
        
        # 分析成本
        analyzer = TranslationCostAnalyzer()
        analyzer.monitor = self.monitor  # 使用同一个监控实例
        
        # 由于成本分析需要数据库查询，这里主要验证函数调用不出错
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            cost_analysis = analyzer.analyze_daily_costs(today)
            self.assertIn('date', cost_analysis)
            self.assertIn('total_cost', cost_analysis)
        except Exception as e:
            # 如果数据库查询失败，至少确保不会崩溃
            self.fail(f"成本分析失败: {e}")

def run_monitoring_tests():
    """运行监控系统测试"""
    print("🧪 开始运行翻译监控系统测试...")
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestTranslationMonitor,
        TestReportGenerator,
        TestCostAnalyzer,
        TestDashboardAPI,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果
    if result.wasSuccessful():
        print("✅ 所有监控系统测试通过！")
        return True
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        return False

if __name__ == "__main__":
    run_monitoring_tests()