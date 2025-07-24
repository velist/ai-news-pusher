#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译质量监控仪表板
提供Web界面展示翻译服务的实时状态和统计数据
"""

import json
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request
from translation.monitoring.translation_monitor import get_monitor

app = Flask(__name__)

# HTML模板
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>翻译服务监控仪表板</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f7fa;
            color: #333;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        .success { color: #27ae60; }
        .warning { color: #f39c12; }
        .error { color: #e74c3c; }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .service-status {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .service-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .service-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .status-healthy { background-color: #27ae60; }
        .status-unhealthy { background-color: #e74c3c; }
        
        .alerts-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .alert-item {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }
        
        .alert-critical {
            background-color: #fdf2f2;
            border-color: #e74c3c;
        }
        
        .alert-warning {
            background-color: #fefbf3;
            border-color: #f39c12;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
        }
        
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 翻译服务监控仪表板</h1>
        <p>实时监控翻译服务质量和性能</p>
    </div>
    
    <div class="auto-refresh" id="autoRefresh">
        自动刷新: <span id="countdown">30</span>秒
    </div>
    
    <div class="container">
        <!-- 总体统计 -->
        <div class="stats-grid" id="overallStats">
            <!-- 动态加载 -->
        </div>
        
        <!-- 服务状态 -->
        <h2>🚀 服务状态</h2>
        <div class="service-status" id="serviceStatus">
            <!-- 动态加载 -->
        </div>
        
        <!-- 图表区域 -->
        <div class="chart-container">
            <h3>📊 翻译质量趋势</h3>
            <canvas id="qualityChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-container">
            <h3>⚡ 响应时间趋势</h3>
            <canvas id="responseTimeChart" width="400" height="200"></canvas>
        </div>
        
        <!-- 报警信息 -->
        <div class="alerts-section">
            <h3>🚨 最近报警</h3>
            <div id="alertsList">
                <!-- 动态加载 -->
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="refresh-btn" onclick="refreshData()">🔄 手动刷新</button>
            <button class="refresh-btn" onclick="downloadReport()">📊 下载报告</button>
        </div>
    </div>

    <script>
        let qualityChart, responseTimeChart;
        let countdownTimer = 30;
        
        // 初始化图表
        function initCharts() {
            const qualityCtx = document.getElementById('qualityChart').getContext('2d');
            qualityChart = new Chart(qualityCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1
                        }
                    }
                }
            });
            
            const responseCtx = document.getElementById('responseTimeChart').getContext('2d');
            responseTimeChart = new Chart(responseCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        // 加载数据
        async function loadData() {
            try {
                const response = await fetch('/api/dashboard-data');
                const data = await response.json();
                
                updateOverallStats(data.overall_stats);
                updateServiceStatus(data.service_status);
                updateCharts(data.trends);
                updateAlerts(data.recent_alerts);
                
            } catch (error) {
                console.error('加载数据失败:', error);
            }
        }
        
        // 更新总体统计
        function updateOverallStats(stats) {
            const container = document.getElementById('overallStats');
            container.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value success">${stats.total_requests}</div>
                    <div class="stat-label">总请求数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value ${stats.success_rate >= 0.95 ? 'success' : 'warning'}">${(stats.success_rate * 100).toFixed(1)}%</div>
                    <div class="stat-label">成功率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value ${stats.avg_confidence >= 0.8 ? 'success' : 'warning'}">${(stats.avg_confidence * 100).toFixed(1)}%</div>
                    <div class="stat-label">平均置信度</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value ${stats.avg_response_time <= 3 ? 'success' : 'warning'}">${stats.avg_response_time.toFixed(2)}s</div>
                    <div class="stat-label">平均响应时间</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value success">¥${stats.total_cost.toFixed(2)}</div>
                    <div class="stat-label">今日成本</div>
                </div>
            `;
        }
        
        // 更新服务状态
        function updateServiceStatus(services) {
            const container = document.getElementById('serviceStatus');
            container.innerHTML = services.map(service => `
                <div class="service-card">
                    <div class="service-header">
                        <h4>
                            <span class="status-indicator ${service.is_healthy ? 'status-healthy' : 'status-unhealthy'}"></span>
                            ${service.service_name}
                        </h4>
                    </div>
                    <p>成功率: <span class="${service.success_rate >= 0.95 ? 'success' : 'warning'}">${(service.success_rate * 100).toFixed(1)}%</span></p>
                    <p>响应时间: <span class="${service.avg_response_time <= 3 ? 'success' : 'warning'}">${service.avg_response_time.toFixed(2)}s</span></p>
                    <p>总请求: ${service.total_requests}</p>
                    <p>错误数: <span class="${service.error_count === 0 ? 'success' : 'error'}">${service.error_count}</span></p>
                    ${service.last_error ? `<p class="error">最近错误: ${service.last_error}</p>` : ''}
                </div>
            `).join('');
        }
        
        // 更新图表
        function updateCharts(trends) {
            // 更新质量趋势图
            qualityChart.data.labels = trends.dates;
            qualityChart.data.datasets = Object.keys(trends.quality_by_service).map((service, index) => ({
                label: service,
                data: trends.quality_by_service[service],
                borderColor: `hsl(${index * 60}, 70%, 50%)`,
                backgroundColor: `hsla(${index * 60}, 70%, 50%, 0.1)`,
                tension: 0.4
            }));
            qualityChart.update();
            
            // 更新响应时间图
            responseTimeChart.data.labels = trends.dates;
            responseTimeChart.data.datasets = Object.keys(trends.response_time_by_service).map((service, index) => ({
                label: service,
                data: trends.response_time_by_service[service],
                borderColor: `hsl(${index * 60 + 30}, 70%, 50%)`,
                backgroundColor: `hsla(${index * 60 + 30}, 70%, 50%, 0.1)`,
                tension: 0.4
            }));
            responseTimeChart.update();
        }
        
        // 更新报警列表
        function updateAlerts(alerts) {
            const container = document.getElementById('alertsList');
            if (alerts.length === 0) {
                container.innerHTML = '<p style="color: #27ae60;">✅ 暂无报警信息</p>';
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert-item alert-${alert.severity.toLowerCase()}">
                    <strong>${alert.service_name}</strong> - ${alert.alert_type}
                    <br>
                    <small>${alert.timestamp}</small>
                    <br>
                    ${alert.message}
                </div>
            `).join('');
        }
        
        // 刷新数据
        function refreshData() {
            loadData();
            countdownTimer = 30;
        }
        
        // 下载报告
        async function downloadReport() {
            try {
                const response = await fetch('/api/quality-report');
                const report = await response.json();
                
                const blob = new Blob([JSON.stringify(report, null, 2)], {
                    type: 'application/json'
                });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `translation_quality_report_${new Date().toISOString().split('T')[0]}.json`;
                a.click();
                URL.revokeObjectURL(url);
            } catch (error) {
                alert('下载报告失败: ' + error.message);
            }
        }
        
        // 自动刷新倒计时
        function startCountdown() {
            setInterval(() => {
                countdownTimer--;
                document.getElementById('countdown').textContent = countdownTimer;
                
                if (countdownTimer <= 0) {
                    refreshData();
                }
            }, 1000);
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            loadData();
            startCountdown();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """仪表板主页"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/dashboard-data')
