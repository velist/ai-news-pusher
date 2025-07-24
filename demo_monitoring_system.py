#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译监控系统演示脚本
展示监控系统的核心功能和使用方法
"""

import sys
import os
import time
import random
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.getcwd())

from translation.monitoring.translation_monitor import (
    get_monitor, TranslationMetrics, record_translation_metrics
)
from translation.monitoring.cost_analyzer import TranslationCostAnalyzer
from translation.monitoring.report_generator import TranslationReportGenerator

def simulate_translation_activity():
    """模拟翻译活动"""
    print("🔄 模拟翻译活动...")
    
    services = [
        {'name': 'siliconflow', 'success_rate': 0.95, 'avg_time': 1.5, 'cost_factor': 0.001},
        {'name': 'baidu', 'success_rate': 0.88, 'avg_time': 2.2, 'cost_factor': 0.012},
        {'name': 'tencent', 'success_rate': 0.92, 'avg_time': 1.8, 'cost_factor': 0.058},
        {'name': 'google', 'success_rate': 0.97, 'avg_time': 2.8, 'cost_factor': 0.145}
    ]
    
    # 模拟过去24小时的翻译活动
    for hour in range(24):
        timestamp = datetime.now() - timedelta(hours=23-hour)
        
        # 每小时的请求数量（模拟业务高峰）
        if 9 <= hour <= 18:  # 工作时间
            requests_per_hour = random.randint(20, 50)
        else:  # 非工作时间
            requests_per_hour = random.randint(5, 15)
        
        for _ in range(requests_per_hour):
            service = random.choice(services)
            
            # 模拟翻译成功/失败
            success = random.random() < service['success_rate']
            
            # 模拟响应时间（有一定随机性）
            response_time = service['avg_time'] * (0.8 + random.random() * 0.4)
            
            # 模拟输入输出长度
            input_length = random.randint(50, 500)
            output_length = int(input_length * (0.7 + random.random() * 0.6))
            
            # 模拟置信度
            confidence = random.uniform(0.85, 0.98) if success else 0.0
            
            # 计算成本
            cost = (input_length + output_length) / 1000 * service['cost_factor']
            
            # 记录指标
            metrics = TranslationMetrics(
                timestamp=timestamp.isoformat(),
                service_name=service['name'],
                operation_type="translate_text",
                success=success,
                response_time=response_time,
                input_length=input_length,
                output_length=output_length,
                confidence_score=confidence,
                error_message=None if success else "API Error",
                cost_estimate=cost
            )
            
            monitor = get_monitor()
            monitor.record_translation(metrics)
    
    print(f"✅ 已模拟 24 小时的翻译活动")

def show_monitoring_dashboard():
    """显示监控仪表板数据"""
    print("\n📊 翻译服务监控仪表板")
    print("=" * 60)
    
    monitor = get_monitor()
    
    # 显示服务健康状态
    print("\n🚀 服务健康状态:")
    service_names = list(monitor.service_stats.keys())
    
    if not service_names:
        print("   暂无服务数据")
    else:
        for service_name in service_names:
            health = monitor.get_service_health(service_name)
            status_icon = "✅" if health.is_healthy else "❌"
            print(f"   {status_icon} {service_name}:")
            print(f"      成功率: {health.success_rate:.1%}")
            print(f"      响应时间: {health.avg_response_time:.2f}秒")
            print(f"      总请求: {health.total_requests}")
            print(f"      错误数: {health.error_count}")
            if health.last_error:
                print(f"      最近错误: {health.last_error}")
    
    # 显示今日统计
    print("\n📈 今日统计:")
    today = datetime.now().strftime('%Y-%m-%d')
    daily_stats = monitor.get_daily_statistics(today)
    overall = daily_stats.get('overall', {})
    
    print(f"   总请求数: {overall.get('total_requests', 0)}")
    print(f"   成功率: {overall.get('success_rate', 0):.1%}")
    print(f"   平均响应时间: {overall.get('avg_response_time', 0):.2f}秒")
    print(f"   总成本: ¥{overall.get('total_cost', 0):.2f}")
    
    # 显示服务分布
    by_service = daily_stats.get('by_service', {})
    if by_service:
        print("\n📊 服务分布:")
        for service, stats in by_service.items():
            print(f"   {service}: {stats.get('total_requests', 0)} 请求, "
                  f"成功率 {stats.get('success_rate', 0):.1%}")
    
    # 显示最近报警
    print("\n🚨 最近报警 (24小时内):")
    recent_alerts = monitor.get_recent_alerts(hours=24)
    
    if not recent_alerts:
        print("   ✅ 无报警信息")
    else:
        for alert in recent_alerts[:5]:  # 显示最近5条
            severity_icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡"
            print(f"   {severity_icon} {alert['service_name']}: {alert['message']}")
            print(f"      时间: {alert['timestamp'][:19]}")

def show_cost_analysis():
    """显示成本分析"""
    print("\n💰 成本分析报告")
    print("=" * 60)
    
    analyzer = TranslationCostAnalyzer()
    
    try:
        # 今日成本分析
        today = datetime.now().strftime('%Y-%m-%d')
        daily_cost = analyzer.analyze_daily_costs(today)
        
        print(f"\n📊 今日成本分析 ({today}):")
        print(f"   总成本: ¥{daily_cost['total_cost']:.2f}")
        
        cost_breakdown = daily_cost.get('cost_breakdown', [])
        if cost_breakdown:
            print(f"   服务成本分布:")
            for service in cost_breakdown:
                print(f"      {service['service_name']}: ¥{service['total_cost']:.2f} "
                      f"({service['cost_percentage']:.1f}%)")
        
        # 优化建议
        suggestions = daily_cost.get('optimization_suggestions', [])
        if suggestions:
            print(f"\n💡 优化建议:")
            for suggestion in suggestions[:3]:
                print(f"   • {suggestion}")
        
        # 服务比较
        print(f"\n🔍 服务性价比比较 (最近7天):")
        comparison = analyzer.compare_service_costs(days=7)
        
        service_comparison = comparison.get('service_comparison', [])
        if service_comparison:
            print(f"   性价比排名:")
            for i, service in enumerate(service_comparison[:3]):
                rank_icon = ["🥇", "🥈", "🥉"][i]
                print(f"   {rank_icon} {service['service_name']}: "
                      f"评分 {service['value_score']:.1f}, "
                      f"单次成本 ¥{service['cost_per_request']:.4f}")
        
        # 成本预测
        cost_report = analyzer.generate_cost_report(days=7)
        print(f"\n📈 成本预测:")
        print(f"   预计月度成本: ¥{cost_report['projected_monthly_cost']:.2f}")
        print(f"   预计年度成本: ¥{cost_report['projected_annual_cost']:.2f}")
        
    except Exception as e:
        print(f"❌ 成本分析失败: {e}")

def generate_sample_reports():
    """生成示例报告"""
    print("\n📊 生成示例报告")
    print("=" * 60)
    
    try:
        generator = TranslationReportGenerator()
        
        # 生成今日报告
        print("📈 生成每日报告...")
        daily_report = generator.generate_daily_report()
        
        summary = daily_report.get('summary', {})
        print(f"   今日总请求: {summary.get('total_requests', 0)}")
        print(f"   成功率: {summary.get('success_rate', 0):.1%}")
        print(f"   总成本: ¥{summary.get('total_cost', 0):.2f}")
        print(f"   状态: {summary.get('status', 'unknown').upper()}")
        
        recommendations = daily_report.get('recommendations', [])
        if recommendations:
            print(f"   优化建议数量: {len(recommendations)}")
        
        # 生成周报告
        print("\n📊 生成周报告...")
        weekly_report = generator.generate_weekly_report()
        
        weekly_summary = weekly_report.get('summary', {})
        print(f"   周总请求: {weekly_summary.get('total_requests', 0)}")
        print(f"   平均成功率: {weekly_summary.get('avg_success_rate', 0):.1%}")
        print(f"   周总成本: ¥{weekly_summary.get('total_cost', 0):.2f}")
        
        trends = weekly_report.get('trends', {})
        if trends:
            print(f"   成功率趋势: {trends.get('success_rate_trend', 'stable')}")
            print(f"   响应时间趋势: {trends.get('response_time_trend', 'stable')}")
        
        print(f"✅ 报告已生成并保存到 translation/monitoring/reports/")
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")

def show_quality_analysis():
    """显示质量分析"""
    print("\n🎯 翻译质量分析")
    print("=" * 60)
    
    monitor = get_monitor()
    
    try:
        # 生成质量报告
        quality_report = monitor.generate_quality_report(days=7)
        
        print(f"📊 质量报告 ({quality_report.get('report_period', '最近7天')}):")
        
        # 质量趋势
        quality_trends = quality_report.get('quality_trends', {})
        if quality_trends:
            print(f"   服务质量趋势:")
            for service, trends in quality_trends.items():
                if trends:
                    avg_quality = sum(t['avg_confidence'] for t in trends) / len(trends)
                    print(f"      {service}: 平均置信度 {avg_quality:.1%}")
        
        # 优化建议
        recommendations = quality_report.get('recommendations', [])
        if recommendations:
            print(f"\n💡 质量改进建议:")
            for rec in recommendations[:3]:
                print(f"   • {rec}")
        else:
            print(f"\n✅ 翻译质量良好，无需特别优化")
        
    except Exception as e:
        print(f"❌ 质量分析失败: {e}")

def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式监控系统演示")
    print("=" * 60)
    print("可用命令:")
    print("  1 - 显示监控仪表板")
    print("  2 - 显示成本分析")
    print("  3 - 生成报告")
    print("  4 - 显示质量分析")
    print("  5 - 重新模拟数据")
    print("  q - 退出")
    
    while True:
        try:
            choice = input("\n请选择操作 (1-5, q): ").strip()
            
            if choice == 'q':
                break
            elif choice == '1':
                show_monitoring_dashboard()
            elif choice == '2':
                show_cost_analysis()
            elif choice == '3':
                generate_sample_reports()
            elif choice == '4':
                show_quality_analysis()
            elif choice == '5':
                simulate_translation_activity()
                print("✅ 数据重新模拟完成")
            else:
                print("无效选择，请输入 1-5 或 q")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"操作失败: {e}")

def main():
    """主演示函数"""
    print("🚀 翻译质量监控和运维体系演示")
    print("=" * 60)
    print("这个演示将展示翻译监控系统的核心功能:")
    print("• 实时监控和报警")
    print("• 成本分析和优化")
    print("• 质量评估和改进建议")
    print("• 自动报告生成")
    print()
    
    # 1. 模拟翻译活动
    simulate_translation_activity()
    
    # 2. 显示监控仪表板
    show_monitoring_dashboard()
    
    # 3. 显示成本分析
    show_cost_analysis()
    
    # 4. 生成示例报告
    generate_sample_reports()
    
    # 5. 显示质量分析
    show_quality_analysis()
    
    # 6. 交互式演示
    print(f"\n🎯 演示完成！")
    print(f"如需进一步探索，可以:")
    print(f"• 运行 'python translation/monitoring/start_monitoring.py' 启动完整监控系统")
    print(f"• 访问 http://127.0.0.1:5000 查看Web仪表板")
    print(f"• 查看 translation/monitoring/reports/ 目录下的生成报告")
    
    # 询问是否进入交互模式
    try:
        choice = input(f"\n是否进入交互式演示模式? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            interactive_demo()
    except KeyboardInterrupt:
        pass
    
    print(f"\n👋 演示结束，感谢使用翻译监控系统！")

if __name__ == "__main__":
    main()