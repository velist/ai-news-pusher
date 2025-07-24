"""
翻译服务配置Web界面 - 提供实时配置管理的Web接口

功能特性:
- 实时查看和修改翻译服务配置
- API密钥管理和轮换
- 成本监控和预算控制
- 服务优先级调整
- 配置导入导出
"""

import json
import threading
from datetime import datetime
from typing import Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

from .dynamic_config_manager import DynamicConfigManager

logger = logging.getLogger(__name__)

class ConfigWebHandler(BaseHTTPRequestHandler):
    """配置管理Web处理器"""
    
    def __init__(self, *args, config_manager: DynamicConfigManager = None, **kwargs):
        self.config_manager = config_manager
        super().__init__(*args, **kwargs)
        
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self._serve_main_page()
        elif parsed_path.path == '/api/config':
            self._serve_config_api()
        elif parsed_path.path == '/api/stats':
            self._serve_stats_api()
        elif parsed_path.path.startswith('/static/'):
            self._serve_static_file(parsed_path.path)
        else:
            self._send_404()
            
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/config/update':
            self._handle_config_update()
        elif parsed_path.path == '/api/service/toggle':
            self._handle_service_toggle()
        elif parsed_path.path == '/api/key/rotate':
            self._handle_key_rotation()
        elif parsed_path.path == '/api/priority/update':
            self._handle_priority_update()
        else:
            self._send_404()
            
    def _serve_main_page(self):
        """提供主页面"""
        html_content = self._generate_main_html()
        self._send_response(200, html_content, 'text/html; charset=utf-8')
        
    def _serve_config_api(self):
        """提供配置API"""
        config_data = self.config_manager.export_config()
        self._send_json_response(config_data)
        
    def _serve_stats_api(self):
        """提供统计API"""
        stats = self.config_manager.get_cost_statistics()
        self._send_json_response(stats)
        
    def _handle_config_update(self):
        """处理配置更新"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            service_name = data.get('service_name')
            updates = data.get('updates', {})
            
            if service_name and updates:
                self.config_manager.update_service_config(service_name, **updates)
                self._send_json_response({'success': True, 'message': '配置更新成功'})
            else:
                self._send_json_response({'success': False, 'message': '无效的请求数据'}, 400)
                
        except Exception as e:
            logger.error(f"配置更新失败: {e}")
            self._send_json_response({'success': False, 'message': str(e)}, 500)
            
    def _handle_service_toggle(self):
        """处理服务启用/禁用"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            service_name = data.get('service_name')
            enabled = data.get('enabled')
            
            if service_name is not None and enabled is not None:
                if enabled:
                    self.config_manager.enable_service(service_name)
                else:
                    self.config_manager.disable_service(service_name)
                    
                self._send_json_response({'success': True, 'message': '服务状态更新成功'})
            else:
                self._send_json_response({'success': False, 'message': '无效的请求数据'}, 400)
                
        except Exception as e:
            logger.error(f"服务状态更新失败: {e}")
            self._send_json_response({'success': False, 'message': str(e)}, 500)
            
    def _handle_key_rotation(self):
        """处理API密钥轮换"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            service_name = data.get('service_name')
            
            if service_name:
                success = self.config_manager.rotate_api_key(service_name)
                if success:
                    self._send_json_response({'success': True, 'message': 'API密钥轮换成功'})
                else:
                    self._send_json_response({'success': False, 'message': '无法轮换API密钥'}, 400)
            else:
                self._send_json_response({'success': False, 'message': '无效的服务名称'}, 400)
                
        except Exception as e:
            logger.error(f"API密钥轮换失败: {e}")
            self._send_json_response({'success': False, 'message': str(e)}, 500)
            
    def _handle_priority_update(self):
        """处理优先级更新"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            service_name = data.get('service_name')
            new_priority = data.get('priority')
            
            if service_name and new_priority is not None:
                self.config_manager.update_service_priority(service_name, new_priority)
                self._send_json_response({'success': True, 'message': '优先级更新成功'})
            else:
                self._send_json_response({'success': False, 'message': '无效的请求数据'}, 400)
                
        except Exception as e:
            logger.error(f"优先级更新失败: {e}")
            self._send_json_response({'success': False, 'message': str(e)}, 500)
            
    def _send_response(self, status_code: int, content: str, content_type: str = 'text/plain'):
        """发送HTTP响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
        
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """发送JSON响应"""
        json_content = json.dumps(data, ensure_ascii=False, indent=2)
        self._send_response(status_code, json_content, 'application/json; charset=utf-8')
        
    def _send_404(self):
        """发送404响应"""
        self._send_response(404, '页面未找到', 'text/plain; charset=utf-8')
        
    def _generate_main_html(self) -> str:
        """生成主页面HTML"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>翻译服务配置管理</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .service-item { border: 1px solid #ddd; border-radius: 6px; padding: 15px; margin-bottom: 15px; }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .service-name { font-weight: bold; font-size: 18px; }
        .service-status { padding: 4px 12px; border-radius: 20px; font-size: 12px; }
        .status-enabled { background: #27ae60; color: white; }
        .status-disabled { background: #e74c3c; color: white; }
        .service-details { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 10px 0; }
        .detail-item { padding: 8px; background: #f8f9fa; border-radius: 4px; }
        .detail-label { font-weight: bold; color: #666; }
        .detail-value { color: #333; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 2px; }
        .btn-primary { background: #3498db; color: white; }
        .btn-success { background: #27ae60; color: white; }
        .btn-warning { background: #f39c12; color: white; }
        .btn-danger { background: #e74c3c; color: white; }
        .btn:hover { opacity: 0.8; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }
        .stat-value { font-size: 24px; font-weight: bold; }
        .stat-label { font-size: 14px; opacity: 0.9; }
        .progress-bar { width: 100%; height: 8px; background: rgba(255,255,255,0.3); border-radius: 4px; margin-top: 10px; }
        .progress-fill { height: 100%; background: white; border-radius: 4px; transition: width 0.3s; }
        .input-group { margin: 10px 0; }
        .input-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .input-group input, .input-group select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; }
        .modal-content { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; max-width: 500px; width: 90%; }
        .close { float: right; font-size: 24px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 翻译服务配置管理中心</h1>
            <p>实时管理翻译服务配置、API密钥、成本控制和服务优先级</p>
        </div>
        
        <div class="card">
            <h2>📊 成本统计概览</h2>
            <div id="statsContainer" class="stats-grid">
                <!-- 统计数据将通过JavaScript动态加载 -->
            </div>
        </div>
        
        <div class="card">
            <h2>⚙️ 翻译服务配置</h2>
            <div id="servicesContainer">
                <!-- 服务配置将通过JavaScript动态加载 -->
            </div>
        </div>
    </div>
    
    <!-- 配置编辑模态框 -->
    <div id="configModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h3>编辑服务配置</h3>
            <div id="configForm">
                <!-- 配置表单将动态生成 -->
            </div>
        </div>
    </div>
    
    <script>
        let configData = {};
        let statsData = {};
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            loadConfig();
            loadStats();
            setInterval(loadStats, 30000); // 每30秒刷新统计数据
        });
        
        // 加载配置数据
        async function loadConfig() {
            try {
                const response = await fetch('/api/config');
                configData = await response.json();
                renderServices();
            } catch (error) {
                console.error('加载配置失败:', error);
            }
        }
        
        // 加载统计数据
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                statsData = await response.json();
                renderStats();
            } catch (error) {
                console.error('加载统计数据失败:', error);
            }
        }
        
        // 渲染统计信息
        function renderStats() {
            const container = document.getElementById('statsContainer');
            const dailyUsage = (statsData.daily_usage_rate * 100).toFixed(1);
            const monthlyUsage = (statsData.monthly_usage_rate * 100).toFixed(1);
            
            container.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">¥${statsData.current_daily_cost.toFixed(2)}</div>
                    <div class="stat-label">今日成本 / ¥${statsData.daily_budget}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.min(dailyUsage, 100)}%"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">¥${statsData.current_monthly_cost.toFixed(2)}</div>
                    <div class="stat-label">本月成本 / ¥${statsData.monthly_budget}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.min(monthlyUsage, 100)}%"></div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${dailyUsage}%</div>
                    <div class="stat-label">今日预算使用率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${monthlyUsage}%</div>
                    <div class="stat-label">本月预算使用率</div>
                </div>
            `;
        }
        
        // 渲染服务列表
        function renderServices() {
            const container = document.getElementById('servicesContainer');
            const services = Object.values(configData.services || {});
            
            container.innerHTML = services.map(service => `
                <div class="service-item">
                    <div class="service-header">
                        <span class="service-name">${service.name}</span>
                        <span class="service-status ${service.enabled ? 'status-enabled' : 'status-disabled'}">
                            ${service.enabled ? '已启用' : '已禁用'}
                        </span>
                    </div>
                    <div class="service-details">
                        <div class="detail-item">
                            <div class="detail-label">优先级</div>
                            <div class="detail-value">${service.priority}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">每字符成本</div>
                            <div class="detail-value">¥${service.cost_per_char.toFixed(6)}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">质量阈值</div>
                            <div class="detail-value">${(service.quality_threshold * 100).toFixed(1)}%</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">API密钥数量</div>
                            <div class="detail-value">${service.api_keys.length}个</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">当前密钥索引</div>
                            <div class="detail-value">${service.current_key_index}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">每分钟限制</div>
                            <div class="detail-value">${service.max_requests_per_minute}次</div>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <button class="btn btn-primary" onclick="editService('${service.name}')">编辑配置</button>
                        <button class="btn ${service.enabled ? 'btn-warning' : 'btn-success'}" 
                                onclick="toggleService('${service.name}', ${!service.enabled})">
                            ${service.enabled ? '禁用服务' : '启用服务'}
                        </button>
                        <button class="btn btn-warning" onclick="rotateKey('${service.name}')">轮换密钥</button>
                    </div>
                </div>
            `).join('');
        }
        
        // 切换服务状态
        async function toggleService(serviceName, enabled) {
            try {
                const response = await fetch('/api/service/toggle', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ service_name: serviceName, enabled: enabled })
                });
                
                const result = await response.json();
                if (result.success) {
                    loadConfig();
                    alert(result.message);
                } else {
                    alert('操作失败: ' + result.message);
                }
            } catch (error) {
                alert('操作失败: ' + error.message);
            }
        }
        
        // 轮换API密钥
        async function rotateKey(serviceName) {
            try {
                const response = await fetch('/api/key/rotate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ service_name: serviceName })
                });
                
                const result = await response.json();
                if (result.success) {
                    loadConfig();
                    alert(result.message);
                } else {
                    alert('操作失败: ' + result.message);
                }
            } catch (error) {
                alert('操作失败: ' + error.message);
            }
        }
        
        // 编辑服务配置
        function editService(serviceName) {
            const service = configData.services[serviceName];
            if (!service) return;
            
            const form = document.getElementById('configForm');
            form.innerHTML = `
                <div class="input-group">
                    <label>优先级</label>
                    <input type="number" id="priority" value="${service.priority}" min="1" max="10">
                </div>
                <div class="input-group">
                    <label>每字符成本</label>
                    <input type="number" id="costPerChar" value="${service.cost_per_char}" step="0.000001">
                </div>
                <div class="input-group">
                    <label>质量阈值</label>
                    <input type="number" id="qualityThreshold" value="${service.quality_threshold}" step="0.01" min="0" max="1">
                </div>
                <div class="input-group">
                    <label>每分钟最大请求数</label>
                    <input type="number" id="maxRequests" value="${service.max_requests_per_minute}" min="1">
                </div>
                <div class="input-group">
                    <label>超时时间(秒)</label>
                    <input type="number" id="timeout" value="${service.timeout_seconds}" min="5">
                </div>
                <div class="input-group">
                    <label>重试次数</label>
                    <input type="number" id="retryCount" value="${service.retry_count}" min="0" max="5">
                </div>
                <div style="margin-top: 20px;">
                    <button class="btn btn-success" onclick="saveConfig('${serviceName}')">保存配置</button>
                    <button class="btn btn-warning" onclick="closeModal()">取消</button>
                </div>
            `;
            
            document.getElementById('configModal').style.display = 'block';
        }
        
        // 保存配置
        async function saveConfig(serviceName) {
            try {
                const updates = {
                    priority: parseInt(document.getElementById('priority').value),
                    cost_per_char: parseFloat(document.getElementById('costPerChar').value),
                    quality_threshold: parseFloat(document.getElementById('qualityThreshold').value),
                    max_requests_per_minute: parseInt(document.getElementById('maxRequests').value),
                    timeout_seconds: parseInt(document.getElementById('timeout').value),
                    retry_count: parseInt(document.getElementById('retryCount').value)
                };
                
                const response = await fetch('/api/config/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ service_name: serviceName, updates: updates })
                });
                
                const result = await response.json();
                if (result.success) {
                    closeModal();
                    loadConfig();
                    alert(result.message);
                } else {
                    alert('保存失败: ' + result.message);
                }
            } catch (error) {
                alert('保存失败: ' + error.message);
            }
        }
        
        // 关闭模态框
        function closeModal() {
            document.getElementById('configModal').style.display = 'none';
        }
        
        // 点击模态框外部关闭
        window.onclick = function(event) {
            const modal = document.getElementById('configModal');
            if (event.target === modal) {
                closeModal();
            }
        }
    </script>
</body>
</html>'''

class ConfigWebServer:
    """配置管理Web服务器"""
    
    def __init__(self, config_manager: DynamicConfigManager, host: str = 'localhost', port: int = 8080):
        self.config_manager = config_manager
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        
    def start(self):
        """启动Web服务器"""
        try:
            # 创建处理器类，注入配置管理器
            def handler_factory(*args, **kwargs):
                return ConfigWebHandler(*args, config_manager=self.config_manager, **kwargs)
                
            self.server = HTTPServer((self.host, self.port), handler_factory)
            
            def run_server():
                logger.info(f"配置管理Web界面已启动: http://{self.host}:{self.port}")
                self.server.serve_forever()
                
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"启动Web服务器失败: {e}")
            return False
            
    def stop(self):
        """停止Web服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("配置管理Web服务器已停止")
            
    def get_url(self) -> str:
        """获取Web界面URL"""
        return f"http://{self.host}:{self.port}"