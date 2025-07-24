#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译服务健康监控系统
实现实时健康检查、状态监控和自动恢复机制
"""

import time
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed

from .interfaces import ITranslationService, ServiceStatus, TranslationResult


class HealthStatus(Enum):
    """健康状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealthInfo:
    """服务健康信息"""
    service_name: str
    status: HealthStatus
    last_check_time: datetime
    response_time: float
    error_count: int = 0
    success_count: int = 0
    consecutive_failures: int = 0
    last_error: Optional[str] = None
    uptime_percentage: float = 100.0
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        total = self.success_count + self.error_count
        return (self.success_count / total * 100) if total > 0 else 0.0


@dataclass
class HealthCheckConfig:
    """健康检查配置"""
    check_interval: int = 60  # 检查间隔（秒）
    timeout: int = 10  # 超时时间（秒）
    max_consecutive_failures: int = 3  # 最大连续失败次数
    degraded_threshold: float = 5.0  # 降级阈值（响应时间秒）
    unhealthy_threshold: int = 5  # 不健康阈值（连续失败次数）
    test_text: str = "Hello world"  # 测试文本
    enable_auto_recovery: bool = True  # 启用自动恢复
    recovery_check_interval: int = 300  # 恢复检查间隔（秒）


class ServiceHealthMonitor:
    """服务健康监控器"""
    
    def __init__(self, services: List[ITranslationService], config: Optional[HealthCheckConfig] = None):
        """
        初始化健康监控器
        
        Args:
            services: 翻译服务列表
            config: 健康检查配置
        """
        self.services = {service.get_service_name(): service for service in services}
        self.config = config or HealthCheckConfig()
        self.logger = logging.getLogger(__name__)
        
        # 健康状态信息
        self.health_info: Dict[str, ServiceHealthInfo] = {}
        self._initialize_health_info()
        
        # 监控控制
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        
        # 回调函数
        self._status_change_callbacks: List[Callable[[str, HealthStatus, HealthStatus], None]] = []
        
        # 统计信息
        self.monitoring_stats = {
            'total_checks': 0,
            'total_failures': 0,
            'start_time': datetime.now()
        }
    
    def _initialize_health_info(self):
        """初始化健康信息"""
        for service_name in self.services.keys():
            self.health_info[service_name] = ServiceHealthInfo(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                last_check_time=datetime.now(),
                response_time=0.0
            )
    
    def start_monitoring(self):
        """开始健康监控"""
        if self._monitoring:
            self.logger.warning("健康监控已经在运行")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("健康监控已启动")
    
    def stop_monitoring(self):
        """停止健康监控"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        self.logger.info("健康监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self._monitoring:
            try:
                self._perform_health_checks()
                time.sleep(self.config.check_interval)
            except Exception as e:
                self.logger.error(f"健康检查循环出错: {e}")
                time.sleep(self.config.check_interval)
    
    def _perform_health_checks(self):
        """执行健康检查"""
        self.monitoring_stats['total_checks'] += 1
        
        # 使用线程池并行检查所有服务
        with ThreadPoolExecutor(max_workers=len(self.services)) as executor:
            future_to_service = {
                executor.submit(self._check_service_health, service_name, service): service_name
                for service_name, service in self.services.items()
            }
            
            for future in as_completed(future_to_service):
                service_name = future_to_service[future]
                try:
                    health_info = future.result(timeout=self.config.timeout + 5)
                    self._update_health_info(service_name, health_info)
                except Exception as e:
                    self.logger.error(f"检查服务 {service_name} 健康状态失败: {e}")
                    self._handle_check_failure(service_name, str(e))
    
    def _check_service_health(self, service_name: str, service: ITranslationService) -> ServiceHealthInfo:
        """
        检查单个服务的健康状态
        
        Args:
            service_name: 服务名称
            service: 服务实例
            
        Returns:
            ServiceHealthInfo: 健康信息
        """
        start_time = time.time()
        
        try:
            # 执行测试翻译
            result = service.translate_text(
                self.config.test_text,
                source_lang='en',
                target_lang='zh'
            )
            
            response_time = time.time() - start_time
            
            # 检查翻译结果
            if result.error_message:
                raise Exception(f"翻译失败: {result.error_message}")
            
            if not result.translated_text or result.translated_text == self.config.test_text:
                raise Exception("翻译结果无效")
            
            # 确定健康状态
            if response_time > self.config.degraded_threshold:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.HEALTHY
            
            # 更新健康信息
            current_info = self.health_info[service_name]
            return ServiceHealthInfo(
                service_name=service_name,
                status=status,
                last_check_time=datetime.now(),
                response_time=response_time,
                error_count=current_info.error_count,
                success_count=current_info.success_count + 1,
                consecutive_failures=0,  # 重置连续失败计数
                uptime_percentage=self._calculate_uptime(service_name)
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            current_info = self.health_info[service_name]
            consecutive_failures = current_info.consecutive_failures + 1
            
            # 确定健康状态
            if consecutive_failures >= self.config.unhealthy_threshold:
                status = HealthStatus.UNHEALTHY
            else:
                status = HealthStatus.DEGRADED
            
            return ServiceHealthInfo(
                service_name=service_name,
                status=status,
                last_check_time=datetime.now(),
                response_time=response_time,
                error_count=current_info.error_count + 1,
                success_count=current_info.success_count,
                consecutive_failures=consecutive_failures,
                last_error=str(e),
                uptime_percentage=self._calculate_uptime(service_name)
            ) 
   
    def _update_health_info(self, service_name: str, new_info: ServiceHealthInfo):
        """更新健康信息"""
        with self._lock:
            old_status = self.health_info[service_name].status
            self.health_info[service_name] = new_info
            
            # 如果状态发生变化，触发回调
            if old_status != new_info.status:
                self._notify_status_change(service_name, old_status, new_info.status)
    
    def _handle_check_failure(self, service_name: str, error: str):
        """处理检查失败"""
        with self._lock:
            current_info = self.health_info[service_name]
            consecutive_failures = current_info.consecutive_failures + 1
            
            # 更新失败信息
            updated_info = ServiceHealthInfo(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY if consecutive_failures >= self.config.unhealthy_threshold else HealthStatus.DEGRADED,
                last_check_time=datetime.now(),
                response_time=self.config.timeout,
                error_count=current_info.error_count + 1,
                success_count=current_info.success_count,
                consecutive_failures=consecutive_failures,
                last_error=error,
                uptime_percentage=self._calculate_uptime(service_name)
            )
            
            old_status = current_info.status
            self.health_info[service_name] = updated_info
            
            # 触发状态变化回调
            if old_status != updated_info.status:
                self._notify_status_change(service_name, old_status, updated_info.status)
            
            self.monitoring_stats['total_failures'] += 1
    
    def _calculate_uptime(self, service_name: str) -> float:
        """计算服务正常运行时间百分比"""
        current_info = self.health_info[service_name]
        total_checks = current_info.success_count + current_info.error_count
        
        if total_checks == 0:
            return 100.0
        
        return (current_info.success_count / total_checks) * 100
    
    def _notify_status_change(self, service_name: str, old_status: HealthStatus, new_status: HealthStatus):
        """通知状态变化"""
        self.logger.info(f"服务 {service_name} 状态变化: {old_status.value} -> {new_status.value}")
        
        for callback in self._status_change_callbacks:
            try:
                callback(service_name, old_status, new_status)
            except Exception as e:
                self.logger.error(f"状态变化回调执行失败: {e}")
    
    def add_status_change_callback(self, callback: Callable[[str, HealthStatus, HealthStatus], None]):
        """添加状态变化回调"""
        self._status_change_callbacks.append(callback)
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealthInfo]:
        """获取服务健康信息"""
        return self.health_info.get(service_name)
    
    def get_all_health_info(self) -> Dict[str, ServiceHealthInfo]:
        """获取所有服务健康信息"""
        with self._lock:
            return self.health_info.copy()
    
    def get_healthy_services(self) -> List[str]:
        """获取健康的服务列表"""
        return [
            name for name, info in self.health_info.items()
            if info.status == HealthStatus.HEALTHY
        ]
    
    def get_available_services(self) -> List[str]:
        """获取可用的服务列表（健康或降级）"""
        return [
            name for name, info in self.health_info.items()
            if info.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
        ]
    
    def get_unhealthy_services(self) -> List[str]:
        """获取不健康的服务列表"""
        return [
            name for name, info in self.health_info.items()
            if info.status == HealthStatus.UNHEALTHY
        ]
    
    def force_health_check(self, service_name: Optional[str] = None):
        """强制执行健康检查"""
        if service_name:
            if service_name in self.services:
                service = self.services[service_name]
                health_info = self._check_service_health(service_name, service)
                self._update_health_info(service_name, health_info)
            else:
                raise ValueError(f"未知服务: {service_name}")
        else:
            self._perform_health_checks()
    
    def get_monitoring_statistics(self) -> Dict:
        """获取监控统计信息"""
        uptime = datetime.now() - self.monitoring_stats['start_time']
        
        return {
            'monitoring_uptime': str(uptime),
            'total_checks': self.monitoring_stats['total_checks'],
            'total_failures': self.monitoring_stats['total_failures'],
            'failure_rate': (self.monitoring_stats['total_failures'] / max(1, self.monitoring_stats['total_checks'])) * 100,
            'services_count': len(self.services),
            'healthy_services': len(self.get_healthy_services()),
            'available_services': len(self.get_available_services()),
            'unhealthy_services': len(self.get_unhealthy_services())
        }
    
    def get_service_summary(self) -> Dict[str, Dict]:
        """获取服务摘要信息"""
        summary = {}
        
        for service_name, health_info in self.health_info.items():
            summary[service_name] = {
                'status': health_info.status.value,
                'last_check': health_info.last_check_time.isoformat(),
                'response_time': health_info.response_time,
                'success_rate': health_info.get_success_rate(),
                'uptime_percentage': health_info.uptime_percentage,
                'consecutive_failures': health_info.consecutive_failures,
                'last_error': health_info.last_error
            }
        
        return summary