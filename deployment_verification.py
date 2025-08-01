#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
部署功能验证脚本
验证部署的网站是否满足所有要求：
1. 正常部署到vercel
2. 首页新闻有tab分类
3. 首页新闻卡片，中文标题与摘要，确切的媒体与时间
4. 详情是中文标题与中文正文，包含AI点评，底部是点击阅读原文跳转新闻源链接
"""

import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import re

class DeploymentVerifier:
    def __init__(self, deployment_url):
        self.deployment_url = deployment_url
        self.verification_results = {
            "deployment_status": False,
            "tab_categories": False,
            "chinese_content": False,
            "news_cards": False,
            "detail_pages": False,
            "ai_commentary": False,
            "source_links": False,
            "errors": [],
            "details": {}
        }
    
    def log_result(self, test_name, success, details=""):
        """记录验证结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name}: {status}")
        if details:
            print(f"  详情: {details}")
        if not success:
            self.verification_results["errors"].append(f"{test_name}: {details}")
    
    def verify_deployment_status(self):
        """验证部署状态"""
        try:
            response = requests.get(self.deployment_url, timeout=10)
            if response.status_code == 200:
                self.verification_results["deployment_status"] = True
                self.log_result("1. Vercel部署状态", True, "网站可正常访问")
                return response.text
            else:
                self.log_result("1. Vercel部署状态", False, f"HTTP状态码: {response.status_code}")
                return None
        except Exception as e:
            self.log_result("1. Vercel部署状态", False, f"访问错误: {str(e)}")
            return None
    
    def verify_tab_categories(self, html_content):
        """验证tab分类功能"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找tab相关元素
        tabs = soup.find_all(['div', 'ul', 'nav'], class_=re.compile(r'tab|category|filter', re.I))
        tab_buttons = soup.find_all(['button', 'a'], class_=re.compile(r'tab|category', re.I))
        
        # 检查是否有分类标签
        categories_found = []
        for element in soup.find_all(text=re.compile(r'AI科技|科技创新|经济新闻|游戏资讯')):
            categories_found.append(element.strip())
        
        if tabs or tab_buttons or categories_found:
            self.verification_results["tab_categories"] = True
            self.verification_results["details"]["categories"] = list(set(categories_found))
            self.log_result("2. Tab分类功能", True, f"发现分类: {', '.join(set(categories_found))}")
        else:
            self.log_result("2. Tab分类功能", False, "未发现tab分类元素")
    
    def verify_chinese_content(self, html_content):
        """验证中文内容"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 检查中文字符比例
        text_content = soup.get_text()
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text_content))
        total_chars = len(text_content.replace(' ', '').replace('\n', ''))
        
        if total_chars > 0:
            chinese_ratio = chinese_chars / total_chars
            if chinese_ratio > 0.3:  # 中文字符占比超过30%
                self.verification_results["chinese_content"] = True
                self.log_result("3. 中文内容", True, f"中文字符占比: {chinese_ratio:.1%}")
            else:
                self.log_result("3. 中文内容", False, f"中文字符占比过低: {chinese_ratio:.1%}")
        else:
            self.log_result("3. 中文内容", False, "无法获取文本内容")
    
    def verify_news_cards(self, html_content):
        """验证新闻卡片功能"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找新闻卡片
        news_items = soup.find_all(['div', 'article'], class_=re.compile(r'news|item|card', re.I))
        
        if not news_items:
            news_items = soup.find_all('div', class_='news-item')
        
        news_count = len(news_items)
        
        if news_count > 0:
            self.verification_results["news_cards"] = True
            
            # 检查新闻卡片内容
            sample_item = news_items[0] if news_items else None
            details = []
            
            if sample_item:
                # 检查标题
                title_elem = sample_item.find(['h1', 'h2', 'h3', 'div'], class_=re.compile(r'title', re.I))
                if title_elem:
                    details.append(f"标题: {title_elem.get_text()[:50]}...")
                
                # 检查时间
                time_elem = sample_item.find(['div', 'span'], class_=re.compile(r'time|date|meta', re.I))
                if time_elem:
                    details.append(f"时间信息: {time_elem.get_text()[:30]}")
                
                # 检查摘要
                desc_elem = sample_item.find(['div', 'p'], class_=re.compile(r'desc|summary|content', re.I))
                if desc_elem:
                    details.append(f"摘要: {desc_elem.get_text()[:50]}...")
            
            self.verification_results["details"]["news_cards"] = {
                "count": news_count,
                "sample_content": details
            }
            
            self.log_result("4. 新闻卡片", True, f"发现 {news_count} 个新闻项")
        else:
            self.log_result("4. 新闻卡片", False, "未发现新闻卡片")
    
    def verify_detail_pages(self):
        """验证详情页功能"""
        try:
            # 尝试访问一个详情页
            detail_url = f"{self.deployment_url}/news/ai_0_1753614821.html"
            response = requests.get(detail_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 检查中文标题
                title_elem = soup.find(['h1', 'h2', 'title'])
                has_chinese_title = False
                if title_elem:
                    title_text = title_elem.get_text()
                    has_chinese_title = bool(re.search(r'[\u4e00-\u9fff]', title_text))
                
                # 检查AI点评
                ai_commentary = soup.find(['div', 'section'], class_=re.compile(r'ai|commentary|comment', re.I))
                has_ai_commentary = ai_commentary is not None
                
                # 检查原文链接
                source_links = soup.find_all('a', href=True)
                has_source_link = any('http' in link.get('href', '') for link in source_links)
                
                if has_chinese_title and has_ai_commentary and has_source_link:
                    self.verification_results["detail_pages"] = True
                    self.verification_results["ai_commentary"] = has_ai_commentary
                    self.verification_results["source_links"] = has_source_link
                    
                    self.log_result("5. 详情页功能", True, "包含中文标题、AI点评和原文链接")
                    self.log_result("6. AI点评功能", True, "详情页包含AI点评")
                    self.log_result("7. 原文链接", True, "包含跳转链接")
                else:
                    missing = []
                    if not has_chinese_title: missing.append("中文标题")
                    if not has_ai_commentary: missing.append("AI点评")
                    if not has_source_link: missing.append("原文链接")
                    
                    self.log_result("5. 详情页功能", False, f"缺少: {', '.join(missing)}")
                    self.log_result("6. AI点评功能", has_ai_commentary, "")
                    self.log_result("7. 原文链接", has_source_link, "")
            else:
                self.log_result("5. 详情页功能", False, f"详情页访问失败: {response.status_code}")
                
        except Exception as e:
            self.log_result("5. 详情页功能", False, f"访问详情页时出错: {str(e)}")
    
    def run_full_verification(self):
        """运行完整验证"""
        print("=" * 60)
        print(f"开始验证部署: {self.deployment_url}")
        print("=" * 60)
        
        # 1. 验证部署状态
        html_content = self.verify_deployment_status()
        
        if html_content:
            # 2. 验证tab分类
            self.verify_tab_categories(html_content)
            
            # 3. 验证中文内容
            self.verify_chinese_content(html_content)
            
            # 4. 验证新闻卡片
            self.verify_news_cards(html_content)
        
        # 5-7. 验证详情页功能
        self.verify_detail_pages()
        
        # 生成总结报告
        self.generate_summary_report()
    
    def generate_summary_report(self):
        """生成总结报告"""
        print("\n" + "=" * 60)
        print("验证结果总结")
        print("=" * 60)
        
        total_tests = 7
        passed_tests = sum([
            self.verification_results["deployment_status"],
            self.verification_results["tab_categories"],
            self.verification_results["chinese_content"],
            self.verification_results["news_cards"],
            self.verification_results["detail_pages"],
            self.verification_results["ai_commentary"],
            self.verification_results["source_links"]
        ])
        
        print(f"通过测试: {passed_tests}/{total_tests}")
        print(f"成功率: {passed_tests/total_tests:.1%}")
        
        if self.verification_results["errors"]:
            print("\n❌ 发现的问题:")
            for error in self.verification_results["errors"]:
                print(f"  - {error}")
        
        if passed_tests == total_tests:
            print("\n🎉 所有功能验证通过！部署成功！")
        else:
            print(f"\n⚠️  还有 {total_tests - passed_tests} 个功能需要修复")
        
        # 保存验证报告
        report_file = f"verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细报告已保存: {report_file}")
        print(f"🌐 部署地址: {self.deployment_url}")

def main():
    deployment_url = "https://docs-n68d4n5f4-velists-projects.vercel.app"
    verifier = DeploymentVerifier(deployment_url)
    verifier.run_full_verification()

if __name__ == "__main__":
    main()