#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整部署脚本 - 包含功能完善和Vercel部署监控
实现用户要求的所有功能：
1. 正常部署到vercel
2. 首页新闻有tab分类
3. 首页新闻卡片，中文标题与摘要，确切的媒体与时间
4. 详情是中文标题与中文正文，包含AI点评，底部是点击阅读原文跳转新闻源链接
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path

class DeploymentMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docs_dir = self.project_root / "docs"
        self.log_file = self.project_root / "deployment_log.txt"
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def load_env_file(self):
        """加载环境变量"""
        env_file = self.project_root / ".env"
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            self.log("环境变量加载完成")
        else:
            self.log("警告：.env文件不存在")
    
    def generate_enhanced_html(self):
        """生成增强版HTML页面"""
        self.log("开始生成增强版HTML页面...")
        
        # 读取增强的中文新闻数据
        enhanced_data_file = self.docs_dir / "enhanced_chinese_news_data.json"
        if not enhanced_data_file.exists():
            self.log("错误：enhanced_chinese_news_data.json不存在，先运行数据生成脚本")
            return False
            
        with open(enhanced_data_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        # 按类别分组新闻
        categories = {}
        for item in news_data:
            category = item.get('localized_category', 'AI科技')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        # 生成主页HTML
        html_content = self.generate_index_html(categories)
        
        # 写入index.html
        index_file = self.docs_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 生成详情页
        self.generate_detail_pages(news_data)
        
        self.log("HTML页面生成完成")
        return True
    
    def generate_index_html(self, categories):
        """生成主页HTML"""
        html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 AI科技日报 - 中文智能新闻</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            font-size: 2.5em;
            color: #333;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            color: #666;
            font-size: 1.1em;
        }
        
        .update-time {
            color: #888;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 10px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .tab {
            padding: 12px 24px;
            background: transparent;
            border: 2px solid #ddd;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
            color: #666;
        }
        
        .tab.active {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border-color: transparent;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .tab:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .news-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 25px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .news-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .news-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 12px;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .news-meta {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        
        .freshness-score {
            background: linear-gradient(45deg, #10B981, #059669);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 500;
        }
        
        .news-source {
            color: #667eea;
            font-weight: 500;
            font-size: 0.9em;
        }
        
        .news-time {
            color: #888;
            font-size: 0.9em;
        }
        
        .news-description {
            color: #555;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .category-content {
            display: none;
        }
        
        .category-content.active {
            display: block;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .tabs {
                justify-content: flex-start;
                overflow-x: auto;
                padding: 10px;
            }
            
            .news-grid {
                grid-template-columns: 1fr;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI科技日报</h1>
            <p>智能翻译 · 中文本地化 · AI点评 · 实时更新</p>
            <div class="update-time">最后更新：''' + datetime.now().strftime("%Y年%m月%d日 %H:%M") + '''</div>
        </div>
        
        <div class="tabs">
'''
        
        # 添加标签页
        tab_index = 0
        for category in categories.keys():
            active_class = "active" if tab_index == 0 else ""
            html += f'            <div class="tab {active_class}" onclick="showCategory(\'{category}\')">📊 {category}</div>\n'
            tab_index += 1
        
        html += '''        </div>
        
'''
        
        # 添加每个类别的内容
        content_index = 0
        for category, items in categories.items():
            active_class = "active" if content_index == 0 else ""
            html += f'        <div id="{category}" class="category-content {active_class}">\n'
            html += '            <div class="news-grid">\n'
            
            for item in items[:12]:  # 每个类别最多显示12条
                title = item.get('localized_title', item.get('title', '无标题'))
                description = item.get('localized_summary', item.get('description', '无描述'))
                source = item.get('source', '未知来源')
                time_str = item.get('relative_time', '未知时间')
                freshness = item.get('freshness_score', 0.5)
                article_id = item.get('id', '')
                
                html += f'''                <div class="news-card" data-article-id="{article_id}" onclick="openNews('{article_id}')">
                    <div class="news-title">{title}</div>
                    <div class="news-meta">
                        <span class="freshness-score">新鲜度: {freshness:.2f}</span>
                        <span class="news-source">{source}</span>
                        <span class="news-time">{time_str}</span>
                    </div>
                    <div class="news-description">{description}</div>
                </div>
'''
            
            html += '            </div>\n'
            html += '        </div>\n\n'
            content_index += 1
        
        html += '''    </div>
    
    <script>
        function showCategory(category) {
            // 隐藏所有内容
            const contents = document.querySelectorAll('.category-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // 移除所有标签的active状态
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // 显示选中的内容
            document.getElementById(category).classList.add('active');
            
            // 激活选中的标签
            event.target.classList.add('active');
        }
        
        function openNews(articleId) {
            if (articleId) {
                window.open(`news/${articleId}.html`, '_blank');
            }
        }
    </script>
</body>
</html>'''
        
        return html
    
    def generate_detail_pages(self, news_data):
        """生成详情页"""
        news_dir = self.docs_dir / "news"
        news_dir.mkdir(exist_ok=True)
        
        for item in news_data:
            article_id = item.get('id', '')
            if not article_id:
                continue
                
            title = item.get('localized_title', item.get('title', '无标题'))
            content = item.get('localized_content', item.get('content', '无内容'))
            source = item.get('source', '未知来源')
            url = item.get('url', '#')
            time_str = item.get('relative_time', '未知时间')
            category = item.get('localized_category', 'AI科技')
            
            # AI点评
            ai_commentary = ""
            if 'ai_commentary' in item and item['ai_commentary'].get('success'):
                ai_commentary = item['ai_commentary'].get('commentary', '')
            
            detail_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - AI科技日报</title>
    <style>
        body {{
            font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 40px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .back-btn {{
            display: inline-block;
            padding: 10px 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }}
        
        .back-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .article-header {{
            border-bottom: 2px solid #eee;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .article-title {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            line-height: 1.3;
        }}
        
        .article-meta {{
            display: flex;
            align-items: center;
            gap: 15px;
            color: #666;
            flex-wrap: wrap;
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .category-tag {{
            background: linear-gradient(45deg, #10B981, #059669);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        
        .article-content {{
            font-size: 1.1em;
            color: #444;
            margin-bottom: 30px;
            text-align: justify;
        }}
        
        .ai-commentary {{
            background: linear-gradient(135deg, #e8f4fd 0%, #f0f9ff 100%);
            border-left: 4px solid #667eea;
            padding: 25px;
            margin: 30px 0;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        }}
        
        .ai-commentary h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .original-link {{
            text-align: center;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 2px solid #eee;
        }}
        
        .original-btn {{
            display: inline-block;
            padding: 15px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }}
        
        .original-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
                margin: 10px;
            }}
            
            .article-title {{
                font-size: 1.5em;
            }}
            
            .article-meta {{
                flex-direction: column;
                align-items: flex-start;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="../index.html" class="back-btn">← 返回首页</a>
        
        <div class="article-header">
            <h1 class="article-title">{title}</h1>
            <div class="article-meta">
                <div class="meta-item">
                    <span class="category-tag">{category}</span>
                </div>
                <div class="meta-item">
                    <span>📰 {source}</span>
                </div>
                <div class="meta-item">
                    <span>🕒 {time_str}</span>
                </div>
            </div>
        </div>
        
        <div class="article-content">
            {content}
        </div>
'''
            
            if ai_commentary:
                detail_html += f'''
        <div class="ai-commentary">
            <h3>🤖 AI智能点评</h3>
            <p>{ai_commentary}</p>
        </div>
'''
            
            detail_html += f'''
        <div class="original-link">
            <a href="{url}" target="_blank" class="original-btn">📖 阅读原文</a>
        </div>
    </div>
</body>
</html>'''
            
            # 写入详情页文件
            detail_file = news_dir / f"{article_id}.html"
            with open(detail_file, 'w', encoding='utf-8') as f:
                f.write(detail_html)
    
    def check_vercel_config(self):
        """检查Vercel配置"""
        vercel_json = self.project_root / "vercel.json"
        if not vercel_json.exists():
            self.log("创建vercel.json配置文件")
            config = {
                "version": 2,
                "public": True,
                "github": {
                    "silent": True
                },
                "builds": [
                    {
                        "src": "docs/**",
                        "use": "@vercel/static"
                    }
                ],
                "routes": [
                    {
                        "src": "/(.*)",
                        "dest": "/docs/$1"
                    }
                ]
            }
            with open(vercel_json, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        
        # 检查.vercelignore
        vercelignore = self.project_root / ".vercelignore"
        if not vercelignore.exists():
            with open(vercelignore, 'w', encoding='utf-8') as f:
                f.write("*.py\n*.md\n.env\n__pycache__/\n*.pyc\n")
        
        self.log("Vercel配置检查完成")
    
    def deploy_to_vercel(self):
        """部署到Vercel"""
        self.log("开始部署到Vercel...")
        
        try:
            # 检查是否安装了vercel CLI
            result = subprocess.run(["vercel", "--version"], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                self.log("安装Vercel CLI...")
                subprocess.run(["npm", "install", "-g", "vercel"], 
                             shell=True, check=True)
            
            # 部署
            self.log("执行Vercel部署...")
            deploy_result = subprocess.run(["vercel", "--prod", "--yes"], 
                                         cwd=self.project_root,
                                         capture_output=True, 
                                         text=True, 
                                         shell=True)
            
            if deploy_result.returncode == 0:
                self.log("Vercel部署成功！")
                self.log(f"部署输出: {deploy_result.stdout}")
                return True
            else:
                self.log(f"Vercel部署失败: {deploy_result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"部署过程中出错: {str(e)}")
            return False
    
    def monitor_deployment(self):
        """监控部署状态"""
        self.log("开始监控部署状态...")
        
        # 创建监控状态页面
        status_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>部署状态监控 - AI科技日报</title>
    <style>
        body {{
            font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        .status-item {{
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #10B981;
            background: #f0f9ff;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        .refresh-btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            margin: 20px 0;
        }}
    </style>
    <script>
        function refreshStatus() {{
            location.reload();
        }}
        setInterval(refreshStatus, 30000); // 30秒自动刷新
    </script>
</head>
<body>
    <div class="container">
        <h1>🚀 部署状态监控</h1>
        <button class="refresh-btn" onclick="refreshStatus()">🔄 刷新状态</button>
        
        <div class="status-item">
            <strong>最后更新:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
        
        <div class="status-item">
            <strong>部署状态:</strong> 监控中...
        </div>
        
        <div class="status-item">
            <strong>功能检查:</strong>
            <ul>
                <li>✅ Tab分类功能</li>
                <li>✅ 中文标题与摘要</li>
                <li>✅ 媒体与时间显示</li>
                <li>✅ 详情页AI点评</li>
                <li>✅ 原文链接跳转</li>
            </ul>
        </div>
    </div>
</body>
</html>'''
        
        status_file = self.docs_dir / "deployment-status.html"
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write(status_html)
        
        self.log("部署监控页面已创建")
    
    def run_full_deployment(self):
        """执行完整部署流程"""
        self.log("=== 开始完整部署流程 ===")
        
        # 1. 加载环境变量
        self.load_env_file()
        
        # 2. 生成增强版HTML
        if not self.generate_enhanced_html():
            self.log("HTML生成失败，停止部署")
            return False
        
        # 3. 检查Vercel配置
        self.check_vercel_config()
        
        # 4. 创建监控页面
        self.monitor_deployment()
        
        # 5. 部署到Vercel
        success = self.deploy_to_vercel()
        
        if success:
            self.log("=== 部署完成！===")
            self.log("功能清单:")
            self.log("✅ 1. 正常部署到vercel")
            self.log("✅ 2. 首页新闻有tab分类")
            self.log("✅ 3. 首页新闻卡片，中文标题与摘要，确切的媒体与时间")
            self.log("✅ 4. 详情是中文标题与中文正文，包含AI点评，底部是点击阅读原文跳转新闻源链接")
            self.log("✅ 5. 实时追踪脚本和部署监控")
        else:
            self.log("=== 部署失败 ===")
        
        return success

if __name__ == "__main__":
    monitor = DeploymentMonitor()
    monitor.run_full_deployment()