"""
动态配置管理器 - 支持翻译服务的实时配置管理

功能特性:
- API密钥的安全管理和轮换
- 翻译服务优先级动态调整
- 成本控制和预算管理
- 翻译质量阈值配置
- 负载均衡策略管理
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import logging

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """翻译服务配置"""
    name: str
    api_keys: List[str]  # 支持多个API密钥轮换
    priority: int  # 优先级，数字越小优先级越高
    enabled: bool
    cost_per_char: float  # 每字符成本
    quality_threshold: float  # 质量阈值
    max_requests_per_minute: int  # 每分钟最大请求数
    timeout_seconds: int
    retry_count: int
    current_key_index: int = 0  # 当前使用的密钥索引
    
@dataclass
class CostControl:
    """成本控制配置"""
    daily_budget: float  # 每日预算
    monthly_budget: float  # 每月预算
    current_daily_cost: float = 0.0
    current_monthly_cost: float = 0.0
    cost_alert_threshold: float = 0.8  # 成本警告阈值(80%)
    auto_disable_on_budget_exceeded: bool = True
    
@dataclass
class QualityConfig:
    """翻译质量配置"""
    min_confidence_score: float = 0.7
    enable_quality_comparison: bool = True
    fallback_on_low_quality: bool = True
    quality_improvement_threshold: float = 0.1  # 质量提升阈值
    
class DynamicConfigManager:
    """动态配置管理器"""
    
    def __init__(self, config_file: str = "translation/config/dynamic_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置数据
        self.services: Dict[str, ServiceConfig] = {}
        self.cost_control = CostControl(daily_budget=100.0, monthly_budget=2000.0)
        self.quality_config = QualityConfig()
        
        # 运行时状态
        self._lock = threading.RLock()
        self._config_watchers: List[Callable] = []
        self._last_modified = 0
        self._cost_tracking: Dict[str, List[tuple]] = {}  # 成本追踪记录
        
        # 初始化配置
        self._load_config()
        self._start_config_watcher()
        
    def _load_config(self):
        """加载配置文件"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 加载服务配置
                for name, config_data in data.get('services', {}).items():
                    self.services[name] = ServiceConfig(**config_data)
                    
                # 加载成本控制配置
                if 'cost_control' in data:
                    self.cost_control = CostControl(**data['cost_control'])
                    
                # 加载质量配置
                if 'quality_config' in data:
                    self.quality_config = QualityConfig(**data['quality_config'])
                    
                logger.info(f"配置已加载: {len(self.services)} 个翻译服务")
            else:
                # 创建默认配置
                self._create_default_config()
                
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            self._create_default_config()
            
    def _create_default_config(self):
        """创建默认配置"""
        self.services = {
            'siliconflow': ServiceConfig(
                name='siliconflow',
                api_keys=['your_siliconflow_api_key'],
                priority=1,
                enabled=True,
                cost_per_char=0.00001,  # 极低成本
                quality_threshold=0.85,
                max_requests_per_minute=60,
                timeout_seconds=30,
                retry_count=3
            ),
            'baidu': ServiceConfig(
                name='baidu',
                api_keys=['your_baidu_api_key'],
                priority=2,
                enabled=True,
                cost_per_char=0.0001,
                quality_threshold=0.8,
                max_requests_per_minute=100,
                timeout_seconds=15,
                retry_count=2
            ),
            'tencent': ServiceConfig(
                name='tencent',
                api_keys=['your_tencent_api_key'],
                priority=3,
                enabled=True,
                cost_per_char=0.0001,
                quality_threshold=0.8,
                max_requests_per_minute=100,
                timeout_seconds=15,
                retry_count=2
            ),
            'google': ServiceConfig(
                name='google',
                api_keys=['your_google_api_key'],
                priority=4,
                enabled=False,  # 默认禁用，因为网络限制
                cost_per_char=0.0002,
                quality_threshold=0.9,
                max_requests_per_minute=50,
                timeout_seconds=20,
                retry_count=2
            )
        }
        
        self.cost_control = CostControl(
            daily_budget=50.0,
            monthly_budget=1000.0,
            cost_alert_threshold=0.8,
            auto_disable_on_budget_exceeded=True
        )
        
        self.quality_config = QualityConfig(
            min_confidence_score=0.7,
            enable_quality_comparison=True,
            fallback_on_low_quality=True,
            quality_improvement_threshold=0.1
        )
        
        self._save_config()
        
    def _save_config(self):
        """保存配置到文件"""
        try:
            with self._lock:
                config_data = {
                    'services': {name: asdict(config) for name, config in self.services.items()},
                    'cost_control': asdict(self.cost_control),
                    'quality_config': asdict(self.quality_config),
                    'last_updated': datetime.now().isoformat()
                }
                
                # 确保目录存在
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 使用临时文件写入，然后重命名，确保原子性
                temp_file = self.config_file.with_suffix('.tmp')
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                
                # 原子性重命名
                temp_file.replace(self.config_file)
                    
                logger.info("配置已保存")
                
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            
    def get_service_config(self, service_name: str) -> Optional[ServiceConfig]:
        """获取服务配置"""
        with self._lock:
            return self.services.get(service_name)
            
    def update_service_config(self, service_name: str, **kwargs):
        """更新服务配置"""
        with self._lock:
            if service_name in self.services:
                config = self.services[service_name]
                for key, value in kwargs.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
                        
                self._save_config()
                self._notify_watchers('service_updated', service_name, kwargs)
                logger.info(f"服务 {service_name} 配置已更新: {kwargs}")
                
    def get_active_api_key(self, service_name: str) -> Optional[str]:
        """获取当前活跃的API密钥"""
        with self._lock:
            config = self.services.get(service_name)
            if config and config.api_keys:
                return config.api_keys[config.current_key_index]
            return None
            
    def rotate_api_key(self, service_name: str) -> bool:
        """轮换API密钥"""
        with self._lock:
            config = self.services.get(service_name)
            if config and len(config.api_keys) > 1:
                config.current_key_index = (config.current_key_index + 1) % len(config.api_keys)
                self._save_config()
                logger.info(f"服务 {service_name} API密钥已轮换到索引 {config.current_key_index}")
                return True
            return False
            
    def add_api_key(self, service_name: str, api_key: str) -> bool:
        """添加新的API密钥"""
        with self._lock:
            config = self.services.get(service_name)
            if config and api_key not in config.api_keys:
                config.api_keys.append(api_key)
                self._save_config()
                logger.info(f"为服务 {service_name} 添加了新的API密钥")
                return True
            return False
            
    def remove_api_key(self, service_name: str, api_key: str) -> bool:
        """移除API密钥"""
        with self._lock:
            config = self.services.get(service_name)
            if config and api_key in config.api_keys and len(config.api_keys) > 1:
                # 调整当前索引
                if config.current_key_index >= config.api_keys.index(api_key):
                    config.current_key_index = max(0, config.current_key_index - 1)
                    
                config.api_keys.remove(api_key)
                self._save_config()
                logger.info(f"从服务 {service_name} 移除了API密钥")
                return True
            return False
            
    def get_services_by_priority(self) -> List[ServiceConfig]:
        """按优先级获取启用的服务列表"""
        with self._lock:
            enabled_services = [config for config in self.services.values() if config.enabled]
            return sorted(enabled_services, key=lambda x: x.priority)
            
    def update_service_priority(self, service_name: str, new_priority: int):
        """更新服务优先级"""
        with self._lock:
            if service_name in self.services:
                old_priority = self.services[service_name].priority
                self.services[service_name].priority = new_priority
                self._save_config()
                logger.info(f"服务 {service_name} 优先级从 {old_priority} 更新为 {new_priority}")
                
    def enable_service(self, service_name: str):
        """启用服务"""
        self.update_service_config(service_name, enabled=True)
        
    def disable_service(self, service_name: str):
        """禁用服务"""
        self.update_service_config(service_name, enabled=False)
        
    def record_translation_cost(self, service_name: str, char_count: int, cost: float):
        """记录翻译成本"""
        with self._lock:
            now = datetime.now()
            
            # 记录成本
            if service_name not in self._cost_tracking:
                self._cost_tracking[service_name] = []
                
            self._cost_tracking[service_name].append((now, char_count, cost))
            
            # 更新当日和当月成本
            today = now.date()
            this_month = (now.year, now.month)
            
            # 计算所有服务的总成本
            total_daily_cost = 0
            total_monthly_cost = 0
            
            for svc_name, records in self._cost_tracking.items():
                daily_cost = sum(c for dt, _, c in records if dt.date() == today)
                monthly_cost = sum(c for dt, _, c in records if (dt.year, dt.month) == this_month)
                total_daily_cost += daily_cost
                total_monthly_cost += monthly_cost
            
            self.cost_control.current_daily_cost = total_daily_cost
            self.cost_control.current_monthly_cost = total_monthly_cost
            
            # 检查预算限制
            self._check_budget_limits()
            
            logger.debug(f"记录翻译成本: {service_name}, {char_count}字符, ¥{cost:.4f}")
            
    def _check_budget_limits(self):
        """检查预算限制"""
        daily_usage = self.cost_control.current_daily_cost / self.cost_control.daily_budget
        monthly_usage = self.cost_control.current_monthly_cost / self.cost_control.monthly_budget
        
        # 预算警告
        if daily_usage >= self.cost_control.cost_alert_threshold:
            logger.warning(f"每日预算使用率达到 {daily_usage:.1%}")
            
        if monthly_usage >= self.cost_control.cost_alert_threshold:
            logger.warning(f"每月预算使用率达到 {monthly_usage:.1%}")
            
        # 自动禁用服务
        if self.cost_control.auto_disable_on_budget_exceeded:
            if daily_usage >= 1.0 or monthly_usage >= 1.0:
                logger.error("预算超限，自动禁用所有翻译服务")
                for service_name in self.services:
                    self.disable_service(service_name)
                    
    def get_cost_statistics(self) -> Dict[str, Any]:
        """获取成本统计信息"""
        with self._lock:
            now = datetime.now()
            today = now.date()
            this_month = (now.year, now.month)
            
            stats = {
                'daily_budget': self.cost_control.daily_budget,
                'monthly_budget': self.cost_control.monthly_budget,
                'current_daily_cost': self.cost_control.current_daily_cost,
                'current_monthly_cost': self.cost_control.current_monthly_cost,
                'daily_usage_rate': self.cost_control.current_daily_cost / self.cost_control.daily_budget,
                'monthly_usage_rate': self.cost_control.current_monthly_cost / self.cost_control.monthly_budget,
                'services': {}
            }
            
            # 各服务成本统计
            for service_name, records in self._cost_tracking.items():
                daily_records = [r for r in records if r[0].date() == today]
                monthly_records = [r for r in records if (r[0].year, r[0].month) == this_month]
                
                stats['services'][service_name] = {
                    'daily_cost': sum(r[2] for r in daily_records),
                    'monthly_cost': sum(r[2] for r in monthly_records),
                    'daily_chars': sum(r[1] for r in daily_records),
                    'monthly_chars': sum(r[1] for r in monthly_records),
                    'daily_requests': len(daily_records),
                    'monthly_requests': len(monthly_records)
                }
                
            return stats
            
    def update_cost_control(self, **kwargs):
        """更新成本控制配置"""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self.cost_control, key):
                    setattr(self.cost_control, key, value)
                    
            self._save_config()
            logger.info(f"成本控制配置已更新: {kwargs}")
            
    def update_quality_config(self, **kwargs):
        """更新质量配置"""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self.quality_config, key):
                    setattr(self.quality_config, key, value)
                    
            self._save_config()
            logger.info(f"质量配置已更新: {kwargs}")
            
    def get_quality_config(self) -> QualityConfig:
        """获取质量配置"""
        return self.quality_config
        
    def should_use_service(self, service_name: str, estimated_chars: int = 0) -> bool:
        """判断是否应该使用指定服务"""
        with self._lock:
            config = self.services.get(service_name)
            if not config or not config.enabled:
                return False
                
            # 检查预算限制
            if estimated_chars > 0:
                estimated_cost = estimated_chars * config.cost_per_char
                
                if (self.cost_control.current_daily_cost + estimated_cost > 
                    self.cost_control.daily_budget):
                    return False
                    
                if (self.cost_control.current_monthly_cost + estimated_cost > 
                    self.cost_control.monthly_budget):
                    return False
                    
            return True
            
    def add_config_watcher(self, callback: Callable):
        """添加配置变更监听器"""
        self._config_watchers.append(callback)
        
    def _notify_watchers(self, event_type: str, *args):
        """通知配置变更监听器"""
        for callback in self._config_watchers:
            try:
                callback(event_type, *args)
            except Exception as e:
                logger.error(f"配置监听器回调失败: {e}")
                
    def _start_config_watcher(self):
        """启动配置文件监控"""
        def watch_config():
            while True:
                try:
                    if self.config_file.exists():
                        current_modified = self.config_file.stat().st_mtime
                        if current_modified > self._last_modified:
                            self._last_modified = current_modified
                            self._load_config()
                            self._notify_watchers('config_reloaded')
                            
                    time.sleep(5)  # 每5秒检查一次
                    
                except Exception as e:
                    logger.error(f"配置文件监控错误: {e}")
                    time.sleep(10)
                    
        thread = threading.Thread(target=watch_config, daemon=True)
        thread.start()
        
    def export_config(self) -> Dict[str, Any]:
        """导出完整配置"""
        with self._lock:
            return {
                'services': {name: asdict(config) for name, config in self.services.items()},
                'cost_control': asdict(self.cost_control),
                'quality_config': asdict(self.quality_config),
                'cost_statistics': self.get_cost_statistics()
            }
            
    def import_config(self, config_data: Dict[str, Any]):
        """导入配置"""
        with self._lock:
            try:
                # 导入服务配置
                if 'services' in config_data:
                    for name, service_data in config_data['services'].items():
                        self.services[name] = ServiceConfig(**service_data)
                        
                # 导入成本控制配置
                if 'cost_control' in config_data:
                    self.cost_control = CostControl(**config_data['cost_control'])
                    
                # 导入质量配置
                if 'quality_config' in config_data:
                    self.quality_config = QualityConfig(**config_data['quality_config'])
                    
                self._save_config()
                self._notify_watchers('config_imported')
                logger.info("配置导入成功")
                
            except Exception as e:
                logger.error(f"配置导入失败: {e}")
                raise