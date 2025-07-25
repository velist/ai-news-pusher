#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI新闻点评系统 - 使用硅基流动API生成智能新闻点评
"""

import json
import urllib.request
import urllib.parse
from typing import Optional, Dict

class AICommentary:
    """AI新闻点评生成器"""
    
    def __init__(self, api_key: str = "sk-wvnbuucaiczandbauqvtnovrshvdmrupjgkdjfvadzqluhpa"):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.model = "Qwen/Qwen2.5-7B-Instruct"
        
        # 点评模板
        self.commentary_prompt = """作为一名专业的科技新闻分析师，请对以下新闻进行简洁而深入的点评分析。

新闻标题：{title}
新闻内容：{content}

请从以下角度进行点评（控制在150字以内）：
1. 新闻的重要性和影响
2. 技术或商业层面的分析
3. 对行业或用户的意义
4. 未来发展趋势预测

要求：
- 语言简洁专业，适合中文读者
- 突出关键信息和洞察
- 避免重复新闻内容
- 提供有价值的分析观点"""

    def generate_commentary(self, title: str, content: str, description: str = "") -> Dict:
        """生成AI新闻点评"""
        try:
            # 准备新闻内容
            news_content = self._prepare_content(title, content, description)
            
            # 构建请求
            prompt = self.commentary_prompt.format(
                title=title,
                content=news_content
            )
            
            # 调用API
            response = self._call_siliconflow_api(prompt)
            
            if response and 'choices' in response:
                commentary_text = response['choices'][0]['message']['content'].strip()
                
                return {
                    'success': True,
                    'commentary': commentary_text,
                    'model': self.model,
                    'timestamp': self._get_current_time(),
                    'word_count': len(commentary_text),
                    'error': None
                }
            else:
                return self._error_response("API响应格式错误")
                
        except Exception as e:
            return self._error_response(f"生成点评失败: {str(e)}")
    
    def _prepare_content(self, title: str, content: str, description: str) -> str:
        """准备用于分析的新闻内容"""
        # 优先使用content，如果没有则使用description
        main_content = content if content and len(content) > 100 else description
        
        # 限制内容长度，避免token过多
        if len(main_content) > 1000:
            main_content = main_content[:1000] + "..."
        
        return main_content
    
    def _call_siliconflow_api(self, prompt: str) -> Optional[Dict]:
        """调用硅基流动API"""
        try:
            # 构建请求数据
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            # 构建请求
            request_data = json.dumps(data).encode('utf-8')
            
            req = urllib.request.Request(
                self.base_url,
                data=request_data,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'AI-News-Commentary/1.0'
                },
                method='POST'
            )
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data)
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"HTTP错误 {e.code}: {error_body}")
            return None
        except Exception as e:
            print(f"API调用失败: {str(e)}")
            return None
    
    def _error_response(self, error_message: str) -> Dict:
        """生成错误响应"""
        return {
            'success': False,
            'commentary': None,
            'model': self.model,
            'timestamp': self._get_current_time(),
            'word_count': 0,
            'error': error_message
        }
    
    def _get_current_time(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate_fallback_commentary(self, title: str, category: str = "") -> str:
        """生成备用点评（当API失败时使用）"""
        fallback_templates = {
            'AI科技': '这是一条关于人工智能技术发展的重要新闻，反映了当前AI领域的最新进展和趋势。',
            'technology': '这项技术创新展现了科技行业的持续发展，可能对相关产业产生重要影响。',
            '游戏资讯': '游戏行业的这一动态体现了娱乐科技的创新发展，值得行业关注。',
            '经济新闻': '这一经济动态反映了市场的变化趋势，可能对相关行业和投资者产生影响。',
            'default': '这是一条值得关注的新闻，展现了当前行业的发展动态和趋势变化。'
        }
        
        template = fallback_templates.get(category, fallback_templates['default'])
        return f"【AI简评】{template}建议关注后续发展。"
    
    def batch_generate_commentary(self, news_list: list) -> Dict:
        """批量生成新闻点评"""
        results = {
            'success_count': 0,
            'error_count': 0,
            'total_count': len(news_list),
            'commentaries': []
        }
        
        for news_item in news_list:
            title = news_item.get('title', '')
            content = news_item.get('content', '')
            description = news_item.get('description', '')
            category = news_item.get('category', '')
            
            if not title:
                continue
            
            # 生成点评
            commentary_result = self.generate_commentary(title, content, description)
            
            if commentary_result['success']:
                results['success_count'] += 1
            else:
                results['error_count'] += 1
                # 使用备用点评
                commentary_result['commentary'] = self.generate_fallback_commentary(title, category)
                commentary_result['is_fallback'] = True
            
            # 添加到新闻项
            news_item['ai_commentary'] = commentary_result
            results['commentaries'].append({
                'title': title,
                'commentary': commentary_result['commentary'],
                'success': commentary_result['success']
            })
        
        return results