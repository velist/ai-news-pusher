#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译监控系统启动脚本
启动完整的翻译质量监控和运维体系
"""

import os
import sys
import time
import threading
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from translation.monitoring.translation_monitor import get_monitor
from translation.monitoring.dashboard import start_dashboard
from translation.monitoring.report_generator import TranslationReportGenerator
from translation.monitoring.cost_analyzer import TranslationCostAnalyzer

class MonitoringSystemManager:
    """监控系统管理器"""
    
    def __init__(self):
        self.monitor = get_monitor()
        self.report_generator = TranslationReportGenerator()
        self.cost_analyzer = TranslationCostAnalyzer()
        self.dashboard_thread = None
        self.report_thread = None
        self.running = False
    
    def start_dashboard_server(self, host='127.0.0.1', port=5000):
        """启动仪表板服务器"""
        print(f"🚀 启动监控仪表板服务器: http://{host}:{port}")
        
        def run_dashboard():
            try:
                start_dashboard(host=host, port=port, debug=False)
            except Exception as e:
                print(f"❌ 仪表板服务器启动失败: {e}")
        
        self.dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
        self.dashboard_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
        print(f"✅ 监控仪表板已启动，访问地址: http://{host}:{port}")
    
    def start_auto_reporting(self, interval_hours=24):
        """启动自动报告生成"""
        print(f"📊 启动自动报告生成，间隔: {interval_hours}小时")
        
        def generate_reports():
            while self.running:
                try:
                    print(f"📈 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 生成自动报告...")
                    
                    # 生成每日报告
                    daily_report = self.report_generator.generate_daily_report()
                    print(f"✅ 每日报告已生成")
                    
                    # 如果是周一，生成周报告
                    if datetime.now().weekday() == 0:  # 周一
                        weekly_report = self.report_generator.generate_weekly_report()
                        print(f"✅ 周报告已生成")
                    
                    # 生成成本分析报告
                    cost_report = self.cost_analyzer.generate_cost_report(days=1)
                    print(f"💰 成本分析完成，今日成本: ¥{cost_report.get('total_cost', 0):.2f}")
                    
                except Exception as e:
                    print(f"❌ 自动报告生成失败: {e}")
                
                # 等待下一次执行
                time.sleep(interval_hours * 3600)
        
        self.report_thread = threading.Thread(target=generate_reports, daemon=True)
        self.report_thread.start()
    
    def show_system_status(self):
        """显示系统状态"""
        print("\n" + "="*60)
        print("📊 翻译监控系统状态")
        print("="*60)
        
        # 显示服务健康状态
        print("\n🚀 服务健康状态:")
        service_names = list(self.monitor.service_stats.keys())
        
        if not service_names:
            print("   暂无服务数据")
        else:
            for service_name in service_names:
                health = self.monitor.get_service_health(service_name)
                status_icon = "✅" if health.is_healthy else "❌"
                print(f"   {status_icon} {service_name}: 成功率 {health.success_rate:.1%}, "
                      f"响应时间 {health.avg_response_time:.2f}s, "
                      f"请求数 {health.total_requests}")
        
        # 显示今日统计
        print("\n📈 今日统计:")
        today = datetime.now().strftime('%Y-%m-%d')
        daily_stats = self.monitor.get_daily_statistics(today)
        overall = daily_stats.get('overall', {})
        
        print(f"   总请求数: {overall.get('total_requests', 0)}")
        print(f"   成功率: {overall.get('success_rate', 0):.1%}")
        print(f"   平均响应时间: {overall.get('avg_response_time', 0):.2f}秒")
        print(f"   总成本: ¥{overall.get('total_cost', 0):.2f}")
        
        # 显示最近报警
        print("\n🚨 最近报警 (24小时内):")
        recent_alerts = self.monitor.get_recent_alerts(hours=24)
        
        if not recent_alerts:
            print("   ✅ 无报警信息")
        else:
            for alert in recent_alerts[:5]:  # 显示最近5条
                severity_icon = "🔴" if alert['severity'] == 'CRITICAL' else "🟡"
                print(f"   {severity_icon} {alert['service_name']}: {alert['message']}")
                print(f"      时间: {alert['timestamp']}")
        
        print("\n" + "="*60)
    
    def run_cost_analysis(self, days=7):
        """运行成本分析"""
        print(f"\n💰 运行最近 {days} 天的成本分析...")
        
        try:
            # 综合成本报告
            cost_report = self.cost_analyzer.generate_cost_report(days=days)
            
            print(f"📊 成本分析结果:")
            print(f"   总成本: ¥{cost_report['total_cost']:.2f}")
            print(f"   日均成本: ¥{cost_report['avg_daily_cost']:.2f}")
            print(f"   预计月度成本: ¥{cost_report['projected_monthly_cost']:.2f}")
            print(f"   预计年度成本: ¥{cost_report['projected_annual_cost']:.2f}")
            
            # 服务比较
            service_comparison = cost_report['service_comparison']
            if service_comparison.get('service_comparison'):
                print(f"\n🏆 服务性价比排名:")
                for i, service in enumerate(service_comparison['service_comparison'][:3]):
                    rank_icon = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
                    print(f"   {rank_icon} {service['service_name']}: "
                          f"评分 {service['value_score']:.1f}, "
                          f"单次成本 ¥{service['cost_per_request']:.4f}")
            
            # 优化建议
            recommendations = cost_report.get('comprehensive_recommendations', [])
            if recommendations:
                print(f"\n💡 优化建议:")
                for rec in recommendations[:5]:
                    print(f"   • {rec}")
        
        except Exception as e:
            print(f"❌ 成本分析失败: {e}")
    
    def generate_manual_reports(self):
        """手动生成报告"""
        print("\n📊 手动生成报告...")
        
        try:
            # 生成今日报告
            print("📈 生成每日报告...")
            daily_report = self.report_generator.generate_daily_report()
            print(f"✅ 每日报告已保存")
            
            # 生成周报告
            print("📊 生成周报告...")
            weekly_report = self.report_generator.generate_weekly_report()
            print(f"✅ 周报告已保存")
            
            # 显示报告路径
            reports_dir = Path("translation/monitoring/reports")
            if reports_dir.exists():
                print(f"\n📁 报告保存位置: {reports_dir.absolute()}")
                report_files = list(reports_dir.glob("*.html"))
                if report_files:
                    print("   最新报告文件:")
                    for file in sorted(report_files, key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
                        print(f"   • {file.name}")
        
        except Exception as e:
            print(f"❌ 报告生成失败: {e}")
    
    def start_full_system(self, dashboard_host='127.0.0.1', dashboard_port=5000, auto_report=True):
        """启动完整监控系统"""
        print("🚀 启动翻译质量监控和运维体系")
        print("="*60)
        
        self.running = True
        
        try:
            # 1. 启动仪表板服务器
            self.start_dashboard_server(dashboard_host, dashboard_port)
            
            # 2. 启动自动报告生成
            if auto_report:
                self.start_auto_reporting(interval_hours=24)
            
            # 3. 显示系统状态
            self.show_system_status()
            
            print(f"\n✅ 监控系统已完全启动")
            print(f"🌐 仪表板地址: http://{dashboard_host}:{dashboard_port}")
            print(f"📊 自动报告: {'已启用' if auto_report else '已禁用'}")
            print(f"📁 报告目录: {Path('translation/monitoring/reports').absolute()}")
            print(f"💾 数据库位置: {self.monitor.db_path}")
            
            print(f"\n⌨️  可用命令:")
            print(f"   • 按 's' 显示系统状态")
            print(f"   • 按 'c' 运行成本分析")
            print(f"   • 按 'r' 生成手动报告")
            print(f"   • 按 'q' 退出系统")
            
            # 交互式命令循环
            self._interactive_loop()
            
        except KeyboardInterrupt:
            print(f"\n⏹️  收到中断信号，正在关闭监控系统...")
        except Exception as e:
            print(f"❌ 监控系统启动失败: {e}")
        finally:
            self.running = False
            print(f"👋 监控系统已关闭")
    
    def _interactive_loop(self):
        """交互式命令循环"""
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if command == 'q' or command == 'quit':
                    break
                elif command == 's' or command == 'status':
                    self.show_system_status()
                elif command == 'c' or command == 'cost':
                    self.run_cost_analysis()
                elif command == 'r' or command == 'report':
                    self.generate_manual_reports()
                elif command == 'h' or command == 'help':
                    print("可用命令: s(status), c(cost), r(report), q(quit)")
                elif command == '':
                    continue
                else:
                    print(f"未知命令: {command}，输入 'h' 查看帮助")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
            except Exception as e:
                print(f"命令执行错误: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='翻译监控系统启动器')
    parser.add_argument('--host', default='127.0.0.1', help='仪表板服务器地址')
    parser.add_argument('--port', type=int, default=5000, help='仪表板服务器端口')
    parser.add_argument('--no-dashboard', action='store_true', help='不启动仪表板服务器')
    parser.add_argument('--no-auto-report', action='store_true', help='不启动自动报告')
    parser.add_argument('--status-only', action='store_true', help='只显示状态信息')
    parser.add_argument('--cost-analysis', type=int, metavar='DAYS', help='运行成本分析（指定天数）')
    parser.add_argument('--generate-reports', action='store_true', help='生成报告后退出')
    
    args = parser.parse_args()
    
    # 创建监控系统管理器
    manager = MonitoringSystemManager()
    
    try:
        if args.status_only:
            # 只显示状态
            manager.show_system_status()
        
        elif args.cost_analysis:
            # 运行成本分析
            manager.run_cost_analysis(days=args.cost_analysis)
        
        elif args.generate_reports:
            # 生成报告
            manager.generate_manual_reports()
        
        else:
            # 启动完整系统
            start_dashboard = not args.no_dashboard
            auto_report = not args.no_auto_report
            
            if start_dashboard:
                manager.start_full_system(
                    dashboard_host=args.host,
                    dashboard_port=args.port,
                    auto_report=auto_report
                )
            else:
                # 只启动后台监控
                manager.running = True
                if auto_report:
                    manager.start_auto_reporting()
                
                print("🔄 后台监控已启动，按 Ctrl+C 退出")
                try:
                    while manager.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    manager.running = False
                    print("\n👋 监控系统已关闭")
    
    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()