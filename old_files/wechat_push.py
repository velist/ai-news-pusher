#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
微信公众号推送 - 生成精美的推文内容
"""

import json
from datetime import datetime

class WeChatNewsGenerator:
    def __init__(self):
        pass
    
    def generate_article_content(self, news_list):
        """生成公众号文章内容"""
        today = datetime.now()
        
        content = f"""
# 🤖 AI科技日报 | {today.strftime('%m月%d日')}

> 每日精选人工智能前沿资讯，洞察科技发展趋势

---

## 📊 今日概览

🔢 **新闻数量**: {len(news_list)} 条
📈 **重要资讯**: {len([n for n in news_list if n.get('importance', 3) >= 4])} 条
🏢 **涉及公司**: {len(set([self.extract_company(n['title']) for n in news_list]))} 家

---

## 🌟 今日亮点

"""
        
        # 按重要性排序
        sorted_news = sorted(news_list, key=lambda x: x.get('importance', 3), reverse=True)
        
        for i, news in enumerate(sorted_news[:5], 1):
            importance_stars = '⭐' * news.get('importance', 3)
            
            content += f"""
### {i}. {news['title']}

**{importance_stars} 重要程度**

{news['description']}

**💡 快速点评**: {self.generate_quick_comment(news['title'])}

**🔗 [阅读原文]({news['url']})**

---
"""
        
        content += f"""
## 📈 行业趋势

{self.generate_trend_analysis(news_list)}

---

## 🎯 明日关注

• 关注OpenAI最新动态
• 留意谷歌AI产品发布
• 观察投资市场变化
• 跟踪技术突破进展

---

<center>

**🚀 AI科技日报**

*每日8:00准时更新 | 专业AI资讯聚合*

*关注我们，不错过每一个AI发展里程碑*

</center>

---

> 📅 发布时间: {today.strftime('%Y年%m月%d日 %H:%M')}  
> 📊 数据来源: GNews AI科技新闻API  
> 🤖 内容生成: AI智能分析系统
"""
        return content
    
    def extract_company(self, title):
        """提取公司名称"""
        companies = ['OpenAI', '谷歌', 'Google', '微软', 'Microsoft', 'Meta', '苹果', 'Apple', '英伟达', 'NVIDIA']
        for company in companies:
            if company in title:
                return company
        return '其他'
    
    def generate_quick_comment(self, title):
        """生成快速点评"""
        title_lower = title.lower()
        
        if 'openai' in title_lower or 'gpt' in title_lower:
            return "OpenAI继续引领大语言模型发展，值得关注其技术突破对整个AI行业的推动作用。"
        elif 'google' in title_lower or '谷歌' in title_lower:
            return "谷歌在AI领域的持续投入显示了科技巨头对人工智能未来的信心。"
        elif 'invest' in title_lower or '投资' in title_lower:
            return "AI领域的投资动态反映了市场对人工智能商业价值的认可。"
        elif 'breakthrough' in title_lower or '突破' in title_lower:
            return "技术突破往往带来新的应用可能，可能催生新的商业模式。"
        else:
            return "该发展体现了AI技术的快速演进，值得持续关注。"
    
    def generate_trend_analysis(self, news_list):
        """生成趋势分析"""
        analysis = """
基于今日新闻，我们观察到以下趋势：

🔹 **大模型竞争加剧**: 各大科技公司持续发力，技术迭代速度加快

🔹 **应用场景扩展**: AI技术从概念验证走向实际应用，商业化进程提速

🔹 **投资热度持续**: 资本市场对AI领域保持高度关注，资金流入增加

🔹 **监管关注增强**: 政府层面对AI发展的规范化要求日益明确
"""
        return analysis
    
    def create_html_preview(self, content):
        """创建HTML预览"""
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号文章预览</title>
    <style>
        body {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', sans-serif;
            background-color: #f5f5f5;
        }}
        .article {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            line-height: 1.8;
        }}
        h1 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        h2 {{ color: #007acc; margin-top: 30px; }}
        h3 {{ color: #333; margin-top: 25px; }}
        blockquote {{ 
            background: #f8f9fa; 
            border-left: 4px solid #007acc; 
            padding: 10px 15px; 
            margin: 20px 0;
            font-style: italic;
        }}
        a {{ color: #007acc; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        center {{ margin: 30px 0; }}
        hr {{ border: none; border-top: 1px solid #eee; margin: 25px 0; }}
    </style>
</head>
<body>
    <div class="article">
        {self.markdown_to_html(content)}
    </div>
</body>
</html>"""
        return html_template
    
    def markdown_to_html(self, markdown_text):
        """简单的Markdown转HTML"""
        html = markdown_text
        
        # 转换标题
        html = html.replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>')
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        html = f'<p>{html}</p>'
        
        # 转换引用
        html = html.replace('<p>> ', '<blockquote>').replace('</p>', '</blockquote>', html.count('<p>> '))
        
        # 转换加粗
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        
        # 转换链接
        import re
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        return html

def main():
    generator = WeChatNewsGenerator()
    
    # 示例新闻数据
    sample_news = [
        {
            'title': '🚀 OpenAI发布革命性GPT-5模型',
            'description': 'OpenAI最新发布的GPT-5模型在推理能力、创意表达等方面实现显著提升，有望重新定义人工智能应用边界。',
            'url': 'https://example.com/news1',
            'importance': 5
        },
        {
            'title': '📰 谷歌AI新突破：多模态理解能力大幅提升',
            'description': '谷歌研究团队在多模态AI理解方面取得重要进展，新模型能够更好地理解图像、文本和语音的复杂关联。',
            'url': 'https://example.com/news2',
            'importance': 4
        }
    ]
    
    # 生成文章内容
    article_content = generator.generate_article_content(sample_news)
    
    # 保存为文件
    with open('docs/wechat_article.md', 'w', encoding='utf-8') as f:
        f.write(article_content)
    
    # 生成HTML预览
    html_preview = generator.create_html_preview(article_content)
    with open('docs/wechat_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_preview)
    
    print("📱 微信公众号文章生成完成！")
    print("📄 Markdown文件: docs/wechat_article.md")
    print("🌐 HTML预览: docs/wechat_preview.html")

if __name__ == "__main__":
    main()