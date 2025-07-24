#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译质量监控系统
实现翻译服务的实时监控、报警和统计分析
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
import threading
from collections import defaultdict, deque

@dataclass
class TranslationMetrics:
    """翻译指标数据"""
    timestamp: str
    service_name: str
    operation_type: str  # translate_text, translate_batch, etc.
    success: bool
    response_time: float  # 响应时间(秒)
    input_length: int
    output_length: int
    confidence_score: float
    error_message: Optional[str] = None
    cost_estimate: float = 0.0  # 成本估算
    
@dataclass
class ServiceHealthStatus:
    """服务健康状态"""
    service_name: str
    is_healthy: bool
    last_check_time: str
    success_rate: float  # 最近1小时成功率
    avg_response_time: float  # 平均响应时间
    error_count: int  # 错误次数
    total_requests: int  # 总请求数
    last_error: Optional[str] = None

class TranslationMonitor:
    """翻译质量监控器"""
    
    def __init__(self, db_path: str = "translation/monitoring/translation_metrics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存，用于实时统计
        self.recent_metrics = deque(maxlen=1000)  # 最近1000条记录
        self.service_stats = defaultdict(lambda: {
            'success_count': 0,
            'error_count': 0,
            'total_response_time': 0.0,
            'last_success_time': None,
            'last_error_time': None,
            'last_error_message': None
        })
        
        # 报警配置
        self.alert_thresholds = {
            'error_rate_threshold': 0.1,  # 错误率超过10%报警
            'response_time_threshold': 5.0,  # 响应时间超过5秒报警
            'service_down_threshold': 300,  # 服务5分钟无响应报警
        }
        
        # 配置日志
        self._setup_logging()
        
        # 初始化数据库
        self._init_database()
        
        # 启动后台监控线程
        self._start_monitoring_thread()
    
    def _setup_logging(self):
        """配置监控日志"""
        log_dir = Path("translation/monitoring/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建专门的监控日志记录器
        self.logger = logging.getLogger('translation_monitor')
        self.logger.setLevel(logging.INFO)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            log_dir / f"monitor_{datetime.now().strftime('%Y%m%d')}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _init_database(self):
        """初始化监控数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS translation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    response_time REAL NOT NULL,
                    input_length INTEGER NOT NULL,
                    output_length INTEGER NOT NULL,
                    confidence_score REAL NOT NULL,
                    error_message TEXT,
                    cost_estimate REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS service_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建索引提高查询性能
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON translation_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_service ON translation_metrics(service_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_success ON translation_metrics(success)')
    
    def record_translation(self, metrics: TranslationMetrics):
        """记录翻译指标"""
        try:
            # 添加到内存缓存
            self.recent_metrics.append(metrics)
            
            # 更新服务统计
            service = metrics.service_name
            if metrics.success:
                self.service_stats[service]['success_count'] += 1
                self.service_stats[service]['last_success_time'] = metrics.timestamp
            else:
                self.service_stats[service]['error_count'] += 1
                self.service_stats[service]['last_error_time'] = metrics.timestamp
                self.service_stats[service]['last_error_message'] = metrics.error_message
            
            self.service_stats[service]['total_response_time'] += metrics.response_time
            
            # 保存到数据库
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO translation_metrics 
                    (timestamp, service_name, operation_type, success, response_time, 
                     input_length, output_length, confidence_score, error_message, cost_estimate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp, metrics.service_name, metrics.operation_type,
                    metrics.success, metrics.response_time, metrics.input_length,
                    metrics.output_length, metrics.confidence_score, 
                    metrics.error_message, metrics.cost_estimate
                ))
            
            # 检查是否需要报警
            self._check_alerts(metrics)
            
            self.logger.info(f"记录翻译指标: {metrics.service_name} - 成功: {metrics.success}")
            
        except Exception as e:
            self.logger.error(f"记录翻译指标失败: {str(e)}")
    
    def _check_alerts(self, metrics: TranslationMetrics):
        """检查报警条件"""
        service = metrics.service_name
        
        # 检查响应时间报警
        if metrics.response_time > self.alert_thresholds['response_time_threshold']:
            self._create_alert(
                service, 
                "high_response_time", 
                "WARNING",
                f"响应时间过长: {metrics.response_time:.2f}秒"
            )
        
        # 检查错误率报警
        if not metrics.success:
            recent_errors = self._get_recent_error_rate(service, minutes=10)
            if recent_errors > self.alert_thresholds['error_rate_threshold']:
                self._create_alert(
                    service,
                    "high_error_rate",
                    "CRITICAL", 
                    f"错误率过高: {recent_errors:.2%} (最近10分钟)"
                )
    
    def _create_alert(self, service_name: str, alert_type: str, severity: str, message: str):
        """创建报警记录"""
        try:
            timestamp = datetime.now().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO service_alerts 
                    (timestamp, service_name, alert_type, severity, message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (timestamp, service_name, alert_type, severity, message))
            
            # 记录到日志
            log_level = logging.CRITICAL if severity == "CRITICAL" else logging.WARNING
            self.logger.log(log_level, f"报警: {service_name} - {alert_type} - {message}")
            
        except Exception as e:
            self.logger.error(f"创建报警失败: {str(e)}")
    
    def get_service_health(self, service_name: str) -> ServiceHealthStatus:
        """获取服务健康状态"""
        stats = self.service_stats[service_name]
        
        total_requests = stats['success_count'] + stats['error_count']
        success_rate = stats['success_count'] / max(total_requests, 1)
        avg_response_time = stats['total_response_time'] / max(total_requests, 1)
        
        # 检查服务是否健康
        is_healthy = (
            success_rate >= (1 - self.alert_thresholds['error_rate_threshold']) and
            avg_response_time <= self.alert_thresholds['response_time_threshold'] and
            self._is_service_responsive(service_name)
        )
        
        return ServiceHealthStatus(
            service_name=service_name,
            is_healthy=is_healthy,
            last_check_time=datetime.now().isoformat(),
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            error_count=stats['error_count'],
            total_requests=total_requests,
            last_error=stats['last_error_message']
        )
    
    def _is_service_responsive(self, service_name: str) -> bool:
        """检查服务是否响应"""
        stats = self.service_stats[service_name]
        last_success = stats['last_success_time']
        
        if not last_success:
            return False
        
        try:
            last_time = datetime.fromisoformat(last_success)
            now = datetime.now()
            time_diff = (now - last_time).total_seconds()
            
            return time_diff <= self.alert_thresholds['service_down_threshold']
        except:
            return False
    
    def _get_recent_error_rate(self, service_name: str, minutes: int = 60) -> float:
        """获取最近指定时间内的错误率"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        recent_metrics = [
            m for m in self.recent_metrics 
            if (m.service_name == service_name and 
                datetime.fromisoformat(m.timestamp) >= cutoff_time)
        ]
        
        if not recent_metrics:
            return 0.0
        
        error_count = sum(1 for m in recent_metrics if not m.success)
        return error_count / len(recent_metrics)
    
    def get_daily_statistics(self, date: str = None) -> Dict[str, Any]:
        """获取每日统计数据"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 基础统计
                cursor.execute('''
                    SELECT 
                        service_name,
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                        AVG(response_time) as avg_response_time,
                        AVG(confidence_score) as avg_confidence,
                        SUM(cost_estimate) as total_cost
                    FROM translation_metrics 
                    WHERE DATE(timestamp) = ?
                    GROUP BY service_name
                ''', (date,))
                
                service_stats = {}
                for row in cursor.fetchall():
                    service_name, total, success, avg_time, avg_conf, cost = row
                    service_stats[service_name] = {
                        'total_requests': total,
                        'success_count': success,
                        'error_count': total - success,
                        'success_rate': success / total if total > 0 else 0,
                        'avg_response_time': avg_time or 0,
                        'avg_confidence': avg_conf or 0,
                        'total_cost': cost or 0
                    }
                
                # 整体统计
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_requests,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                        AVG(response_time) as avg_response_time,
                        SUM(cost_estimate) as total_cost
                    FROM translation_metrics 
                    WHERE DATE(timestamp) = ?
                ''', (date,))
                
                overall = cursor.fetchone()
                total_requests, success_count, avg_response_time, total_cost = overall
                
                return {
                    'date': date,
                    'overall': {
                        'total_requests': total_requests or 0,
                        'success_count': success_count or 0,
                        'error_count': (total_requests or 0) - (success_count or 0),
                        'success_rate': (success_count or 0) / max(total_requests or 1, 1),
                        'avg_response_time': avg_response_time or 0,
                        'total_cost': total_cost or 0
                    },
                    'by_service': service_stats
                }
                
        except Exception as e:
            self.logger.error(f"获取每日统计失败: {str(e)}")
            return {'date': date, 'overall': {}, 'by_service': {}}
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取最近的报警记录"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, service_name, alert_type, severity, message, resolved
                    FROM service_alerts 
                    WHERE datetime(timestamp) >= datetime(?)
                    ORDER BY timestamp DESC
                ''', (cutoff_time.isoformat(),))
                
                alerts = []
                for row in cursor.fetchall():
                    timestamp, service, alert_type, severity, message, resolved = row
                    alerts.append({
                        'timestamp': timestamp,
                        'service_name': service,
                        'alert_type': alert_type,
                        'severity': severity,
                        'message': message,
                        'resolved': bool(resolved)
                    })
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"获取报警记录失败: {str(e)}")
            return []
    
    def _start_monitoring_thread(self):
        """启动后台监控线程"""
        def monitor_loop():
            while True:
                try:
                    # 每分钟检查一次服务健康状态
                    self._periodic_health_check()
                    time.sleep(60)
                except Exception as e:
                    self.logger.error(f"监控线程异常: {str(e)}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        self.logger.info("后台监控线程已启动")
    
    def _periodic_health_check(self):
        """定期健康检查"""
        for service_name in self.service_stats.keys():
            health = self.get_service_health(service_name)
            
            if not health.is_healthy:
                # 检查是否需要创建服务不健康报警
                if health.success_rate < (1 - self.alert_thresholds['error_rate_threshold']):
                    self._create_alert(
                        service_name,
                        "service_unhealthy",
                        "CRITICAL",
                        f"服务不健康: 成功率 {health.success_rate:.2%}"
                    )
    
    def generate_quality_report(self, days: int = 7) -> Dict[str, Any]:
        """生成翻译质量报告"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 质量趋势分析
                cursor.execute('''
                    SELECT 
                        DATE(timestamp) as date,
                        service_name,
                        AVG(confidence_score) as avg_confidence,
                        COUNT(*) as request_count,
                        SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count
                    FROM translation_metrics 
                    WHERE datetime(timestamp) BETWEEN datetime(?) AND datetime(?)
                    GROUP BY DATE(timestamp), service_name
                    ORDER BY date DESC
                ''', (start_date.isoformat(), end_date.isoformat()))
                
                quality_trends = defaultdict(list)
                for row in cursor.fetchall():
                    date, service, avg_conf, count, success = row
                    quality_trends[service].append({
                        'date': date,
                        'avg_confidence': avg_conf or 0,
                        'request_count': count,
                        'success_rate': success / count if count > 0 else 0
                    })
                
                # 生成改进建议
                recommendations = self._generate_recommendations(quality_trends)
                
                return {
                    'report_period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
                    'quality_trends': dict(quality_trends),
                    'recommendations': recommendations,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"生成质量报告失败: {str(e)}")
            return {}
    
    def _generate_recommendations(self, quality_trends: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        for service, trends in quality_trends.items():
            if not trends:
                continue
            
            # 计算平均置信度
            avg_confidence = sum(t['avg_confidence'] for t in trends) / len(trends)
            avg_success_rate = sum(t['success_rate'] for t in trends) / len(trends)
            
            if avg_confidence < 0.8:
                recommendations.append(
                    f"{service}: 翻译置信度偏低({avg_confidence:.2%})，建议优化提示词或切换到更高质量的模型"
                )
            
            if avg_success_rate < 0.95:
                recommendations.append(
                    f"{service}: 成功率偏低({avg_success_rate:.2%})，建议检查API配置和网络连接"
                )
            
            # 检查趋势
            if len(trends) >= 3:
                recent_conf = sum(t['avg_confidence'] for t in trends[:3]) / 3
                older_conf = sum(t['avg_confidence'] for t in trends[-3:]) / 3
                
                if recent_conf < older_conf - 0.05:
                    recommendations.append(
                        f"{service}: 翻译质量呈下降趋势，建议检查服务状态和配置"
                    )
        
        if not recommendations:
            recommendations.append("翻译服务运行良好，质量指标正常")
        
        return recommendations

# 全局监控实例
_monitor_instance = None

def get_monitor() -> TranslationMonitor:
    """获取全局监控实例"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = TranslationMonitor()
    return _monitor_instance

def record_translation_metrics(
    service_name: str,
    operation_type: str,
    success: bool,
    response_time: float,
    input_length: int,
    output_length: int,
    confidence_score: float,
    error_message: str = None,
    cost_estimate: float = 0.0
):
    """便捷函数：记录翻译指标"""
    metrics = TranslationMetrics(
        timestamp=datetime.now().isoformat(),
        service_name=service_name,
        operation_type=operation_type,
        success=success,
        response_time=response_time,
        input_length=input_length,
        output_length=output_length,
        confidence_score=confidence_score,
        error_message=error_message,
        cost_estimate=cost_estimate
    )
    
    monitor = get_monitor()
    monitor.record_translation(metrics)