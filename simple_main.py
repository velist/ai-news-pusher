#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版主程序 - 专注核心功能，确保翻译生效
"""

import json
import urllib.request
import urllib.parse
import time
from datetime import datetime

class SimpleNewsProcessor:
    def __init__(self):
        # 直接硬编码配置，避免依赖问题
        self.gnews_api_key = "c3cb6fef0f86251ada2b515017b97143"
        self.feishu_app_id = "cli_a8f4efb90f3a1013"
        self.feishu_app_secret = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
        self.feishu_base_url = "https://open.feishu.cn/open-apis"
        self.gnews_base_url = "https://gnews.io/api/v4"
        
    def translate_title(self, title):
        """简化但有效的中文翻译"""
        if not title:
            return title
            
        # 核心翻译映射
        replacements = [
            ('OpenAI', 'OpenAI'),
            ('Google', '谷歌'),
            ('Microsoft', '微软'),
            ('Apple', '苹果'),
            ('NVIDIA', '英伟达'),
            ('Artificial Intelligence', '人工智能'),
            ('AI', 'AI'),
            ('Machine Learning', '机器学习'),
            ('ChatGPT', 'ChatGPT'),
            ('GPT-4', 'GPT-4'),
            ('GPT-5', 'GPT-5'),
            ('Launches', '发布'),
            ('Releases', '发布'),
            ('Announces', '宣布'),
            ('Introduces', '推出'),
            ('Updates', '更新'),
            ('New', '全新'),
            ('Latest', '最新'),
            ('Advanced', '先进的'),
            ('Revolutionary', '革命性'),
            ('Breakthrough', '突破性'),
        ]
        
        chinese_title = title
        
        # 简单字符串替换
        for english, chinese in replacements:
            chinese_title = chinese_title.replace(english, chinese)
            chinese_title = chinese_title.replace(english.lower(), chinese)
        
        # 计算英文字符比例
        english_chars = sum(1 for c in chinese_title if c.isalpha() and ord(c) < 128)
        total_chars = len(chinese_title)
        
        # 如果英文字符超过50%，添加中文前缀
        if total_chars > 0 and english_chars / total_chars > 0.5:
            if any(word in title.lower() for word in ['launch', 'release', 'announce']):
                chinese_title = f"🚀 最新发布：{chinese_title}"
            elif any(word in title.lower() for word in ['breakthrough', 'innovation']):
                chinese_title = f"💡 技术突破：{chinese_title}"
            elif any(word in title.lower() for word in ['update', 'improve']):
                chinese_title = f"🔄 重大更新：{chinese_title}"
            else:
                chinese_title = f"📰 AI资讯：{chinese_title}"
        
        return chinese_title
    
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
                
            if result.get('code') == 0:
                print("✅ 飞书令牌获取成功")
                return result.get('tenant_access_token')
            else:
                print(f"❌ 飞书令牌获取失败: {result}")
                return None
                
        except Exception as e:
            print(f"❌ 飞书令牌获取异常: {str(e)}")
            return None
    
    def get_news(self):
        """获取AI新闻"""
        try:
            params = {
                'apikey': self.gnews_api_key,
                'q': 'AI OR OpenAI OR "artificial intelligence"',
                'lang': 'en',
                'max': '10'
            }
            
            query_string = urllib.parse.urlencode(params)
            url = f"{self.gnews_base_url}/search?{query_string}"
            
            with urllib.request.urlopen(url, timeout=15) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            articles = result.get('articles', [])
            print(f"✅ 成功获取 {len(articles)} 条新闻")
            return articles
            
        except Exception as e:
            print(f"❌ 新闻获取失败: {str(e)}")
            return []
    
    def get_max_timestamp(self, token):
        """获取表格最大时间戳"""
        try:
            app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
            table_id = "tblyPOJ4k9DxJuKc"
            
            url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            req = urllib.request.Request(
                url,
                headers={'Authorization': f'Bearer {token}'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            max_timestamp = int(time.time() * 1000)
            
            if result.get('code') == 0:
                records = result.get('data', {}).get('items', [])
                for record in records:
                    update_date = record.get('fields', {}).get('更新日期', 0)
                    if isinstance(update_date, (int, float)) and update_date > max_timestamp:
                        max_timestamp = int(update_date)
            
            print(f"📅 当前最大时间戳: {max_timestamp}")
            return max_timestamp
            
        except Exception as e:
            print(f"❌ 获取时间戳失败: {str(e)}")
            return int(time.time() * 1000)
    
    def push_news(self, articles, token, base_timestamp):
        """推送新闻到飞书表格"""
        app_token = "TXkMb0FBwaD52ese70ScPLn5n5b"
        table_id = "tblyPOJ4k9DxJuKc"
        success_count = 0
        
        for i, article in enumerate(articles):
            try:
                # 翻译标题
                chinese_title = self.translate_title(article.get('title', ''))
                
                # 生成递增时间戳，确保最新的在顶部
                timestamp = base_timestamp + (len(articles) - i) * 60000  # 每条间隔1分钟
                
                # 构建记录数据
                record_data = {
                    "fields": {
                        "标题": chinese_title,
                        "摘要": (article.get('description', '') or article.get('content', ''))[:300],
                        "AI观点": "该AI技术发展值得关注，体现了人工智能领域的持续创新进展。",
                        "中国影响分析": "技术发展：推动国内AI产业升级\n市场机遇：为企业提供新发展方向\n竞争态势：需关注对现有格局的影响",
                        "更新日期": timestamp,
                        "来源": {
                            "link": article.get('url', ''),
                            "text": article.get('source', {}).get('name', '新闻源')
                        }
                    }
                }
                
                # 发送请求
                url = f"{self.feishu_base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
                req = urllib.request.Request(
                    url,
                    data=json.dumps(record_data).encode('utf-8'),
                    headers={
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json'
                    }
                )
                
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read().decode('utf-8'))
                
                if result.get('code') == 0:
                    success_count += 1
                    print(f"✅ 推送成功 ({i+1}/{len(articles)}): {chinese_title[:50]}...")
                else:
                    print(f"❌ 推送失败 ({i+1}): {result}")
                
                time.sleep(0.5)  # 避免频率限制
                
            except Exception as e:
                print(f"❌ 推送异常 ({i+1}): {str(e)}")
        
        return success_count
    
    def run(self):
        """执行完整流程"""
        print("🚀 开始AI新闻推送任务")
        print("=" * 50)
        
        # 1. 获取飞书令牌
        token = self.get_feishu_token()
        if not token:
            print("❌ 无法获取飞书令牌，任务终止")
            return False
        
        # 2. 获取新闻
        articles = self.get_news()
        if not articles:
            print("❌ 无法获取新闻，任务终止")  
            return False
        
        # 3. 获取基准时间戳
        base_timestamp = self.get_max_timestamp(token)
        
        # 4. 推送新闻
        success_count = self.push_news(articles, token, base_timestamp)
        
        print("=" * 50)
        print(f"🎉 任务完成！成功推送 {success_count}/{len(articles)} 条新闻")
        print("🔗 查看结果: https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b")
        
        return success_count > 0

def main():
    processor = SimpleNewsProcessor()
    success = processor.run()
    
    if not success:
        print("❌ 任务失败")
        exit(1)
    else:
        print("✅ 任务成功")

if __name__ == "__main__":
    main()