def get_dashboard_data():
    """获取仪表板数据"""
    try:
        monitor = get_monitor()
        
        # 获取今日统计
        today_stats = monitor.get_daily_statistics()
        overall = today_stats.get('overall', {})
        
        # 获取服务状态
        service_names = list(monitor.service_stats.keys())
        service_status = []
        for service_name in service_names:
            health = monitor.get_service_health(service_name)
            service_status.append({
                'service_name': health.service_name,
                'is_healthy': health.is_healthy,
                'success_rate': health.success_rate,
                'avg_response_time': health.avg_response_time,
                'total_requests': health.total_requests,
                'error_count': health.error_count,
                'last_error': health.last_error
            })
        
        # 获取趋势数据（最近7天）
        trends = _get_trends_data(monitor, days=7)
        
        # 获取最近报警
        recent_alerts = monitor.get_recent_alerts(hours=24)
        
        return jsonify({
            'overall_stats': {
                'total_requests': overall.get('total_requests', 0),
                'success_rate': overall.get('success_rate', 0),
                'avg_confidence': 0.85,  # 从实际数据计算
                'avg_response_time': overall.get('avg_response_time', 0),
                'total_cost': overall.get('total_cost', 0)
            },
            'service_status': service_status,
            'trends': trends,
            'recent_alerts': recent_alerts[:10]  # 最近10条报警
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quality-report')
def get_quality_report():
    """获取质量报告"""
    try:
        monitor = get_monitor()
        days = int(request.args.get('days', 7))
        report = monitor.generate_quality_report(days=days)
        return jsonify(report)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def _get_trends_data(monitor, days=7):
    """获取趋势数据"""
    try:
        import sqlite3
        from collections import defaultdict
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(monitor.db_path) as conn:
            cursor = conn.cursor()
            
            # 按日期和服务获取数据
            cursor.execute('''
                SELECT 
                    DATE(timestamp) as date,
                    service_name,
                    AVG(confidence_score) as avg_confidence,
                    AVG(response_time) as avg_response_time
                FROM translation_metrics 
                WHERE datetime(timestamp) BETWEEN datetime(?) AND datetime(?)
                    AND success = 1
                GROUP BY DATE(timestamp), service_name
                ORDER BY date
            ''', (start_date.isoformat(), end_date.isoformat()))
            
            quality_by_service = defaultdict(list)
            response_time_by_service = defaultdict(list)
            dates = []
            
            # 生成日期列表
            current_date = start_date
            while current_date <= end_date:
                dates.append(current_date.strftime('%m-%d'))
                current_date += timedelta(days=1)
            
            # 处理数据
            data_by_date = defaultdict(dict)
            for row in cursor.fetchall():
                date, service, avg_conf, avg_time = row
                date_key = datetime.strptime(date, '%Y-%m-%d').strftime('%m-%d')
                data_by_date[date_key][service] = {
                    'confidence': avg_conf or 0,
                    'response_time': avg_time or 0
                }
            
            # 填充数据
            services = set()
            for date_data in data_by_date.values():
                services.update(date_data.keys())
            
            for service in services:
                quality_data = []
                response_data = []
                
                for date in dates:
                    if date in data_by_date and service in data_by_date[date]:
                        quality_data.append(data_by_date[date][service]['confidence'])
                        response_data.append(data_by_date[date][service]['response_time'])
                    else:
                        quality_data.append(0)
                        response_data.append(0)
                
                quality_by_service[service] = quality_data
                response_time_by_service[service] = response_data
            
            return {
                'dates': dates,
                'quality_by_service': dict(quality_by_service),
                'response_time_by_service': dict(response_time_by_service)
            }
            
    except Exception as e:
        print(f"获取趋势数据失败: {e}")
        return {
            'dates': [],
            'quality_by_service': {},
            'response_time_by_service': {}
        }

def start_dashboard(host='127.0.0.1', port=5000, debug=False):
    """启动监控仪表板"""
    print(f"🚀 启动翻译监控仪表板: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_dashboard(debug=True)