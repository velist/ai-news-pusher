"""
托管翻译服务 - 集成动态配置管理的智能翻译服务

功能特性:
- 基于动态配置的服务选择和负载均衡
- 实时成本监控和预算控制
- API密钥自动轮换和故障转移
- 翻译质量评估和服务优化
- Web界面配置管理
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..core.interfaces import ITranslationService, TranslationResult
from ..core.dynamic_config_manager import DynamicConfigManager, ServiceConfig
from ..core.config_web_interface import ConfigWebServer
from ..services.siliconflow_translator import SiliconFlowTranslator
from ..services.baidu_translator import BaiduTranslator
from ..services.tencent_translator import TencentTranslator
from ..services.google_translator import GoogleTranslator
from ..services.rule_based_translator import RuleBasedTranslator

logger = logging.getLogger(__name__)

class ManagedTranslationService(ITranslationService):
    """托管翻译服务 - 具备动态配置管理能力的翻译服务"""
    
    def __init__(self, config_file: str = "translation/config/dynamic_config.json", 
                 enable_web_interface: bool = True, web_port: int = 8080):
        """
        初始化托管翻译服务
        
        Args:
            config_file: 配置文件路径
            enable_web_interface: 是否启用Web配置界面
            web_port: Web界面端口
        """
        # 初始化配置管理器
        self.config_manager = DynamicConfigManager(config_file)
        
        # 翻译服务实例缓存
        self._service_instances: Dict[str, ITranslationService] = {}
        
        # 服务统计信息
        self._service_stats: Dict[str, Dict[str, Any]] = {}
        
        # Web配置界面
        self.web_server = None
        if enable_web_interface:
            self.web_server = ConfigWebServer(self.config_manager, port=web_port)
            self.web_server.start()
            
        # 注册配置变更监听器
        self.config_manager.add_config_watcher(self._on_config_changed)
        
        # 初始化翻译服务
        self._initialize_services()
        
        logger.info(f"托管翻译服务已初始化，Web界面: {self.web_server.get_url() if self.web_server else '未启用'}")
        
    def _initialize_services(self):
        """初始化翻译服务实例"""
        try:
            # 获取所有服务配置
            services = self.config_manager.get_services_by_priority()
            
            for service_config in services:
                if service_config.enabled:
                    self._create_service_instance(service_config)
                    
            logger.info(f"已初始化 {len(self._service_instances)} 个翻译服务")
            
        except Exception as e:
            logger.error(f"初始化翻译服务失败: {e}")
            
    def _create_service_instance(self, config: ServiceConfig) -> Optional[ITranslationService]:
        """创建翻译服务实例"""
        try:
            api_key = self.config_manager.get_active_api_key(config.name)
            if not api_key:
                logger.warning(f"服务 {config.name} 没有可用的API密钥")
                return None
                
            # 根据服务名称创建对应的翻译器实例
            if config.name == 'siliconflow':
                service = SiliconFlowTranslator(api_key=api_key)
            elif config.name == 'baidu':
                service = BaiduTranslator(api_key=api_key)
            elif config.name == 'tencent':
                service = TencentTranslator(api_key=api_key)
            elif config.name == 'google':
                service = GoogleTranslator(api_key=api_key)
            else:
                logger.warning(f"未知的翻译服务类型: {config.name}")
                return None
                
            # 应用配置参数
            if hasattr(service, 'set_timeout'):
                service.set_timeout(config.timeout_seconds)
            if hasattr(service, 'set_retry_count'):
                service.set_retry_count(config.retry_count)
                
            self._service_instances[config.name] = service
            self._service_stats[config.name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'total_chars': 0,
                'total_cost': 0.0,
                'avg_response_time': 0.0,
                'last_used': None
            }
            
            logger.info(f"翻译服务 {config.name} 实例创建成功")
            return service
            
        except Exception as e:
            logger.error(f"创建翻译服务 {config.name} 实例失败: {e}")
            return None
            
    def _on_config_changed(self, event_type: str, *args):
        """配置变更回调"""
        logger.info(f"配置变更事件: {event_type}")
        
        if event_type in ['config_reloaded', 'service_updated']:
            # 重新初始化服务
            self._initialize_services()
            
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'zh') -> TranslationResult:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            TranslationResult: 翻译结果
        """
        if not text or not text.strip():
            return TranslationResult(
                original_text=text,
                translated_text=text,
                source_language=source_lang,
                target_language=target_lang,
                service_name='none',
                confidence_score=1.0,
                timestamp=datetime.now()
            )
            
        # 估算字符数和成本
        char_count = len(text)
        
        # 按优先级尝试翻译服务
        services = self.config_manager.get_services_by_priority()
        
        for service_config in services:
            if not service_config.enabled:
                continue
                
            # 检查预算限制
            if not self.config_manager.should_use_service(service_config.name, char_count):
                logger.info(f"服务 {service_config.name} 因预算限制跳过")
                continue
                
            # 尝试翻译
            result = self._try_translate_with_service(
                service_config, text, source_lang, target_lang, char_count
            )
            
            if result and result.confidence_score >= service_config.quality_threshold:
                return result
                
        # 所有服务都失败，使用规则翻译器作为最后保障
        logger.warning("所有翻译服务都失败，使用规则翻译器")
        return self._fallback_translate(text, source_lang, target_lang)
        
    def _try_translate_with_service(self, config: ServiceConfig, text: str, 
                                  source_lang: str, target_lang: str, 
                                  char_count: int) -> Optional[TranslationResult]:
        """尝试使用指定服务翻译"""
        service_name = config.name
        
        try:
            # 获取服务实例
            service = self._service_instances.get(service_name)
            if not service:
                service = self._create_service_instance(config)
                if not service:
                    return None
                    
            # 记录开始时间
            start_time = time.time()
            
            # 更新统计信息
            stats = self._service_stats[service_name]
            stats['total_requests'] += 1
            stats['total_chars'] += char_count
            stats['last_used'] = datetime.now()
            
            # 执行翻译
            result = service.translate_text(text, source_lang, target_lang)
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            if result and result.translated_text:
                # 翻译成功
                stats['successful_requests'] += 1
                
                # 更新平均响应时间
                total_successful = stats['successful_requests']
                stats['avg_response_time'] = (
                    (stats['avg_response_time'] * (total_successful - 1) + response_time) / total_successful
                )
                
                # 计算和记录成本
                cost = char_count * config.cost_per_char
                stats['total_cost'] += cost
                self.config_manager.record_translation_cost(service_name, char_count, cost)
                
                # 设置服务名称
                result.service_name = service_name
                
                logger.info(f"翻译成功: {service_name}, {char_count}字符, 耗时{response_time:.2f}秒, 成本¥{cost:.4f}")
                return result
                
            else:
                # 翻译失败
                stats['failed_requests'] += 1
                logger.warning(f"翻译失败: {service_name}")
                
                # 尝试轮换API密钥
                if self.config_manager.rotate_api_key(service_name):
                    logger.info(f"已轮换 {service_name} 的API密钥")
                    # 重新创建服务实例
                    self._create_service_instance(config)
                    
                return None
                
        except Exception as e:
            # 翻译异常
            stats = self._service_stats.get(service_name, {})
            stats['failed_requests'] = stats.get('failed_requests', 0) + 1
            
            logger.error(f"翻译服务 {service_name} 异常: {e}")
            
            # 尝试轮换API密钥
            if self.config_manager.rotate_api_key(service_name):
                logger.info(f"已轮换 {service_name} 的API密钥")
                
            return None
            
    def _fallback_translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """降级翻译 - 使用规则翻译器"""
        try:
            rule_translator = RuleBasedTranslator()
            result = rule_translator.translate_text(text, source_lang, target_lang)
            result.service_name = 'rule_based_fallback'
            return result
            
        except Exception as e:
            logger.error(f"规则翻译器也失败了: {e}")
            
            # 最终降级：返回原文
            return TranslationResult(
                original_text=text,
                translated_text=text,  # 返回原文
                source_language=source_lang,
                target_language=target_lang,
                service_name='fallback_original',
                confidence_score=0.0,
                timestamp=datetime.now()
            )
            
    def translate_batch(self, texts: List[str], source_lang: str = 'en', 
                       target_lang: str = 'zh') -> List[TranslationResult]:
        """
        批量翻译文本
        
        Args:
            texts: 要翻译的文本列表
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            List[TranslationResult]: 翻译结果列表
        """
        results = []
        
        for text in texts:
            result = self.translate_text(text, source_lang, target_lang)
            results.append(result)
            
        return results
        
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        status = {
            'enabled_services': len([s for s in self.config_manager.services.values() if s.enabled]),
            'total_services': len(self.config_manager.services),
            'cost_statistics': self.config_manager.get_cost_statistics(),
            'service_statistics': self._service_stats.copy(),
            'web_interface_url': self.web_server.get_url() if self.web_server else None
        }
        
        return status
        
    def get_config_manager(self) -> DynamicConfigManager:
        """获取配置管理器实例"""
        return self.config_manager
        
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "managed_translation_service"
        
    def shutdown(self):
        """关闭服务"""
        if self.web_server:
            self.web_server.stop()
            
        logger.info("托管翻译服务已关闭")