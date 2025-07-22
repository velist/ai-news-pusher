#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书表格美化 - 添加今日亮点卡片和样式优化
"""

import json
import urllib.request
import time
from datetime import datetime

class TableEnhancer:
    def __init__(self):
        self.feishu_app_id = "cli_a8f4efb90f3a1013"
        self.feishu_app_secret = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
        self.feishu_base_url = "https://open.feishu.cn/open-apis"
        
    def get_feishu_token(self):
        """获取飞书访问令牌"""
        try:
            url = f"{self.feishu_base_url}/auth/v3/tenant_access_token/internal"
            data = {
                "app_id": self.feishu_app_id,
                "app_secret": self.feishu_app_secret
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            return result.get('tenant_access_token') if result.get('code') == 0 else None
        except:
            return None
    
    def add_highlight_card(self, token):
        """添加今日亮点卡片"""
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        
        try:
            # 获取今日最新的3条记录作为亮点
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records?page_size=3"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') != 0:
                return False
            
            records = result.get('data', {}).get('items', [])
            if not records:
                return False
            
            # 创建亮点汇总
            highlight_titles = []
            for record in records[:3]:
                title = record.get('fields', {}).get('标题', '')
                if title:
                    # 简化标题，去掉emoji前缀
                    clean_title = title.replace('📰 AI资讯：', '').replace('🚀 最新发布：', '').replace('💡 技术突破：', '').replace('🔄 重大更新：', '')
                    highlight_titles.append(clean_title[:50])
            
            # 生成今日亮点内容
            today = datetime.now().strftime('%Y年%m月%d日')
            highlight_content = f"""
🌟 【{today} AI科技亮点】

📊 今日热门话题：
1. {highlight_titles[0] if len(highlight_titles) > 0 else '暂无'}
2. {highlight_titles[1] if len(highlight_titles) > 1 else '暂无'}  
3. {highlight_titles[2] if len(highlight_titles) > 2 else '暂无'}

💡 关键洞察：人工智能技术持续快速发展，各大科技公司竞相发布新产品和技术突破

🎯 关注重点：大语言模型、AI应用落地、技术商业化进展
            """.strip()
            
            # 创建亮点卡片记录
            current_timestamp = int(time.time() * 1000)
            # 确保亮点卡片在最顶部
            highlight_timestamp = current_timestamp + 3600000  # 加1小时
            
            highlight_record = {
                "fields": {
                    "标题": f"🌟 今日AI科技亮点汇总 - {today}",
                    "摘要": highlight_content,
                    "AI观点": "每日亮点汇总帮助快速掌握AI行业动态，识别重要趋势和机会。",
                    "中国影响分析": "信息整合：提高AI资讯获取效率\n趋势把握：便于识别行业发展方向\n决策支持：为相关投资和技术决策提供参考",
                    "更新日期": highlight_timestamp,
                    "来源": {
                        "link": "https://example.com/daily-highlights",
                        "text": "每日亮点汇总"
                    }
                }
            }
            
            # 推送亮点卡片
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            req = urllib.request.Request(
                url,
                data=json.dumps(highlight_record).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') == 0:
                print("✅ 今日亮点卡片添加成功")
                return True
            else:
                print(f"❌ 亮点卡片添加失败: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 添加亮点卡片异常: {str(e)}")
            return False
    
    def add_stats_card(self, token):
        """添加统计卡片"""
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        
        try:
            # 获取所有记录进行统计
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') != 0:
                return False
            
            records = result.get('data', {}).get('items', [])
            
            # 统计分析
            total_records = len(records)
            today = datetime.now().strftime('%Y-%m-%d')
            today_records = 0
            
            # 统计公司提及次数
            company_mentions = {}
            companies = ['OpenAI', '谷歌', '微软', '英伟达', 'Meta', '苹果']
            
            for record in records:
                title = record.get('fields', {}).get('标题', '')
                update_time = record.get('fields', {}).get('更新日期', 0)
                
                # 统计今日记录
                if update_time:
                    try:
                        record_date = datetime.fromtimestamp(update_time / 1000).strftime('%Y-%m-%d')
                        if record_date == today:
                            today_records += 1
                    except:
                        pass
                
                # 统计公司提及
                for company in companies:
                    if company in title:
                        company_mentions[company] = company_mentions.get(company, 0) + 1
            
            # 找出最热门的公司
            top_companies = sorted(company_mentions.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # 生成统计内容
            stats_content = f"""
📊 【AI新闻数据统计】

📈 数据概览：
• 累计新闻: {total_records} 条
• 今日新增: {today_records} 条
• 数据覆盖: AI科技全领域

🏢 热门公司Top3:
{f"1. {top_companies[0][0]} ({top_companies[0][1]}次)" if len(top_companies) > 0 else "1. 暂无数据"}
{f"2. {top_companies[1][0]} ({top_companies[1][1]}次)" if len(top_companies) > 1 else "2. 暂无数据"}
{f"3. {top_companies[2][0]} ({top_companies[2][1]}次)" if len(top_companies) > 2 else "3. 暂无数据"}

🔄 更新频率: 每日8:00自动更新
📱 数据来源: GNews AI科技新闻API
            """.strip()
            
            # 创建统计卡片
            current_timestamp = int(time.time() * 1000)
            stats_timestamp = current_timestamp + 3000000  # 加50分钟，在亮点卡片下方
            
            stats_record = {
                "fields": {
                    "标题": f"📊 AI新闻数据统计面板 - {datetime.now().strftime('%Y-%m-%d')}",
                    "摘要": stats_content,
                    "AI观点": "数据统计有助于了解AI行业热点和趋势变化，为深入分析提供量化依据。",
                    "中国影响分析": "趋势识别：通过数据发现行业热点\n竞争分析：了解各公司在AI领域的活跃度\n投资参考：为相关投资决策提供数据支持",
                    "更新日期": stats_timestamp,
                    "来源": {
                        "link": "https://example.com/ai-stats",
                        "text": "数据统计面板"
                    }
                }
            }
            
            # 推送统计卡片
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            req = urllib.request.Request(
                url,
                data=json.dumps(stats_record).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            if result.get('code') == 0:
                print("✅ 数据统计卡片添加成功")
                return True
            else:
                print(f"❌ 统计卡片添加失败: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 添加统计卡片异常: {str(e)}")
            return False
    
    def enhance_table(self):
        """执行表格美化"""
        print("🎨 开始美化飞书表格...")
        print("=" * 40)
        
        token = self.get_feishu_token()
        if not token:
            print("❌ 无法获取飞书令牌")
            return False
        
        print("1️⃣ 添加今日亮点卡片...")
        highlight_success = self.add_highlight_card(token)
        
        print("2️⃣ 添加数据统计卡片...")
        stats_success = self.add_stats_card(token)
        
        print("=" * 40)
        
        if highlight_success and stats_success:
            print("🎉 表格美化完成！")
            print("📋 已添加:")
            print("   ✅ 今日AI科技亮点汇总")
            print("   ✅ 数据统计分析面板")
            print("🔗 查看效果: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
            return True
        else:
            print("⚠️  部分美化功能执行失败")
            return False

def main():
    enhancer = TableEnhancer()
    enhancer.enhance_table()

if __name__ == "__main__":
    main()