#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel部署实时追踪脚本
功能：
1. 监控Vercel部署状态
2. 记录部署日志
3. 实时显示部署进度
4. 检查项目大小并优化
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path

class VercelDeploymentTracker:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.docs_dir = self.project_root / "docs"
        self.log_file = self.project_root / "deployment_logs.txt"
        self.deployment_status = {
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "deployment_url": None,
            "errors": [],
            "logs": []
        }
    
    def log_message(self, message, level="INFO"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # 写入日志文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        
        # 添加到状态记录
        self.deployment_status["logs"].append(log_entry)
    
    def check_project_size(self):
        """检查项目大小"""
        self.log_message("检查项目大小...")
        
        total_size = 0
        file_count = 0
        large_files = []
        
        for root, dirs, files in os.walk(self.docs_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1
                    
                    # 记录大文件（>1MB）
                    if size > 1024 * 1024:
                        large_files.append((str(file_path), size / (1024 * 1024)))
                except:
                    pass
        
        total_size_mb = total_size / (1024 * 1024)
        self.log_message(f"项目总大小: {total_size_mb:.2f} MB")
        self.log_message(f"文件总数: {file_count}")
        
        if large_files:
            self.log_message("发现大文件:")
            for file_path, size_mb in large_files:
                self.log_message(f"  - {file_path}: {size_mb:.2f} MB")
        
        # Vercel限制是10MB
        if total_size_mb > 10:
            self.log_message(f"警告: 项目大小 ({total_size_mb:.2f} MB) 超过Vercel限制 (10 MB)", "WARNING")
            return False, total_size_mb
        
        return True, total_size_mb
    
    def optimize_project_size(self):
        """优化项目大小"""
        self.log_message("开始优化项目大小...")
        
        # 删除不必要的文件
        unnecessary_files = [
            ".deploy-version",
            ".deployment-sync-timestamp", 
            ".last-deploy-attempt",
            ".vercel-deploy-*",
            ".vercel-sync-trigger",
            ".vercel-trigger",
            "deployment-status.html"
        ]
        
        removed_count = 0
        for pattern in unnecessary_files:
            if "*" in pattern:
                # 处理通配符
                import glob
                for file_path in glob.glob(str(self.docs_dir / pattern)):
                    try:
                        os.remove(file_path)
                        self.log_message(f"删除文件: {file_path}")
                        removed_count += 1
                    except:
                        pass
            else:
                file_path = self.docs_dir / pattern
                if file_path.exists():
                    try:
                        file_path.unlink()
                        self.log_message(f"删除文件: {file_path}")
                        removed_count += 1
                    except:
                        pass
        
        # 压缩JSON文件
        json_files = list(self.docs_dir.glob("*.json"))
        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # 重新写入，去除空格
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
                
                self.log_message(f"压缩JSON文件: {json_file.name}")
            except:
                pass
        
        self.log_message(f"优化完成，删除了 {removed_count} 个文件")
    
    def deploy_to_vercel(self):
        """部署到Vercel"""
        self.log_message("开始部署到Vercel...")
        self.deployment_status["status"] = "deploying"
        self.deployment_status["start_time"] = datetime.now().isoformat()
        
        try:
            # 检查是否安装了Vercel CLI
            try:
                result = subprocess.run(["vercel", "--version"], 
                                      capture_output=True, text=True, cwd=self.project_root, shell=True)
                
                if result.returncode != 0:
                    self.log_message("Vercel CLI未安装，正在安装...", "WARNING")
                    install_result = subprocess.run(["npm", "install", "-g", "vercel"], 
                                                  capture_output=True, text=True, shell=True)
                    if install_result.returncode != 0:
                        raise Exception(f"安装Vercel CLI失败: {install_result.stderr}")
            except FileNotFoundError:
                raise Exception("无法找到vercel命令，请确保Vercel CLI已正确安装并在PATH中")
            
            # 部署到Vercel
            deploy_cmd = ["vercel", "--prod", "--yes"]
            self.log_message(f"执行部署命令: {' '.join(deploy_cmd)}")
            
            process = subprocess.Popen(
                deploy_cmd,
                cwd=self.docs_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                shell=True
            )
            
            # 实时读取输出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(f"Vercel输出: {output.strip()}")
                    
                    # 检查是否包含部署URL
                    if "https://" in output and "vercel.app" in output:
                        self.deployment_status["deployment_url"] = output.strip()
            
            # 获取最终结果
            stderr = process.stderr.read()
            if stderr:
                self.log_message(f"Vercel错误: {stderr}", "ERROR")
                self.deployment_status["errors"].append(stderr)
            
            if process.returncode == 0:
                self.deployment_status["status"] = "success"
                self.log_message("部署成功！", "SUCCESS")
                if self.deployment_status["deployment_url"]:
                    self.log_message(f"部署地址: {self.deployment_status['deployment_url']}", "SUCCESS")
            else:
                self.deployment_status["status"] = "failed"
                self.log_message(f"部署失败，退出代码: {process.returncode}", "ERROR")
                
        except Exception as e:
            self.deployment_status["status"] = "failed"
            self.deployment_status["errors"].append(str(e))
            self.log_message(f"部署过程中发生错误: {str(e)}", "ERROR")
        
        finally:
            self.deployment_status["end_time"] = datetime.now().isoformat()
    
    def check_deployment_status(self):
        """检查部署状态"""
        if self.deployment_status["deployment_url"]:
            try:
                response = requests.get(self.deployment_status["deployment_url"], timeout=10)
                if response.status_code == 200:
                    self.log_message("部署的网站可以正常访问", "SUCCESS")
                    return True
                else:
                    self.log_message(f"网站访问异常，状态码: {response.status_code}", "WARNING")
                    return False
            except Exception as e:
                self.log_message(f"检查网站状态时发生错误: {str(e)}", "ERROR")
                return False
        return False
    
    def save_deployment_report(self):
        """保存部署报告"""
        report_file = self.project_root / f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.deployment_status, f, ensure_ascii=False, indent=2)
        
        self.log_message(f"部署报告已保存: {report_file}")
    
    def run_deployment_process(self):
        """运行完整的部署流程"""
        self.log_message("=" * 50)
        self.log_message("开始Vercel部署流程")
        self.log_message("=" * 50)
        
        # 1. 检查项目大小
        size_ok, size_mb = self.check_project_size()
        
        # 2. 如果项目太大，进行优化
        if not size_ok:
            self.optimize_project_size()
            # 重新检查大小
            size_ok, size_mb = self.check_project_size()
            
            if not size_ok:
                self.log_message(f"优化后项目仍然太大 ({size_mb:.2f} MB)，无法部署", "ERROR")
                return False
        
        # 3. 部署到Vercel
        self.deploy_to_vercel()
        
        # 4. 检查部署状态
        if self.deployment_status["status"] == "success":
            time.sleep(5)  # 等待部署完全生效
            self.check_deployment_status()
        
        # 5. 保存部署报告
        self.save_deployment_report()
        
        # 6. 显示最终结果
        self.log_message("=" * 50)
        self.log_message(f"部署流程完成，状态: {self.deployment_status['status']}")
        if self.deployment_status["deployment_url"]:
            self.log_message(f"部署地址: {self.deployment_status['deployment_url']}")
        self.log_message("=" * 50)
        
        return self.deployment_status["status"] == "success"

def main():
    """主函数"""
    tracker = VercelDeploymentTracker()
    
    try:
        success = tracker.run_deployment_process()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        tracker.log_message("部署被用户中断", "WARNING")
        sys.exit(1)
    except Exception as e:
        tracker.log_message(f"部署过程中发生未预期的错误: {str(e)}", "ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()