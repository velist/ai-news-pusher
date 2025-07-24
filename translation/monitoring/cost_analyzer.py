#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务成本分析器
分析翻译服务的成本消耗和优化建议
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from translation.monitoring.translation_monitor import get_monitor

@dataclass
class CostBreakdown:
    """成本分解数据"""
    service_name: str
    total_cost: float
    request_count: int
    avg_cost_per_request: float
    input_tokens: int
    output_tokens: int
    cost_per_input_token: float
    cost_per_output_token: float

@dataclass
class CostOptimization:
    """成本优化建议"""
    current_cost: float
    optimized_cost: float
    savings: float
    savings_percentage: float
    recommendations: List[str]

class TranslationCostAnalyzer:
    """翻译成本分析器"""
    
    def __init__(self):
        self.monitor = get_monitor()
        
        # 各服务的定价信息（每1000个token的价格，单位：人民币）
        self.pricing = {
            'siliconflow': {
                'Qwen/Qwen2.5-7B-Instruct': {
                    'input': 0.0007,   # ¥0.0007/1K tokens
                    'output': 0.0007
                },
                'meta-llama/Meta-Llama-3.1-8B-Instruct': {
                    'input': 0.0007,
                    'output': 0.0007
                },
                'Qwen/Qwen2.5-72B-Instruct': {
                    'input': 0.0035,   # 更贵的大模型
                    'output': 0.0035
                }
            },
            'baidu': {
                'default': {
                    'input': 0.012,    # 百度翻译API定价
                    'output': 0.012
                }
            },
            'tencent': {
                'default': {
                    'input': 0.058,    # 腾讯翻译API定价
                    'output': 0.058
                }
            },
            'google': {
                'default': {
                    'input': 0.145,    # Google翻译API定价
                    'output': 0.145
                }
            }
        }
    
    def analyze_daily_costs(self, date: str = None) -> Dict[str, Any]:
        """分析每日成本"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"💰 分析 {date} 的翻译成本...")
        
        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取当日所有翻译记录
                cursor.execute('''
                    SELECT 
                        service_name,
                        operation_type,
                        input_length,
                        output_length,
                        cost_estimate,
                        success
                    FROM translation_metrics 
                    WHERE DATE(timestamp) = ? AND success = 1
                ''', (date,))
                
                records = cursor.fetchall()
                
                if not records:
                    return {
                        'date': date,
                        'total_cost': 0,
                        'service_breakdown': {},
                        'cost_analysis': {},
                        'optimization_suggestions': []
                    }
                
                # 按服务分组分析
                service_costs = {}
                total_cost = 0
                
                for record in records:
                    service, operation, input_len, output_len, cost_est, success = record
                    
                    if service not in service_costs:
                        service_costs[service] = {
                            'requests': 0,
                            'total_cost': 0,
                            'input_tokens': 0,
                            'output_tokens': 0,
                            'operations': {}
                        }
                    
                    # 估算实际成本（如果cost_estimate为0）
                    actual_cost = cost_est if cost_est > 0 else self._estimate_cost(service, input_len, output_len)
                    
                    service_costs[service]['requests'] += 1
                    service_costs[service]['total_cost'] += actual_cost
                    service_costs[service]['input_tokens'] += input_len
                    service_costs[service]['output_tokens'] += output_len
                    
                    # 按操作类型统计
                    if operation not in service_costs[service]['operations']:
                        service_costs[service]['operations'][operation] = {'count': 0, 'cost': 0}
                    service_costs[service]['operations'][operation]['count'] += 1
                    service_costs[service]['operations'][operation]['cost'] += actual_cost
                    
                    total_cost += actual_cost
                
                # 生成成本分解
                cost_breakdown = []
                for service, data in service_costs.items():
                    breakdown = CostBreakdown(
                        service_name=service,
                        total_cost=data['total_cost'],
                        request_count=data['requests'],
                        avg_cost_per_request=data['total_cost'] / max(data['requests'], 1),
                        input_tokens=data['input_tokens'],
                        output_tokens=data['output_tokens'],
                        cost_per_input_token=self._get_input_price(service),
                        cost_per_output_token=self._get_output_price(service)
                    )
                    cost_breakdown.append(breakdown)
                
                # 成本分析
                cost_analysis = self._analyze_cost_efficiency(cost_breakdown)
                
                # 优化建议
                optimization = self._generate_cost_optimization(cost_breakdown, total_cost)
                
                return {
                    'date': date,
                    'total_cost': total_cost,
                    'service_breakdown': service_costs,
                    'cost_breakdown': [
                        {
                            'service_name': cb.service_name,
                            'total_cost': cb.total_cost,
                            'request_count': cb.request_count,
                            'avg_cost_per_request': cb.avg_cost_per_request,
                            'cost_percentage': (cb.total_cost / total_cost * 100) if total_cost > 0 else 0
                        }
                        for cb in cost_breakdown
                    ],
                    'cost_analysis': cost_analysis,
                    'optimization_suggestions': optimization.recommendations if optimization else []
                }
                
        except Exception as e:
            print(f"❌ 成本分析失败: {str(e)}")
            return {
                'date': date,
                'total_cost': 0,
                'service_breakdown': {},
                'cost_analysis': {},
                'optimization_suggestions': []
            }
    
    def analyze_monthly_costs(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """分析月度成本"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        print(f"📊 分析 {year}年{month}月 的翻译成本...")
        
        # 获取月度数据
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        daily_costs = []
        total_monthly_cost = 0
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            daily_analysis = self.analyze_daily_costs(date_str)
            daily_costs.append(daily_analysis)
            total_monthly_cost += daily_analysis['total_cost']
            current_date += timedelta(days=1)
        
        # 月度统计
        service_monthly_costs = {}
        for daily in daily_costs:
            for service, data in daily['service_breakdown'].items():
                if service not in service_monthly_costs:
                    service_monthly_costs[service] = {
                        'total_cost': 0,
                        'total_requests': 0,
                        'days_active': 0
                    }
                service_monthly_costs[service]['total_cost'] += data['total_cost']
                service_monthly_costs[service]['total_requests'] += data['requests']
                if data['requests'] > 0:
                    service_monthly_costs[service]['days_active'] += 1
        
        # 成本趋势分析
        cost_trend = self._analyze_monthly_trend(daily_costs)
        
        # 月度优化建议
        monthly_optimization = self._generate_monthly_optimization(service_monthly_costs, total_monthly_cost)
        
        return {
            'year': year,
            'month': month,
            'total_monthly_cost': total_monthly_cost,
            'daily_breakdown': daily_costs,
            'service_monthly_costs': service_monthly_costs,
            'cost_trend': cost_trend,
            'optimization_suggestions': monthly_optimization,
            'projected_annual_cost': total_monthly_cost * 12  # 简单年度预测
        }
    
    def compare_service_costs(self, days: int = 30) -> Dict[str, Any]:
        """比较不同服务的成本效益"""
        print(f"🔍 比较最近 {days} 天的服务成本效益...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        try:
            with sqlite3.connect(self.monitor.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        service_name,
                        COUNT(*) as request_count,
                        SUM(input_length) as total_input,
                        SUM(output_length) as total_output,
                        AVG(confidence_score) as avg_confidence,
                        AVG(response_time) as avg_response_time,
                        SUM(cost_estimate) as total_cost_estimate
                    FROM translation_metrics 
                    WHERE datetime(timestamp) BETWEEN datetime(?) AND datetime(?)
                        AND success = 1
                    GROUP BY service_name
                ''', (start_date.isoformat(), end_date.isoformat()))
                
                service_comparison = []
                
                for row in cursor.fetchall():
                    service, requests, input_tokens, output_tokens, avg_conf, avg_time, cost_est = row
                    
                    # 计算实际成本
                    actual_cost = cost_est if cost_est > 0 else self._estimate_cost(service, input_tokens, output_tokens)
                    
                    # 计算效益指标
                    cost_per_request = actual_cost / max(requests, 1)
                    quality_score = avg_conf or 0
                    speed_score = max(0, 10 - avg_time) / 10  # 响应时间越短分数越高
                    
                    # 综合性价比评分 (0-100)
                    value_score = (quality_score * 0.6 + speed_score * 0.4) * 100 / max(cost_per_request, 0.001)
                    
                    service_comparison.append({
                        'service_name': service,
                        'request_count': requests,
                        'total_cost': actual_cost,
                        'cost_per_request': cost_per_request,
                        'avg_confidence': quality_score,
                        'avg_response_time': avg_time or 0,
                        'value_score': min(value_score, 100),  # 限制最高分100
                        'input_tokens': input_tokens,
                        'output_tokens': output_tokens
                    })
                
                # 按性价比排序
                service_comparison.sort(key=lambda x: x['value_score'], reverse=True)
                
                # 生成比较建议
                comparison_recommendations = self._generate_comparison_recommendations(service_comparison)
                
                return {
                    'comparison_period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
                    'service_comparison': service_comparison,
                    'best_value_service': service_comparison[0]['service_name'] if service_comparison else None,
                    'most_expensive_service': max(service_comparison, key=lambda x: x['cost_per_request'])['service_name'] if service_comparison else None,
                    'recommendations': comparison_recommendations
                }
                
        except Exception as e:
            print(f"❌ 服务成本比较失败: {str(e)}")
            return {
                'comparison_period': '',
                'service_comparison': [],
                'best_value_service': None,
                'most_expensive_service': None,
                'recommendations': []
            }
    
    def _estimate_cost(self, service_name: str, input_length: int, output_length: int, model: str = None) -> float:
        """估算翻译成本"""
        try:
            # 获取服务定价
            service_pricing = self.pricing.get(service_name.lower(), {})
            
            if not service_pricing:
                return 0.0
            
            # 选择模型定价
            if model and model in service_pricing:
                pricing = service_pricing[model]
            elif 'default' in service_pricing:
                pricing = service_pricing['default']
            else:
                # 使用第一个可用的定价
                pricing = list(service_pricing.values())[0]
            
            # 计算成本（按1000个token计费）
            input_cost = (input_length / 1000) * pricing['input']
            output_cost = (output_length / 1000) * pricing['output']
            
            return input_cost + output_cost
            
        except Exception as e:
            print(f"⚠️ 成本估算失败: {e}")
            return 0.0
    
    def _get_input_price(self, service_name: str) -> float:
        """获取输入token价格"""
        service_pricing = self.pricing.get(service_name.lower(), {})
        if 'default' in service_pricing:
            return service_pricing['default']['input']
        elif service_pricing:
            return list(service_pricing.values())[0]['input']
        return 0.0
    
    def _get_output_price(self, service_name: str) -> float:
        """获取输出token价格"""
        service_pricing = self.pricing.get(service_name.lower(), {})
        if 'default' in service_pricing:
            return service_pricing['default']['output']
        elif service_pricing:
            return list(service_pricing.values())[0]['output']
        return 0.0
    
    def _analyze_cost_efficiency(self, cost_breakdown: List[CostBreakdown]) -> Dict[str, Any]:
        """分析成本效率"""
        if not cost_breakdown:
            return {}
        
        total_cost = sum(cb.total_cost for cb in cost_breakdown)
        total_requests = sum(cb.request_count for cb in cost_breakdown)
        
        # 找出最贵和最便宜的服务
        most_expensive = max(cost_breakdown, key=lambda x: x.avg_cost_per_request)
        least_expensive = min(cost_breakdown, key=lambda x: x.avg_cost_per_request)
        
        # 计算成本分布
        cost_distribution = {
            cb.service_name: (cb.total_cost / total_cost * 100) if total_cost > 0 else 0
            for cb in cost_breakdown
        }
        
        return {
            'total_cost': total_cost,
            'total_requests': total_requests,
            'avg_cost_per_request': total_cost / max(total_requests, 1),
            'most_expensive_service': {
                'name': most_expensive.service_name,
                'cost_per_request': most_expensive.avg_cost_per_request
            },
            'least_expensive_service': {
                'name': least_expensive.service_name,
                'cost_per_request': least_expensive.avg_cost_per_request
            },
            'cost_distribution': cost_distribution
        }
    
    def _generate_cost_optimization(self, cost_breakdown: List[CostBreakdown], total_cost: float) -> Optional[CostOptimization]:
        """生成成本优化建议"""
        if not cost_breakdown:
            return None
        
        recommendations = []
        potential_savings = 0
        
        # 分析每个服务的优化潜力
        for cb in cost_breakdown:
            service_name = cb.service_name.lower()
            
            # 建议使用更便宜的模型
            if 'siliconflow' in service_name:
                if cb.avg_cost_per_request > 0.001:  # 如果成本较高
                    recommendations.append(f"考虑将{cb.service_name}切换到更经济的模型，可节省约30%成本")
                    potential_savings += cb.total_cost * 0.3
            
            # 建议批量处理
            if cb.request_count > 100 and cb.avg_cost_per_request > 0.005:
                recommendations.append(f"{cb.service_name}请求量大，建议使用批量翻译减少API调用成本")
                potential_savings += cb.total_cost * 0.15
            
            # 建议缓存优化
            if cb.total_cost > total_cost * 0.3:  # 如果某服务占总成本30%以上
                recommendations.append(f"{cb.service_name}成本占比较高，建议加强缓存策略减少重复翻译")
                potential_savings += cb.total_cost * 0.2
        
        # 通用优化建议
        if total_cost > 10:  # 如果日成本超过10元
            recommendations.append("考虑实施智能路由，根据内容复杂度选择合适的翻译服务")
            potential_savings += total_cost * 0.1
        
        if not recommendations:
            recommendations.append("当前成本控制良好，继续保持现有配置")
        
        optimized_cost = total_cost - potential_savings
        savings_percentage = (potential_savings / total_cost * 100) if total_cost > 0 else 0
        
        return CostOptimization(
            current_cost=total_cost,
            optimized_cost=optimized_cost,
            savings=potential_savings,
            savings_percentage=savings_percentage,
            recommendations=recommendations
        )
    
    def _analyze_monthly_trend(self, daily_costs: List[Dict]) -> Dict[str, Any]:
        """分析月度成本趋势"""
        if len(daily_costs) < 7:
            return {'trend': 'insufficient_data'}
        
        # 计算周平均成本
        weekly_costs = []
        for i in range(0, len(daily_costs), 7):
            week_data = daily_costs[i:i+7]
            week_cost = sum(day['total_cost'] for day in week_data)
            weekly_costs.append(week_cost)
        
        if len(weekly_costs) < 2:
            return {'trend': 'stable'}
        
        # 简单趋势分析
        first_half_avg = sum(weekly_costs[:len(weekly_costs)//2]) / (len(weekly_costs)//2)
        second_half_avg = sum(weekly_costs[len(weekly_costs)//2:]) / (len(weekly_costs) - len(weekly_costs)//2)
        
        trend_percentage = (second_half_avg - first_half_avg) / max(first_half_avg, 0.001) * 100
        
        if trend_percentage > 20:
            trend = 'increasing'
        elif trend_percentage < -20:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'trend_percentage': trend_percentage,
            'weekly_costs': weekly_costs,
            'first_half_avg': first_half_avg,
            'second_half_avg': second_half_avg
        }
    
    def _generate_monthly_optimization(self, service_costs: Dict, total_cost: float) -> List[str]:
        """生成月度优化建议"""
        recommendations = []
        
        if total_cost > 300:  # 月成本超过300元
            recommendations.append("🔴 月度成本较高，建议全面审查翻译策略和服务配置")
        elif total_cost > 100:
            recommendations.append("🟡 月度成本适中，可考虑进一步优化以降低成本")
        else:
            recommendations.append("✅ 月度成本控制良好")
        
        # 分析服务使用情况
        if service_costs:
            most_expensive_service = max(service_costs.items(), key=lambda x: x[1]['total_cost'])
            service_name, service_data = most_expensive_service
            
            if service_data['total_cost'] > total_cost * 0.5:
                recommendations.append(f"💰 {service_name}占月度成本{service_data['total_cost']/total_cost:.1%}，建议重点优化")
        
        return recommendations
    
    def _generate_comparison_recommendations(self, service_comparison: List[Dict]) -> List[str]:
        """生成服务比较建议"""
        recommendations = []
        
        if not service_comparison:
            return ["暂无足够数据进行服务比较"]
        
        best_service = service_comparison[0]
        worst_service = service_comparison[-1]
        
        recommendations.append(f"🏆 性价比最高: {best_service['service_name']} (评分: {best_service['value_score']:.1f})")
        
        if len(service_comparison) > 1:
            recommendations.append(f"📉 性价比最低: {worst_service['service_name']} (评分: {worst_service['value_score']:.1f})")
            
            # 成本差异分析
            cost_diff = worst_service['cost_per_request'] - best_service['cost_per_request']
            if cost_diff > 0.01:  # 如果成本差异超过0.01元
                potential_savings = cost_diff * worst_service['request_count']
                recommendations.append(f"💡 将{worst_service['service_name']}切换到{best_service['service_name']}可节省约¥{potential_savings:.2f}")
        
        # 质量vs成本建议
        high_quality_services = [s for s in service_comparison if s['avg_confidence'] > 0.9]
        if high_quality_services:
            cheapest_high_quality = min(high_quality_services, key=lambda x: x['cost_per_request'])
            recommendations.append(f"🎯 高质量低成本推荐: {cheapest_high_quality['service_name']}")
        
        return recommendations
    
    def generate_cost_report(self, days: int = 30) -> Dict[str, Any]:
        """生成综合成本报告"""
        print(f"📊 生成最近 {days} 天的成本分析报告...")
        
        # 获取每日成本数据
        daily_reports = []
        total_period_cost = 0
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily_report = self.analyze_daily_costs(date)
            daily_reports.append(daily_report)
            total_period_cost += daily_report['total_cost']
        
        # 服务比较
        service_comparison = self.compare_service_costs(days)
        
        # 生成综合建议
        comprehensive_recommendations = []
        
        avg_daily_cost = total_period_cost / days
        if avg_daily_cost > 10:
            comprehensive_recommendations.append("日均成本较高，建议实施成本控制措施")
        
        # 预测月度和年度成本
        projected_monthly = avg_daily_cost * 30
        projected_annual = avg_daily_cost * 365
        
        comprehensive_recommendations.extend([
            f"预计月度成本: ¥{projected_monthly:.2f}",
            f"预计年度成本: ¥{projected_annual:.2f}"
        ])
        
        return {
            'report_period': f"最近{days}天",
            'total_cost': total_period_cost,
            'avg_daily_cost': avg_daily_cost,
            'projected_monthly_cost': projected_monthly,
            'projected_annual_cost': projected_annual,
            'daily_breakdown': daily_reports[:7],  # 只返回最近7天详情
            'service_comparison': service_comparison,
            'comprehensive_recommendations': comprehensive_recommendations,
            'generated_at': datetime.now().isoformat()
        }

def analyze_costs():
    """成本分析的便捷函数"""
    analyzer = TranslationCostAnalyzer()
    
    # 今日成本分析
    today_costs = analyzer.analyze_daily_costs()
    print(f"今日成本: ¥{today_costs['total_cost']:.2f}")
    
    # 服务比较
    comparison = analyzer.compare_service_costs(days=7)
    if comparison['best_value_service']:
        print(f"最佳性价比服务: {comparison['best_value_service']}")
    
    # 综合报告
    comprehensive_report = analyzer.generate_cost_report(days=30)
    print(f"月度预计成本: ¥{comprehensive_report['projected_monthly_cost']:.2f}")
    
    return today_costs, comparison, comprehensive_report

if __name__ == "__main__":
    analyze_costs()