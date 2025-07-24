#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译质量自动报告生成器
生成详细的翻译质量分析报告和优化建议
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib import rcParams
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️ matplotlib未安装，图表功能将被禁用")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
from translation.monitoring.translation_monitor import get_monitor

# 设置中文字体
if MATPLOTLIB_AVAILABLE:
    rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
    rcParams['axes.unicode_minus'] = False

class TranslationReportGenerator:
    """翻译质量报告生成器"""
    
    def __init__(self, output_dir: str = "translation/monitoring/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.monitor = get_monitor()
    
    def generate_daily_report(self, date: str = None) -> Dict[str, Any]:
        """生成每日报告"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 生成 {date} 的每日翻译质量报告...")
        
        # 获取统计数据
        daily_stats = self.monitor.get_daily_statistics(date)
        
        # 获取报警信息
        alerts = self.monitor.get_recent_alerts(hours=24)
        daily_alerts = [
            alert for alert in alerts 
            if alert['timestamp'].startswith(date)
        ]
        
        # 生成报告内容
        report = {
            'report_type': 'daily',
            'date': date,
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_daily_summary(daily_stats),
            'detailed_stats': daily_stats,
            'alerts': daily_alerts,
            'recommendations': self._generate_daily_recommendations(daily_stats, daily_alerts),
            'charts': self._generate_daily_charts(date)
        }
        
        # 保存报告
        report_file = self.output_dir / f"daily_report_{date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成HTML报告
        html_report = self._generate_html_report(report)
        html_file = self.output_dir / f"daily_report_{date}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"✅ 每日报告已生成: {report_file}")
        print(f"📄 HTML报告: {html_file}")
        
        return report
    
    def generate_weekly_report(self, end_date: str = None) -> Dict[str, Any]:
        """生成周报告"""
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(days=6)
        start_date = start_dt.strftime('%Y-%m-%d')
        
        print(f"📈 生成 {start_date} 至 {end_date} 的周报告...")
        
        # 收集一周的数据
        weekly_data = []
        for i in range(7):
            current_date = (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats = self.monitor.get_daily_statistics(current_date)
            weekly_data.append({
                'date': current_date,
                'stats': daily_stats
            })
        
        # 获取周报警
        weekly_alerts = self.monitor.get_recent_alerts(hours=168)  # 7天
        
        # 生成质量报告
        quality_report = self.monitor.generate_quality_report(days=7)
        
        report = {
            'report_type': 'weekly',
            'period': f"{start_date} 至 {end_date}",
            'generated_at': datetime.now().isoformat(),
            'summary': self._generate_weekly_summary(weekly_data),
            'daily_breakdown': weekly_data,
            'quality_analysis': quality_report,
            'alerts_summary': self._analyze_weekly_alerts(weekly_alerts),
            'trends': self._analyze_weekly_trends(weekly_data),
            'recommendations': self._generate_weekly_recommendations(weekly_data, quality_report),
            'charts': self._generate_weekly_charts(weekly_data)
        }
        
        # 保存报告
        report_file = self.output_dir / f"weekly_report_{start_date}_to_{end_date}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 生成HTML报告
        html_report = self._generate_html_report(report)
        html_file = self.output_dir / f"weekly_report_{start_date}_to_{end_date}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"✅ 周报告已生成: {report_file}")
        print(f"📄 HTML报告: {html_file}")
        
        return report
    
    def _generate_daily_summary(self, daily_stats: Dict) -> Dict[str, Any]:
        """生成每日摘要"""
        overall = daily_stats.get('overall', {})
        by_service = daily_stats.get('by_service', {})
        
        total_requests = overall.get('total_requests', 0)
        success_rate = overall.get('success_rate', 0)
        avg_response_time = overall.get('avg_response_time', 0)
        total_cost = overall.get('total_cost', 0)
        
        # 服务表现
        best_service = None
        worst_service = None
        
        if by_service:
            services_by_success = sorted(
                by_service.items(),
                key=lambda x: x[1].get('success_rate', 0),
                reverse=True
            )
            if services_by_success:
                best_service = services_by_success[0][0]
                worst_service = services_by_success[-1][0]
        
        return {
            'total_requests': total_requests,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'total_cost': total_cost,
            'service_count': len(by_service),
            'best_performing_service': best_service,
            'worst_performing_service': worst_service,
            'status': self._get_overall_status(success_rate, avg_response_time)
        }
    
    def _generate_daily_recommendations(self, daily_stats: Dict, alerts: List) -> List[str]:
        """生成每日建议"""
        recommendations = []
        overall = daily_stats.get('overall', {})
        by_service = daily_stats.get('by_service', {})
        
        success_rate = overall.get('success_rate', 0)
        avg_response_time = overall.get('avg_response_time', 0)
        
        # 基于成功率的建议
        if success_rate < 0.9:
            recommendations.append(f"🔴 成功率偏低({success_rate:.1%})，建议检查API配置和网络连接")
        elif success_rate < 0.95:
            recommendations.append(f"🟡 成功率需要改进({success_rate:.1%})，建议优化错误处理机制")
        else:
            recommendations.append(f"✅ 成功率表现良好({success_rate:.1%})")
        
        # 基于响应时间的建议
        if avg_response_time > 5:
            recommendations.append(f"🔴 响应时间过长({avg_response_time:.2f}秒)，建议优化网络或切换更快的服务")
        elif avg_response_time > 3:
            recommendations.append(f"🟡 响应时间偏高({avg_response_time:.2f}秒)，建议监控网络状况")
        else:
            recommendations.append(f"✅ 响应时间表现良好({avg_response_time:.2f}秒)")
        
        # 基于服务表现的建议
        for service_name, stats in by_service.items():
            service_success = stats.get('success_rate', 0)
            service_time = stats.get('avg_response_time', 0)
            
            if service_success < 0.9:
                recommendations.append(f"🔧 {service_name}服务需要关注，成功率仅{service_success:.1%}")
            
            if service_time > 5:
                recommendations.append(f"⚡ {service_name}服务响应慢，平均{service_time:.2f}秒")
        
        # 基于报警的建议
        if alerts:
            critical_alerts = [a for a in alerts if a['severity'] == 'CRITICAL']
            if critical_alerts:
                recommendations.append(f"🚨 发现{len(critical_alerts)}个严重报警，需要立即处理")
        
        return recommendations
    
    def _generate_weekly_summary(self, weekly_data: List) -> Dict[str, Any]:
        """生成周摘要"""
        total_requests = 0
        total_success = 0
        total_response_time = 0
        total_cost = 0
        valid_days = 0
        
        for day_data in weekly_data:
            overall = day_data['stats'].get('overall', {})
            if overall.get('total_requests', 0) > 0:
                total_requests += overall.get('total_requests', 0)
                total_success += overall.get('success_count', 0)
                total_response_time += overall.get('avg_response_time', 0)
                total_cost += overall.get('total_cost', 0)
                valid_days += 1
        
        avg_success_rate = total_success / max(total_requests, 1)
        avg_response_time = total_response_time / max(valid_days, 1)
        
        return {
            'total_requests': total_requests,
            'avg_success_rate': avg_success_rate,
            'avg_response_time': avg_response_time,
            'total_cost': total_cost,
            'active_days': valid_days,
            'avg_daily_requests': total_requests / max(valid_days, 1),
            'status': self._get_overall_status(avg_success_rate, avg_response_time)
        }
    
    def _analyze_weekly_trends(self, weekly_data: List) -> Dict[str, Any]:
        """分析周趋势"""
        dates = []
        success_rates = []
        response_times = []
        request_counts = []
        
        for day_data in weekly_data:
            dates.append(day_data['date'])
            overall = day_data['stats'].get('overall', {})
            success_rates.append(overall.get('success_rate', 0))
            response_times.append(overall.get('avg_response_time', 0))
            request_counts.append(overall.get('total_requests', 0))
        
        # 计算趋势
        success_trend = self._calculate_trend(success_rates)
        response_trend = self._calculate_trend(response_times)
        volume_trend = self._calculate_trend(request_counts)
        
        return {
            'success_rate_trend': success_trend,
            'response_time_trend': response_trend,
            'request_volume_trend': volume_trend,
            'daily_data': {
                'dates': dates,
                'success_rates': success_rates,
                'response_times': response_times,
                'request_counts': request_counts
            }
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return "stable"
        
        # 简单线性趋势计算
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        diff_percent = (second_half - first_half) / max(first_half, 0.001)
        
        if diff_percent > 0.05:
            return "improving"
        elif diff_percent < -0.05:
            return "declining"
        else:
            return "stable"
    
    def _generate_weekly_recommendations(self, weekly_data: List, quality_report: Dict) -> List[str]:
        """生成周建议"""
        recommendations = []
        
        # 基于趋势的建议
        trends = self._analyze_weekly_trends(weekly_data)
        
        if trends['success_rate_trend'] == 'declining':
            recommendations.append("📉 成功率呈下降趋势，建议检查服务稳定性")
        elif trends['success_rate_trend'] == 'improving':
            recommendations.append("📈 成功率持续改善，当前优化措施有效")
        
        if trends['response_time_trend'] == 'declining':
            recommendations.append("⚡ 响应时间持续恶化，建议优化网络或服务配置")
        elif trends['response_time_trend'] == 'improving':
            recommendations.append("🚀 响应时间持续改善，性能优化效果显著")
        
        # 基于质量报告的建议
        quality_recommendations = quality_report.get('recommendations', [])
        recommendations.extend(quality_recommendations)
        
        return recommendations
    
    def _analyze_weekly_alerts(self, alerts: List) -> Dict[str, Any]:
        """分析周报警"""
        if not alerts:
            return {
                'total_alerts': 0,
                'critical_count': 0,
                'warning_count': 0,
                'most_common_type': None,
                'most_affected_service': None
            }
        
        critical_count = len([a for a in alerts if a['severity'] == 'CRITICAL'])
        warning_count = len([a for a in alerts if a['severity'] == 'WARNING'])
        
        # 统计最常见的报警类型
        alert_types = {}
        service_alerts = {}
        
        for alert in alerts:
            alert_type = alert['alert_type']
            service = alert['service_name']
            
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
            service_alerts[service] = service_alerts.get(service, 0) + 1
        
        most_common_type = max(alert_types.items(), key=lambda x: x[1])[0] if alert_types else None
        most_affected_service = max(service_alerts.items(), key=lambda x: x[1])[0] if service_alerts else None
        
        return {
            'total_alerts': len(alerts),
            'critical_count': critical_count,
            'warning_count': warning_count,
            'most_common_type': most_common_type,
            'most_affected_service': most_affected_service,
            'alert_types_breakdown': alert_types,
            'service_alerts_breakdown': service_alerts
        }
    
    def _generate_daily_charts(self, date: str) -> Dict[str, str]:
        """生成每日图表"""
        charts = {}
        
        try:
            # 获取当日按小时的数据（模拟）
            hourly_data = self._get_hourly_data(date)
            
            if hourly_data:
                # 成功率图表
                success_chart = self._create_hourly_success_chart(hourly_data, date)
                charts['hourly_success_rate'] = success_chart
                
                # 响应时间图表
                response_chart = self._create_hourly_response_chart(hourly_data, date)
                charts['hourly_response_time'] = response_chart
        
        except Exception as e:
            print(f"⚠️ 生成每日图表失败: {e}")
        
        return charts
    
    def _generate_weekly_charts(self, weekly_data: List) -> Dict[str, str]:
        """生成周图表"""
        charts = {}
        
        try:
            # 提取数据
            dates = [day['date'] for day in weekly_data]
            success_rates = [day['stats'].get('overall', {}).get('success_rate', 0) for day in weekly_data]
            response_times = [day['stats'].get('overall', {}).get('avg_response_time', 0) for day in weekly_data]
            request_counts = [day['stats'].get('overall', {}).get('total_requests', 0) for day in weekly_data]
            
            # 周趋势图表
            trend_chart = self._create_weekly_trend_chart(dates, success_rates, response_times, request_counts)
            charts['weekly_trends'] = trend_chart
            
        except Exception as e:
            print(f"⚠️ 生成周图表失败: {e}")
        
        return charts
    
    def _get_hourly_data(self, date: str) -> List[Dict]:
        """获取按小时的数据（简化实现）"""
        # 这里应该从数据库获取实际的按小时数据
        # 目前返回模拟数据
        hourly_data = []
        for hour in range(24):
            hourly_data.append({
                'hour': hour,
                'success_rate': 0.95 + (hour % 3) * 0.01,  # 模拟数据
                'response_time': 2.0 + (hour % 5) * 0.2,   # 模拟数据
                'request_count': 10 + (hour % 7) * 5       # 模拟数据
            })
        return hourly_data
    
    def _create_hourly_success_chart(self, hourly_data: List, date: str) -> str:
        """创建按小时成功率图表"""
        if not MATPLOTLIB_AVAILABLE:
            return ""
            
        try:
            hours = [data['hour'] for data in hourly_data]
            success_rates = [data['success_rate'] * 100 for data in hourly_data]
            
            plt.figure(figsize=(12, 6))
            plt.plot(hours, success_rates, marker='o', linewidth=2, markersize=4)
            plt.title(f'{date} 按小时成功率趋势', fontsize=14, fontweight='bold')
            plt.xlabel('小时')
            plt.ylabel('成功率 (%)')
            plt.grid(True, alpha=0.3)
            plt.ylim(90, 100)
            
            chart_file = self.output_dir / f"hourly_success_{date}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_file)
            
        except Exception as e:
            print(f"创建按小时成功率图表失败: {e}")
            return ""
    
    def _create_hourly_response_chart(self, hourly_data: List, date: str) -> str:
        """创建按小时响应时间图表"""
        if not MATPLOTLIB_AVAILABLE:
            return ""
            
        try:
            hours = [data['hour'] for data in hourly_data]
            response_times = [data['response_time'] for data in hourly_data]
            
            plt.figure(figsize=(12, 6))
            plt.plot(hours, response_times, marker='s', linewidth=2, markersize=4, color='orange')
            plt.title(f'{date} 按小时响应时间趋势', fontsize=14, fontweight='bold')
            plt.xlabel('小时')
            plt.ylabel('响应时间 (秒)')
            plt.grid(True, alpha=0.3)
            
            chart_file = self.output_dir / f"hourly_response_{date}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_file)
            
        except Exception as e:
            print(f"创建按小时响应时间图表失败: {e}")
            return ""
    
    def _create_weekly_trend_chart(self, dates: List, success_rates: List, response_times: List, request_counts: List) -> str:
        """创建周趋势图表"""
        if not MATPLOTLIB_AVAILABLE:
            return ""
            
        try:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
            
            # 成功率趋势
            ax1.plot(dates, [rate * 100 for rate in success_rates], marker='o', linewidth=2, color='green')
            ax1.set_title('周成功率趋势', fontweight='bold')
            ax1.set_ylabel('成功率 (%)')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # 响应时间趋势
            ax2.plot(dates, response_times, marker='s', linewidth=2, color='orange')
            ax2.set_title('周响应时间趋势', fontweight='bold')
            ax2.set_ylabel('响应时间 (秒)')
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            # 请求量趋势
            ax3.bar(dates, request_counts, color='blue', alpha=0.7)
            ax3.set_title('周请求量趋势', fontweight='bold')
            ax3.set_ylabel('请求数')
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            chart_file = self.output_dir / f"weekly_trends_{dates[0]}_to_{dates[-1]}.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_file)
            
        except Exception as e:
            print(f"创建周趋势图表失败: {e}")
            return ""
    
    def _get_overall_status(self, success_rate: float, avg_response_time: float) -> str:
        """获取整体状态"""
        if success_rate >= 0.95 and avg_response_time <= 3:
            return "excellent"
        elif success_rate >= 0.9 and avg_response_time <= 5:
            return "good"
        elif success_rate >= 0.8 and avg_response_time <= 8:
            return "fair"
        else:
            return "poor"
    
    def _generate_html_report(self, report: Dict) -> str:
        """生成HTML报告"""
        report_type = report.get('report_type', 'daily')
        
        if report_type == 'daily':
            return self._generate_daily_html(report)
        else:
            return self._generate_weekly_html(report)
    
    def _generate_daily_html(self, report: Dict) -> str:
        """生成每日HTML报告"""
        summary = report.get('summary', {})
        recommendations = report.get('recommendations', [])
        alerts = report.get('alerts', [])
        
        status_colors = {
            'excellent': '#27ae60',
            'good': '#2ecc71', 
            'fair': '#f39c12',
            'poor': '#e74c3c'
        }
        
        status_color = status_colors.get(summary.get('status', 'fair'), '#f39c12')
        
        html = f'''
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>翻译服务每日报告 - {report.get('date')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f7fa; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; color: white; background-color: {status_color}; }}
                .recommendations {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .recommendation {{ padding: 10px; margin: 5px 0; background-color: #f8f9fa; border-left: 4px solid #007bff; }}
                .alerts {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .alert {{ padding: 10px; margin: 5px 0; border-radius: 5px; }}
                .alert-critical {{ background-color: #fdf2f2; border-left: 4px solid #e74c3c; }}
                .alert-warning {{ background-color: #fefbf3; border-left: 4px solid #f39c12; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #333; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 翻译服务每日报告</h1>
                <p>{report.get('date')} | 生成时间: {report.get('generated_at', '')[:19]}</p>
            </div>
            
            <div class="summary">
                <h2>📈 每日摘要</h2>
                <p>整体状态: <span class="status">{summary.get('status', '').upper()}</span></p>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{summary.get('total_requests', 0)}</div>
                        <div class="stat-label">总请求数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get('success_rate', 0):.1%}</div>
                        <div class="stat-label">成功率</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get('avg_response_time', 0):.2f}s</div>
                        <div class="stat-label">平均响应时间</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">¥{summary.get('total_cost', 0):.2f}</div>
                        <div class="stat-label">总成本</div>
                    </div>
                </div>
            </div>
            
            <div class="recommendations">
                <h2>💡 优化建议</h2>
                {''.join(f'<div class="recommendation">{rec}</div>' for rec in recommendations)}
            </div>
            
            <div class="alerts">
                <h2>🚨 报警信息</h2>
                {f'<p>今日共发生 {len(alerts)} 次报警</p>' if alerts else '<p style="color: #27ae60;">✅ 今日无报警信息</p>'}
                {''.join(f'<div class="alert alert-{alert["severity"].lower()}"><strong>{alert["service_name"]}</strong> - {alert["message"]}<br><small>{alert["timestamp"]}</small></div>' for alert in alerts[:10])}
            </div>
        </body>
        </html>
        '''
        
        return html
    
    def _generate_weekly_html(self, report: Dict) -> str:
        """生成周HTML报告"""
        # 类似每日报告的HTML生成，但包含更多周数据
        summary = report.get('summary', {})
        recommendations = report.get('recommendations', [])
        trends = report.get('trends', {})
        
        return f'''
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <title>翻译服务周报告 - {report.get('period')}</title>
            <style>
                /* 样式与每日报告类似，但适配周数据 */
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f7fa; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
                .summary {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .trends {{ background: white; padding: 20px; margin: 20px 0; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .trend-item {{ padding: 10px; margin: 5px 0; background-color: #f8f9fa; border-radius: 5px; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
                .stat-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .stat-value {{ font-size: 2em; font-weight: bold; color: #333; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📈 翻译服务周报告</h1>
                <p>{report.get('period')} | 生成时间: {report.get('generated_at', '')[:19]}</p>
            </div>
            
            <div class="summary">
                <h2>📊 周摘要</h2>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{summary.get('total_requests', 0)}</div>
                        <div class="stat-label">总请求数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get('avg_success_rate', 0):.1%}</div>
                        <div class="stat-label">平均成功率</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{summary.get('avg_response_time', 0):.2f}s</div>
                        <div class="stat-label">平均响应时间</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">¥{summary.get('total_cost', 0):.2f}</div>
                        <div class="stat-label">总成本</div>
                    </div>
                </div>
            </div>
            
            <div class="trends">
                <h2>📈 趋势分析</h2>
                <div class="trend-item">成功率趋势: <strong>{trends.get('success_rate_trend', 'stable')}</strong></div>
                <div class="trend-item">响应时间趋势: <strong>{trends.get('response_time_trend', 'stable')}</strong></div>
                <div class="trend-item">请求量趋势: <strong>{trends.get('request_volume_trend', 'stable')}</strong></div>
            </div>
            
            <div class="recommendations">
                <h2>💡 优化建议</h2>
                {''.join(f'<div class="recommendation">{rec}</div>' for rec in recommendations)}
            </div>
        </body>
        </html>
        '''

def generate_reports():
    """生成所有报告的便捷函数"""
    generator = TranslationReportGenerator()
    
    # 生成今日报告
    daily_report = generator.generate_daily_report()
    
    # 生成本周报告
    weekly_report = generator.generate_weekly_report()
    
    return daily_report, weekly_report

if __name__ == "__main__":
    generate_reports()