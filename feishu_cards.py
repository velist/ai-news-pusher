#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
飞书卡片消息推送 - 个性化新闻卡片
"""

import json
import urllib.request
import urllib.parse

class FeishuCardsPusher:
    def __init__(self):
        self.feishu_app_id = "cli_a8f4efb90f3a1013"
        self.feishu_app_secret = "lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8"
        self.feishu_base_url = "https://open.feishu.cn/open-apis"
        # 需要配置群聊的chat_id或用户open_id
        self.chat_id = "YOUR_CHAT_ID"  # 替换为实际的群聊ID
    
    def get_feishu_token(self):
        """获取飞书访问令牌"""
        try:
            url = f"{self.feishu_base_url}/auth/v3/tenant_access_token/internal"
            data = {"app_id": self.feishu_app_id, "app_secret": self.feishu_app_secret}
            
            req = urllib.request.Request(
                url, data=json.dumps(data).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
            return result.get('tenant_access_token') if result.get('code') == 0 else None
        except:
            return None
    
    def create_news_card(self, news_item):
        """创建新闻卡片"""
        card_content = {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True
            },
            "header": {
                "template": "blue",
                "title": {
                    "content": news_item['title'],
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": news_item['description'],
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**来源**\\n{news_item['source']}",
                                "tag": "lark_md"
                            }
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**重要性**\\n{'⭐' * news_item.get('importance', 3)}",
                                "tag": "lark_md"
                            }
                        }
                    ]
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "🔗 阅读原文",
                                "tag": "plain_text"
                            },
                            "url": news_item['url'],
                            "type": "primary"
                        }
                    ]
                }
            ]
        }
        return card_content
    
    def send_daily_digest(self, news_list):
        """发送每日摘要卡片"""
        token = self.get_feishu_token()
        if not token:
            return False
        
        # 创建摘要卡片
        digest_card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "template": "purple",
                "title": {
                    "content": "🌟 AI科技日报摘要",
                    "tag": "plain_text"
                }
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"📊 今日共收集 **{len(news_list)}** 条AI科技新闻",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "content": "🔥 **今日热点：**",
                        "tag": "lark_md"
                    }
                }
            ]
        }
        
        # 添加前3条重要新闻
        for i, news in enumerate(news_list[:3]):
            digest_card["elements"].append({
                "tag": "div",
                "text": {
                    "content": f"{i+1}. {news['title'][:50]}...",
                    "tag": "lark_md"
                }
            })
        
        return self.send_card_message(digest_card)
    
    def send_card_message(self, card_content):
        """发送卡片消息"""
        # 示例代码 - 需要配置实际的chat_id
        print("📧 飞书卡片消息示例:")
        print(json.dumps(card_content, indent=2, ensure_ascii=False))
        return True

def main():
    pusher = FeishuCardsPusher()
    
    # 示例新闻数据
    sample_news = [
        {
            'title': '🚀 OpenAI发布革命性GPT-5模型',
            'description': 'OpenAI最新发布的GPT-5在多项基准测试中表现优异...',
            'source': 'TechCrunch',
            'url': 'https://example.com/news1',
            'importance': 5
        }
    ]
    
    pusher.send_daily_digest(sample_news)

if __name__ == "__main__":
    main()