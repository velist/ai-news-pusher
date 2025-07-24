#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版新闻翻译器 - 专门优化新闻标题和描述翻译质量
"""

import os
import json
import time
import urllib.request
import urllib.parse
from typing import List, Optional, Dict, Tuple
from datetime import datetime

from ..core.interfaces import ITranslationService, TranslationResult, ServiceStatus


class EnhancedNewsTranslator(ITranslationService):
    """增强版新闻翻译器，专门针对新闻内容优化"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "Qwen/Qwen2.5-7B-Instruct"):
        """初始化增强版新闻翻译器
        
        Args:
            api_key: 硅基流动API密钥
            model: 使用的模型名称
        """
        self.api_key = api_key or os.getenv('SILICONFLOW_API_KEY')
        self.model = model
        self.base_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.max_retries = 3
        self.retry_delay = 1.0
        
        if not self.api_key:
            raise ValueError("硅基流动API密钥未配置，请设置SILICONFLOW_API_KEY环境变量")
        
        # 专业术语映射表 - 扩展版
        self.tech_terms = {
            # AI和机器学习
            'OpenAI': 'OpenAI',
            'ChatGPT': 'ChatGPT', 
            'GPT-4': 'GPT-4',
            'GPT-5': 'GPT-5',
            'GPT-4o': 'GPT-4o',
            'Claude': 'Claude',
            'Gemini': 'Gemini',
            'Bard': 'Bard',
            'AI': '人工智能',
            'artificial intelligence': '人工智能',
            'machine learning': '机器学习',
            'deep learning': '深度学习',
            'neural network': '神经网络',
            'transformer': 'Transformer',
            'LLM': '大语言模型',
            'large language model': '大语言模型',
            'generative AI': '生成式AI',
            'AGI': '通用人工智能',
            'computer vision': '计算机视觉',
            'natural language processing': '自然语言处理',
            'NLP': '自然语言处理',
            'reinforcement learning': '强化学习',
            
            # 区块链和加密货币
            'blockchain': '区块链',
            'cryptocurrency': '加密货币',
            'crypto': '加密货币',
            'bitcoin': '比特币',
            'Bitcoin': '比特币',
            'BTC': '比特币',
            'ethereum': '以太坊',
            'Ethereum': '以太坊',
            'ETH': '以太坊',
            'DeFi': '去中心化金融',
            'NFT': '非同质化代币',
            'Web3': 'Web3',
            'smart contract': '智能合约',
            'mining': '挖矿',
            'wallet': '钱包',
            'exchange': '交易所',
            'staking': '质押',
            'yield farming': '流动性挖矿',
            
            # 元宇宙和XR技术
            'metaverse': '元宇宙',
            'VR': '虚拟现实',
            'virtual reality': '虚拟现实',
            'AR': '增强现实',
            'augmented reality': '增强现实',
            'MR': '混合现实',
            'mixed reality': '混合现实',
            'XR': '扩展现实',
            'extended reality': '扩展现实',
            
            # 云计算和基础设施
            'cloud computing': '云计算',
            'cloud': '云',
            'serverless': '无服务器',
            'microservices': '微服务',
            'containerization': '容器化',
            'DevOps': 'DevOps',
            'CI/CD': '持续集成/持续部署',
            'edge computing': '边缘计算',
            'CDN': '内容分发网络',
            
            # 数据和分析
            'big data': '大数据',
            'data science': '数据科学',
            'analytics': '分析',
            'business intelligence': '商业智能',
            'BI': '商业智能',
            'data mining': '数据挖掘',
            'predictive analytics': '预测分析',
            
            # 物联网和连接技术
            'IoT': '物联网',
            'Internet of Things': '物联网',
            '5G': '5G',
            '6G': '6G',
            'WiFi 6': 'WiFi 6',
            'WiFi 7': 'WiFi 7',
            'Bluetooth': '蓝牙',
            'NFC': '近场通信',
            
            # 新兴技术
            'quantum computing': '量子计算',
            'quantum': '量子',
            'cybersecurity': '网络安全',
            'cyber security': '网络安全',
            'robotics': '机器人技术',
            'automation': '自动化',
            'autonomous': '自主',
            'self-driving': '自动驾驶',
            'electric vehicle': '电动汽车',
            'EV': '电动汽车',
            'renewable energy': '可再生能源',
            'solar': '太阳能',
            'battery': '电池',
            
            # 金融科技
            'fintech': '金融科技',
            'digital payment': '数字支付',
            'mobile payment': '移动支付',
            'e-commerce': '电子商务',
            'marketplace': '市场平台',
            'subscription': '订阅',
            'SaaS': '软件即服务',
            'PaaS': '平台即服务',
            'IaaS': '基础设施即服务',
            
            # 商业和投资
            'startup': '初创公司',
            'unicorn': '独角兽公司',
            'IPO': '首次公开募股',
            'venture capital': '风险投资',
            'VC': '风险投资',
            'private equity': '私募股权',
            'merger': '合并',
            'acquisition': '收购',
            'M&A': '并购',
            'valuation': '估值',
            'funding': '融资',
            'Series A': 'A轮融资',
            'Series B': 'B轮融资',
            'Series C': 'C轮融资',
            
            # 地理和地区
            'Silicon Valley': '硅谷',
            'Wall Street': '华尔街',
            'NASDAQ': '纳斯达克',
            'NYSE': '纽约证券交易所',
            
            # 主要科技公司
            'Tesla': '特斯拉',
            'SpaceX': 'SpaceX',
            'Meta': 'Meta',
            'Google': '谷歌',
            'Alphabet': 'Alphabet',
            'Microsoft': '微软',
            'Apple': '苹果',
            'Amazon': '亚马逊',
            'Netflix': '奈飞',
            'Uber': '优步',
            'Airbnb': 'Airbnb',
            'PayPal': 'PayPal',
            'Salesforce': 'Salesforce',
            'Oracle': '甲骨文',
            'IBM': 'IBM',
            'Intel': '英特尔',
            'AMD': 'AMD',
            'NVIDIA': '英伟达',
            'Qualcomm': '高通',
            'Samsung': '三星',
            'TSMC': '台积电',
            
            # 游戏和娱乐
            'PlayStation': 'PlayStation',
            'PS5': 'PS5',
            'Xbox': 'Xbox',
            'Nintendo': '任天堂',
            'Switch': 'Switch',
            'Steam': 'Steam',
            'Epic Games': 'Epic Games',
            'Fortnite': '堡垒之夜',
            'Minecraft': '我的世界',
            'esports': '电子竞技',
            'gaming': '游戏',
            'streamer': '主播',
            'Twitch': 'Twitch',
            'YouTube Gaming': 'YouTube Gaming',
            
            # 社交媒体和通信
            'TikTok': 'TikTok',
            'YouTube': 'YouTube',
            'Twitter': '推特',
            'X': 'X',
            'Facebook': '脸书',
            'Instagram': 'Instagram',
            'WhatsApp': 'WhatsApp',
            'Telegram': 'Telegram',
            'Discord': 'Discord',
            'Snapchat': 'Snapchat',
            'LinkedIn': '领英',
            'Reddit': 'Reddit',
            'Pinterest': 'Pinterest',
            
            # 工作和协作工具
            'Zoom': 'Zoom',
            'Teams': 'Teams',
            'Slack': 'Slack',
            'Notion': 'Notion',
            'Figma': 'Figma',
            'Canva': 'Canva',
            'Dropbox': 'Dropbox',
            'Google Drive': 'Google Drive',
            'OneDrive': 'OneDrive',
            
            # 开发和技术工具
            'GitHub': 'GitHub',
            'GitLab': 'GitLab',
            'Docker': 'Docker',
            'Kubernetes': 'Kubernetes',
            'Jenkins': 'Jenkins',
            'Terraform': 'Terraform',
            'React': 'React',
            'Vue': 'Vue',
            'Angular': 'Angular',
            'Node.js': 'Node.js',
            'Python': 'Python',
            'JavaScript': 'JavaScript',
            'TypeScript': 'TypeScript',
            'Java': 'Java',
            'C++': 'C++',
            'Go': 'Go',
            'Rust': 'Rust',
            
            # 云服务平台
            'AWS': 'AWS',
            'Amazon Web Services': '亚马逊云服务',
            'Azure': 'Azure',
            'Microsoft Azure': '微软Azure',
            'GCP': 'GCP',
            'Google Cloud': '谷歌云',
            'Alibaba Cloud': '阿里云',
            'Tencent Cloud': '腾讯云',
            
            # 操作系统和平台
            'Windows': 'Windows',
            'macOS': 'macOS',
            'iOS': 'iOS',
            'Android': 'Android',
            'Linux': 'Linux',
            'Ubuntu': 'Ubuntu',
            'Chrome OS': 'Chrome OS'
        }
        
        # 新闻类别特定的翻译策略
        self.category_strategies = {
            'AI科技': {
                'focus': '技术创新、产品发布、行业影响',
                'tone': '专业、准确、前瞻性',
                'keywords': ['AI', '人工智能', '机器学习', '深度学习', '算法', '模型']
            },
            '游戏科技': {
                'focus': '游戏体验、硬件性能、市场表现',
                'tone': '生动、吸引人、娱乐性',
                'keywords': ['游戏', '主机', '体验', '玩家', '发布', '更新']
            },
            '经济金融': {
                'focus': '市场动态、投资机会、风险评估',
                'tone': '客观、严谨、数据导向',
                'keywords': ['市场', '投资', '股价', '收益', '增长', '风险']
            },
            '科技创新': {
                'focus': '技术突破、产品创新、行业变革',
                'tone': '创新、前沿、影响力',
                'keywords': ['创新', '技术', '突破', '发布', '升级', '变革']
            }
        }
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return f"enhanced_news_{self.model.split('/')[-1]}"
    
    def _create_title_translation_prompt(self, title: str, category: str = "") -> str:
        """创建标题翻译的专门提示词"""
        
        # 获取类别特定策略
        strategy = self.category_strategies.get(category, {
            'focus': '准确传达核心信息',
            'tone': '客观、专业',
            'keywords': ['新闻', '资讯', '动态']
        })
        
        # 根据类别生成特定的翻译指导
        category_guidance = self._get_category_specific_guidance(category)
        
        prompt = f"""你是一位专业的科技新闻标题翻译专家。请将以下英文新闻标题翻译成中文，要求：

【翻译原则】
1. 准确性：保持原文的核心信息和关键事实，不能遗漏重要信息
2. 自然性：使用符合中文表达习惯的语言，避免直译和生硬表达
3. 吸引力：保持新闻标题的吸引力和可读性，适合中文读者
4. 专业性：正确翻译专业术语和公司名称，保持行业准确性

【类别特点】{category}
- 关注重点：{strategy['focus']}
- 语言风格：{strategy['tone']}
- 关键词汇：{', '.join(strategy['keywords'])}

{category_guidance}

【专业术语处理规则】
- 知名品牌保持原名：OpenAI, ChatGPT, Tesla, Meta, Google等
- 技术术语使用标准中文：AI→人工智能, blockchain→区块链, VR→虚拟现实
- 数字信息保持原样：价格、日期、百分比、版本号等
- 公司名称使用通用中文名：Google→谷歌, Microsoft→微软, Apple→苹果

【翻译质量要求】
- 标题长度适中，通常15-30个中文字符
- 突出核心信息，避免冗余表达
- 保持时效性和新闻价值
- 符合中文新闻标题的表达习惯

【格式要求】
只返回翻译后的中文标题，不要添加任何解释、引号或其他标点。

英文标题：{title}

中文标题："""
        
        return prompt
    
    def _get_category_specific_guidance(self, category: str) -> str:
        """获取类别特定的翻译指导"""
        guidance_map = {
            'AI科技': """
【AI科技类别特殊要求】
- 突出技术突破和创新点：如"突破性进展"、"重大更新"、"全新功能"
- 强调应用场景和影响：如"改变行业"、"提升效率"、"用户体验"
- 保持技术术语准确性：GPT-4→GPT-4, LLM→大语言模型, AGI→通用人工智能
- 体现前瞻性和重要性：如"引领未来"、"颠覆性"、"里程碑"
- 常用表达：发布、推出、升级、优化、集成、赋能""",
            
            '游戏科技': """
【游戏科技类别特殊要求】
- 突出游戏体验和性能：如"沉浸式体验"、"流畅运行"、"画质提升"
- 强调娱乐性和吸引力：如"震撼登场"、"精彩呈现"、"玩家期待"
- 保持游戏术语准确性：PlayStation→PlayStation, Xbox→Xbox, Switch→Switch
- 体现市场表现和影响：如"热销"、"好评如潮"、"引发热议"
- 常用表达：发售、上线、更新、扩展、联动、竞技""",
            
            '经济金融': """
【经济金融类别特殊要求】
- 突出市场动态和数据：如"股价上涨"、"市值突破"、"业绩增长"
- 强调投资价值和风险：如"投资机会"、"风险提示"、"收益预期"
- 保持金融术语准确性：IPO→首次公开募股, VC→风险投资, M&A→并购
- 体现客观性和数据支撑：如"数据显示"、"分析师预测"、"财报披露"
- 常用表达：融资、上市、收购、增长、下跌、预期""",
            
            '科技创新': """
【科技创新类别特殊要求】
- 突出创新性和技术价值：如"创新突破"、"技术革新"、"产品升级"
- 强调行业影响和变革：如"行业变革"、"市场领先"、"竞争优势"
- 保持科技术语准确性：云计算→云计算, 5G→5G, IoT→物联网
- 体现发展趋势和前景：如"未来趋势"、"发展前景"、"市场潜力"
- 常用表达：推出、发布、创新、升级、整合、拓展"""
        }
        
        return guidance_map.get(category, """
【通用科技新闻要求】
- 保持客观准确的表达
- 突出新闻价值和时效性
- 使用标准的科技术语翻译
- 体现专业性和可读性""")
    
    
    def _create_description_translation_prompt(self, description: str, title: str = "", category: str = "") -> str:
        """创建描述翻译的专门提示词"""
        
        strategy = self.category_strategies.get(category, {
            'focus': '完整传达新闻内容',
            'tone': '客观、详细',
            'keywords': ['详情', '内容', '信息']
        })
        
        context_info = f"\n标题参考：{title}" if title else ""
        category_guidance = self._get_description_category_guidance(category)
        
        prompt = f"""你是一位专业的科技新闻内容翻译专家。请将以下英文新闻描述翻译成中文，要求：

【翻译原则】
1. 完整性：保持原文的所有重要信息，不能遗漏关键细节
2. 连贯性：确保段落逻辑清晰，上下文连贯，语义流畅
3. 准确性：专业术语和关键信息准确翻译，保持事实准确
4. 可读性：使用自然流畅的中文表达，符合中文阅读习惯

【类别特点】{category}
- 内容重点：{strategy['focus']}
- 表达风格：{strategy['tone']}
- 核心词汇：{', '.join(strategy['keywords'])}{context_info}

{category_guidance}

【专业术语处理规则】
- 技术术语使用标准中文翻译：AI→人工智能, machine learning→机器学习
- 品牌名称保持原名或使用通用中文名：Google→谷歌, Microsoft→微软
- 产品名称通常保持英文：ChatGPT, iPhone, PlayStation等
- 数字信息保持原样：价格、日期、百分比、统计数据等

【文本结构处理】
- 保持原文的段落结构和逻辑层次
- 如有多个段落，用空行分隔
- 保持列表、引用等特殊格式
- 确保句子间的逻辑关系清晰

【翻译质量要求】
- 避免直译，使用自然的中文表达
- 保持新闻描述的客观性和准确性
- 确保信息传达的完整性和准确性
- 适合中文读者的阅读习惯

【格式要求】
只返回翻译后的中文内容，保持原有的段落结构，不要添加任何解释或标记。

英文描述：{description}

中文描述："""
        
        return prompt
    
    def _get_description_category_guidance(self, category: str) -> str:
        """获取描述翻译的类别特定指导"""
        guidance_map = {
            'AI科技': """
【AI科技描述翻译特殊要求】
- 技术细节准确翻译：模型参数、算法原理、性能指标
- 应用场景清晰描述：具体用途、使用方法、效果展示
- 行业影响深度分析：对相关行业、用户、市场的影响
- 发展趋势前瞻表达：技术发展方向、未来可能性
- 关键术语：训练、推理、部署、优化、集成、赋能、智能化""",
            
            '游戏科技': """
【游戏科技描述翻译特殊要求】
- 游戏体验生动描述：画面效果、操作感受、沉浸体验
- 技术规格准确翻译：硬件配置、性能参数、兼容性
- 市场表现客观报道：销量数据、用户反馈、行业评价
- 娱乐价值突出表达：趣味性、可玩性、社交性
- 关键术语：发售、更新、扩展包、多人模式、竞技、主机""",
            
            '经济金融': """
【经济金融描述翻译特殊要求】
- 财务数据精确翻译：收入、利润、市值、增长率等
- 市场分析客观表述：趋势分析、风险评估、投资建议
- 商业策略清晰说明：业务模式、发展计划、竞争策略
- 监管政策准确解读：法规变化、合规要求、政策影响
- 关键术语：融资、估值、上市、并购、股东、董事会""",
            
            '科技创新': """
【科技创新描述翻译特殊要求】
- 创新点突出描述：技术突破、产品特色、差异化优势
- 应用价值深入阐述：实际用途、解决问题、提升效率
- 市场前景合理预测：发展潜力、商业价值、竞争优势
- 技术原理适度解释：工作原理、技术架构、实现方式
- 关键术语：创新、突破、升级、整合、优化、变革"""
        }
        
        return guidance_map.get(category, """
【通用科技新闻描述要求】
- 保持内容的客观性和准确性
- 突出新闻的价值和意义
- 使用标准的科技术语翻译
- 确保信息传达的完整性""")
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本，替换专业术语"""
        processed_text = text
        
        # 按长度排序，优先替换长术语
        sorted_terms = sorted(self.tech_terms.items(), key=lambda x: len(x[0]), reverse=True)
        
        for en_term, zh_term in sorted_terms:
            # 使用词边界匹配，避免部分匹配
            import re
            pattern = r'\b' + re.escape(en_term) + r'\b'
            processed_text = re.sub(pattern, zh_term, processed_text, flags=re.IGNORECASE)
        
        return processed_text
    
    def _make_request(self, messages: List[Dict]) -> dict:
        """发起API请求"""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,  # 更低温度确保翻译一致性
            "max_tokens": 2048,
            "top_p": 0.8,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for attempt in range(self.max_retries):
            try:
                data = json.dumps(payload).encode('utf-8')
                request = urllib.request.Request(
                    self.base_url,
                    data=data,
                    headers=headers
                )
                
                with urllib.request.urlopen(request, timeout=30) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                if 'error' in result:
                    error = result['error']
                    error_msg = f"{error.get('type', 'Unknown')}: {error.get('message', 'Unknown error')}"
                    
                    if attempt < self.max_retries - 1:
                        print(f"API错误 (尝试 {attempt + 1}/{self.max_retries}): {error_msg}")
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        raise Exception(f"API错误: {error_msg}")
                
                return result
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    print(f"请求失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}")
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    raise e
    
    def _calculate_enhanced_confidence(self, original: str, translated: str, 
                                     translation_type: str = "general") -> float:
        """计算增强的翻译置信度"""
        if not translated or not translated.strip():
            return 0.0
        
        base_confidence = 0.88  # 增强版翻译器基础置信度更高
        
        # 基于翻译类型调整
        if translation_type == "title":
            base_confidence += 0.05  # 标题翻译通常更准确
        elif translation_type == "description":
            base_confidence += 0.02  # 描述翻译稍微复杂
        
        # 1. 长度比例评估
        if len(original) > 0:
            length_ratio = len(translated) / len(original)
            if translation_type == "title":
                # 标题的合理长度比例（中文通常比英文短）
                if 0.5 <= length_ratio <= 1.8:
                    base_confidence += 0.06
                elif 0.3 <= length_ratio <= 2.5:
                    base_confidence += 0.03
                else:
                    base_confidence -= 0.10
            else:
                # 描述的合理长度比例
                if 0.6 <= length_ratio <= 1.5:
                    base_confidence += 0.05
                elif 0.4 <= length_ratio <= 2.0:
                    base_confidence += 0.02
                else:
                    base_confidence -= 0.08
        
        # 2. 专业术语保留检查
        tech_term_preserved = 0
        tech_term_total = 0
        
        for en_term, zh_term in self.tech_terms.items():
            if en_term.lower() in original.lower():
                tech_term_total += 1
                # 检查是否正确保留或翻译
                if (en_term in translated or 
                    zh_term in translated or 
                    en_term.lower() in translated.lower()):
                    tech_term_preserved += 1
        
        if tech_term_total > 0:
            preservation_rate = tech_term_preserved / tech_term_total
            base_confidence += preservation_rate * 0.08
        
        # 3. 中文表达质量检查
        chinese_char_count = sum(1 for char in translated if '\u4e00' <= char <= '\u9fff')
        if len(translated) > 0:
            chinese_ratio = chinese_char_count / len(translated)
            if chinese_ratio >= 0.4:  # 至少40%中文字符
                base_confidence += 0.04
            elif chinese_ratio >= 0.2:  # 至少20%中文字符
                base_confidence += 0.02
            else:
                base_confidence -= 0.05  # 中文字符太少可能翻译有问题
        
        # 4. 标题特殊质量检查
        if translation_type == "title":
            # 检查标题是否过长或过短
            if 8 <= len(translated) <= 35:  # 合理的中文标题长度
                base_confidence += 0.03
            elif len(translated) < 5 or len(translated) > 50:
                base_confidence -= 0.08
            
            # 检查是否包含新闻标题常用词汇
            news_indicators = ['发布', '推出', '宣布', '上线', '更新', '升级', '突破', '创新', 
                             '增长', '下跌', '收购', '合作', '竞争', '市场', '用户', '功能']
            if any(indicator in translated for indicator in news_indicators):
                base_confidence += 0.02
        
        # 5. 描述特殊质量检查
        elif translation_type == "description":
            # 检查段落结构
            if '\n' in translated or '。' in translated:  # 包含段落或句子结构
                base_confidence += 0.02
            
            # 检查是否保持了逻辑连贯性（简单检查）
            if len(translated.split('。')) >= 2:  # 至少包含两个句子
                base_confidence += 0.02
        
        # 6. 错误模式检查（降低置信度）
        error_patterns = [
            '翻译：',  # 可能包含提示词残留
            '中文：',
            '英文：',
            'Translation:',
            '以下是',
            '请注意',
            '根据',
            '翻译结果'
        ]
        
        for pattern in error_patterns:
            if pattern in translated:
                base_confidence -= 0.15
                break
        
        # 7. 重复内容检查
        words = translated.split()
        if len(words) > 1:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > 0.3:  # 重复率过高
                base_confidence -= 0.10
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _validate_title_quality(self, original_title: str, translated_title: str, category: str = "") -> Tuple[str, float]:
        """验证和优化标题翻译质量"""
        if not translated_title or not translated_title.strip():
            return "", 0.0
        
        cleaned_title = translated_title.strip()
        quality_score = 1.0
        
        # 1. 清理格式问题
        cleanup_patterns = [
            ('中文标题：', ''),
            ('翻译：', ''),
            ('标题：', ''),
            ('"', ''),
            ('"', ''),
            ('"', ''),
            ('「', ''),
            ('」', ''),
        ]
        
        for pattern, replacement in cleanup_patterns:
            if cleaned_title.startswith(pattern):
                cleaned_title = cleaned_title[len(pattern):].strip()
                quality_score -= 0.05
        
        # 2. 长度检查和优化
        if len(cleaned_title) > 40:  # 标题过长
            # 尝试提取核心信息
            sentences = cleaned_title.split('，')
            if len(sentences) > 1:
                cleaned_title = sentences[0]  # 取第一个主要信息
                quality_score -= 0.08
        elif len(cleaned_title) < 5:  # 标题过短
            quality_score -= 0.15
        
        # 3. 专业术语一致性检查
        for en_term, zh_term in self.tech_terms.items():
            if en_term.lower() in original_title.lower():
                # 检查翻译中是否正确处理了这个术语
                if not (en_term in cleaned_title or zh_term in cleaned_title):
                    # 术语丢失，尝试修复
                    if zh_term not in cleaned_title:
                        # 简单替换策略
                        import re
                        pattern = r'\b' + re.escape(en_term) + r'\b'
                        if re.search(pattern, original_title, re.IGNORECASE):
                            # 如果原文中有这个术语，确保翻译中也有
                            quality_score -= 0.05
        
        # 4. 类别特定优化
        if category == 'AI科技':
            # AI新闻标题优化
            if 'AI' in original_title and '人工智能' not in cleaned_title and 'AI' not in cleaned_title:
                cleaned_title = cleaned_title.replace('智能', 'AI')
                quality_score += 0.02
        elif category == '游戏科技':
            # 游戏新闻标题优化
            gaming_terms = ['游戏', '玩家', '主机', '发售', '更新']
            if not any(term in cleaned_title for term in gaming_terms):
                quality_score -= 0.05
        elif category == '经济金融':
            # 金融新闻标题优化
            finance_terms = ['股价', '市值', '投资', '融资', '收益', '增长']
            if not any(term in cleaned_title for term in finance_terms):
                quality_score -= 0.05
        
        # 5. 新闻价值词汇检查
        news_value_words = ['发布', '推出', '宣布', '突破', '创新', '增长', '下跌', '合作', '竞争']
        if any(word in cleaned_title for word in news_value_words):
            quality_score += 0.03
        
        return cleaned_title, max(quality_score, 0.0)
    
    def translate_news_title(self, title: str, category: str = "") -> TranslationResult:
        """专门翻译新闻标题"""
        if not title or not title.strip():
            return TranslationResult(
                original_text=title,
                translated_text="",
                source_language="en",
                target_language="zh",
                service_name=self.get_service_name(),
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message="标题为空"
            )
        
        try:
            # 预处理专业术语
            processed_title = self._preprocess_text(title)
            
            # 创建专门的标题翻译提示
            prompt = self._create_title_translation_prompt(processed_title, category)
            messages = [{"role": "user", "content": prompt}]
            
            result = self._make_request(messages)
            
            if 'choices' in result and result['choices']:
                raw_translated_text = result['choices'][0]['message']['content'].strip()
                
                # 使用质量验证和优化
                validated_title, quality_adjustment = self._validate_title_quality(
                    title, raw_translated_text, category
                )
                
                if not validated_title:
                    raise Exception("标题翻译验证失败")
                
                # 计算置信度（结合质量调整）
                base_confidence = self._calculate_enhanced_confidence(
                    title, validated_title, "title"
                )
                final_confidence = base_confidence * quality_adjustment
                
                return TranslationResult(
                    original_text=title,
                    translated_text=validated_title,
                    source_language="en",
                    target_language="zh",
                    service_name=self.get_service_name(),
                    confidence_score=final_confidence,
                    timestamp=datetime.now()
                )
            else:
                raise Exception("翻译结果为空")
                
        except Exception as e:
            return TranslationResult(
                original_text=title,
                translated_text="",
                source_language="en",
                target_language="zh",
                service_name=self.get_service_name(),
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def translate_news_description(self, description: str, title: str = "", category: str = "") -> TranslationResult:
        """专门翻译新闻描述，支持长文本智能分段处理"""
        if not description or not description.strip():
            return TranslationResult(
                original_text=description,
                translated_text="",
                source_language="en",
                target_language="zh",
                service_name=self.get_service_name(),
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message="描述为空"
            )
        
        try:
            # 预处理专业术语
            processed_description = self._preprocess_text(description)
            
            # 检查是否需要分段处理
            if len(processed_description) > 800:  # 长文本分段处理
                return self._translate_long_description(processed_description, title, category)
            else:
                return self._translate_single_description(processed_description, title, category)
                
        except Exception as e:
            return TranslationResult(
                original_text=description,
                translated_text="",
                source_language="en",
                target_language="zh",
                service_name=self.get_service_name(),
                confidence_score=0.0,
                timestamp=datetime.now(),
                error_message=str(e)
            )
    
    def _validate_description_quality(self, original_desc: str, translated_desc: str, 
                                    title: str = "", category: str = "") -> Tuple[str, float]:
        """验证和优化描述翻译质量"""
        if not translated_desc or not translated_desc.strip():
            return "", 0.0
        
        cleaned_desc = translated_desc.strip()
        quality_score = 1.0
        
        # 1. 清理格式问题
        cleanup_patterns = [
            ('中文描述：', ''),
            ('翻译：', ''),
            ('描述：', ''),
            ('内容：', ''),
        ]
        
        for pattern, replacement in cleanup_patterns:
            if cleaned_desc.startswith(pattern):
                cleaned_desc = cleaned_desc[len(pattern):].strip()
                quality_score -= 0.05
        
        # 2. 段落结构检查
        paragraphs = [p.strip() for p in cleaned_desc.split('\n') if p.strip()]
        if len(paragraphs) > 1:
            # 多段落内容，检查段落间的连贯性
            quality_score += 0.03
        
        # 3. 长度合理性检查
        length_ratio = len(cleaned_desc) / len(original_desc) if len(original_desc) > 0 else 0
        if 0.5 <= length_ratio <= 2.0:  # 合理的长度比例
            quality_score += 0.05
        elif length_ratio < 0.3:  # 翻译过短，可能信息丢失
            quality_score -= 0.15
        elif length_ratio > 3.0:  # 翻译过长，可能有冗余
            quality_score -= 0.10
        
        # 4. 专业术语一致性检查
        term_consistency_score = 0
        term_count = 0
        
        for en_term, zh_term in self.tech_terms.items():
            if en_term.lower() in original_desc.lower():
                term_count += 1
                if en_term in cleaned_desc or zh_term in cleaned_desc:
                    term_consistency_score += 1
        
        if term_count > 0:
            consistency_ratio = term_consistency_score / term_count
            quality_score += consistency_ratio * 0.08
        
        # 5. 句子完整性检查
        sentences = [s.strip() for s in cleaned_desc.split('。') if s.strip()]
        if len(sentences) >= 2:  # 至少包含完整的句子
            quality_score += 0.03
        
        # 6. 类别特定质量检查
        category_bonus = self._check_category_specific_quality(cleaned_desc, category)
        quality_score += category_bonus
        
        # 7. 错误模式检查
        error_patterns = [
            '翻译：',
            '中文：',
            '英文：',
            'Translation:',
            '以下是翻译',
            '根据原文',
            '翻译结果如下'
        ]
        
        for pattern in error_patterns:
            if pattern in cleaned_desc:
                quality_score -= 0.12
                break
        
        # 8. 重复内容检查
        words = cleaned_desc.split()
        if len(words) > 5:
            unique_words = set(words)
            repetition_ratio = 1 - (len(unique_words) / len(words))
            if repetition_ratio > 0.4:  # 重复率过高
                quality_score -= 0.15
        
        return cleaned_desc, max(quality_score, 0.0)
    
    def _check_category_specific_quality(self, translated_desc: str, category: str) -> float:
        """检查类别特定的翻译质量"""
        bonus = 0.0
        
        if category == 'AI科技':
            ai_terms = ['人工智能', 'AI', '机器学习', '深度学习', '算法', '模型', '训练', '推理']
            if any(term in translated_desc for term in ai_terms):
                bonus += 0.02
        elif category == '游戏科技':
            gaming_terms = ['游戏', '玩家', '体验', '性能', '画面', '操作', '主机', '平台']
            if any(term in translated_desc for term in gaming_terms):
                bonus += 0.02
        elif category == '经济金融':
            finance_terms = ['市场', '投资', '收益', '增长', '股价', '融资', '估值', '业绩']
            if any(term in translated_desc for term in finance_terms):
                bonus += 0.02
        elif category == '科技创新':
            tech_terms = ['技术', '创新', '产品', '功能', '升级', '优化', '解决方案', '应用']
            if any(term in translated_desc for term in tech_terms):
                bonus += 0.02
        
        return bonus
    
    def _translate_single_description(self, description: str, title: str = "", category: str = "") -> TranslationResult:
        """翻译单段描述"""
        try:
            # 创建专门的描述翻译提示
            prompt = self._create_description_translation_prompt(description, title, category)
            messages = [{"role": "user", "content": prompt}]
            
            result = self._make_request(messages)
            
            if 'choices' in result and result['choices']:
                raw_translated_text = result['choices'][0]['message']['content'].strip()
                
                # 使用质量验证和优化
                validated_desc, quality_adjustment = self._validate_description_quality(
                    description, raw_translated_text, title, category
                )
                
                if not validated_desc:
                    raise Exception("描述翻译验证失败")
                
                # 计算置信度（结合质量调整）
                base_confidence = self._calculate_enhanced_confidence(
                    description, validated_desc, "description"
                )
                final_confidence = base_confidence * quality_adjustment
                
                return TranslationResult(
                    original_text=description,
                    translated_text=validated_desc,
                    source_language="en",
                    target_language="zh",
                    service_name=self.get_service_name(),
                    confidence_score=final_confidence,
                    timestamp=datetime.now()
                )
            else:
                raise Exception("翻译结果为空")
                
        except Exception as e:
            raise e
    
    def _translate_long_description(self, description: str, title: str = "", category: str = "") -> TranslationResult:
        """智能分段翻译长文本描述"""
        try:
            # 智能分段
            segments = self._smart_segment_text(description)
            translated_segments = []
            total_confidence = 0.0
            
            print(f"📄 长文本分为 {len(segments)} 段进行翻译")
            
            for i, segment in enumerate(segments):
                if not segment.strip():
                    translated_segments.append("")
                    continue
                
                try:
                    # 为每段创建上下文感知的翻译提示
                    segment_prompt = self._create_segment_translation_prompt(
                        segment, title, category, i, len(segments)
                    )
                    messages = [{"role": "user", "content": segment_prompt}]
                    
                    result = self._make_request(messages)
                    
                    if 'choices' in result and result['choices']:
                        translated_segment = result['choices'][0]['message']['content'].strip()
                        
                        # 清理格式
                        if translated_segment.startswith('翻译：'):
                            translated_segment = translated_segment[3:].strip()
                        
                        translated_segments.append(translated_segment)
                        
                        # 计算段落置信度
                        segment_confidence = self._calculate_enhanced_confidence(
                            segment, translated_segment, "description"
                        )
                        total_confidence += segment_confidence
                        
                        print(f"✅ 第 {i+1}/{len(segments)} 段翻译完成")
                        
                        # 添加延迟避免频率限制
                        if i < len(segments) - 1:
                            time.sleep(0.2)
                    else:
                        print(f"⚠️ 第 {i+1} 段翻译失败，保留原文")
                        translated_segments.append(segment)
                        
                except Exception as e:
                    print(f"⚠️ 第 {i+1} 段翻译异常: {str(e)}")
                    translated_segments.append(segment)
            
            # 合并翻译结果
            final_translation = self._merge_translated_segments(translated_segments)
            
            # 计算平均置信度
            avg_confidence = total_confidence / len(segments) if segments else 0.0
            
            return TranslationResult(
                original_text=description,
                translated_text=final_translation,
                source_language="en",
                target_language="zh",
                service_name=self.get_service_name(),
                confidence_score=avg_confidence,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            raise e
    
    def _smart_segment_text(self, text: str) -> List[str]:
        """智能分段文本，保持逻辑完整性"""
        if len(text) <= 600:  # 短文本不需要分段
            return [text]
        
        segments = []
        
        # 1. 首先尝试按自然段落分割
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        if not paragraphs:  # 没有段落分割，按句子处理
            return self._segment_by_sentences(text)
        
        current_segment = ""
        
        for paragraph in paragraphs:
            # 检查单个段落是否过长
            if len(paragraph) > 700:
                # 单个段落过长，需要进一步分割
                if current_segment:
                    segments.append(current_segment.strip())
                    current_segment = ""
                
                # 分割长段落
                sub_segments = self._segment_long_paragraph(paragraph)
                segments.extend(sub_segments)
                continue
            
            # 检查加入当前段落后是否超长
            potential_segment = current_segment + "\n\n" + paragraph if current_segment else paragraph
            
            if len(potential_segment) <= 650:  # 合理的段落长度
                current_segment = potential_segment
            else:
                # 保存当前段落，开始新段落
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = paragraph
        
        # 添加最后一段
        if current_segment:
            segments.append(current_segment.strip())
        
        # 过滤空段落并进行最终检查
        final_segments = []
        for segment in segments:
            if segment.strip():
                # 如果段落仍然过长，进行最后的分割
                if len(segment) > 800:
                    sub_segments = self._segment_by_sentences(segment)
                    final_segments.extend(sub_segments)
                else:
                    final_segments.append(segment)
        
        return final_segments
    
    def _segment_long_paragraph(self, paragraph: str) -> List[str]:
        """分割过长的单个段落"""
        # 首先尝试按句子分割
        sentences = self._split_sentences(paragraph)
        
        if len(sentences) <= 1:
            # 只有一个句子但很长，按逗号分割
            return self._segment_by_punctuation(paragraph)
        
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            potential_segment = current_segment + " " + sentence if current_segment else sentence
            
            if len(potential_segment) <= 600:
                current_segment = potential_segment
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def _segment_by_sentences(self, text: str) -> List[str]:
        """按句子分割文本"""
        sentences = self._split_sentences(text)
        
        if len(sentences) <= 1:
            return [text]  # 无法进一步分割
        
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            potential_segment = current_segment + " " + sentence if current_segment else sentence
            
            if len(potential_segment) <= 600:
                current_segment = potential_segment
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                    current_segment = sentence
                else:
                    # 单个句子就很长，按标点符号分割
                    sub_segments = self._segment_by_punctuation(sentence)
                    segments.extend(sub_segments)
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments
    
    def _segment_by_punctuation(self, text: str) -> List[str]:
        """按标点符号分割文本（最后的分割方式）"""
        import re
        
        # 按主要标点符号分割
        parts = re.split(r'([,;:])', text)
        
        segments = []
        current_segment = ""
        
        for i in range(0, len(parts), 2):  # 跳过标点符号
            part = parts[i] if i < len(parts) else ""
            punct = parts[i + 1] if i + 1 < len(parts) else ""
            
            full_part = part + punct
            potential_segment = current_segment + full_part if current_segment else full_part
            
            if len(potential_segment) <= 600:
                current_segment = potential_segment
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = full_part
        
        if current_segment:
            segments.append(current_segment.strip())
        
        # 如果还是有过长的段落，强制按长度分割
        final_segments = []
        for segment in segments:
            if len(segment) > 700:
                # 强制按长度分割
                words = segment.split()
                temp_segment = ""
                
                for word in words:
                    if len(temp_segment + " " + word) <= 600:
                        temp_segment += " " + word if temp_segment else word
                    else:
                        if temp_segment:
                            final_segments.append(temp_segment.strip())
                        temp_segment = word
                
                if temp_segment:
                    final_segments.append(temp_segment.strip())
            else:
                final_segments.append(segment)
        
        return final_segments
    
    def _split_sentences(self, text: str) -> List[str]:
        """按句子分割文本，考虑各种句子结束标点"""
        import re
        
        # 更精确的句子分割，考虑缩写和特殊情况
        # 先处理常见的缩写，避免误分割
        text = re.sub(r'\bDr\.', 'Dr_DOT_', text)
        text = re.sub(r'\bMr\.', 'Mr_DOT_', text)
        text = re.sub(r'\bMs\.', 'Ms_DOT_', text)
        text = re.sub(r'\bInc\.', 'Inc_DOT_', text)
        text = re.sub(r'\bCorp\.', 'Corp_DOT_', text)
        text = re.sub(r'\bLtd\.', 'Ltd_DOT_', text)
        text = re.sub(r'\bCo\.', 'Co_DOT_', text)
        text = re.sub(r'\bU\.S\.', 'U_DOT_S_DOT_', text)
        text = re.sub(r'\bU\.K\.', 'U_DOT_K_DOT_', text)
        text = re.sub(r'\bE\.g\.', 'E_DOT_g_DOT_', text)
        text = re.sub(r'\bI\.e\.', 'I_DOT_e_DOT_', text)
        text = re.sub(r'\betc\.', 'etc_DOT_', text)
        
        # 按句子结束标点分割
        sentences = re.split(r'[.!?]+\s+', text)
        
        # 恢复缩写中的点号
        restored_sentences = []
        for sentence in sentences:
            if sentence.strip():
                restored = sentence.replace('_DOT_', '.')
                restored_sentences.append(restored.strip())
        
        # 如果分割结果太少，尝试其他分割方式
        if len(restored_sentences) <= 1 and len(text) > 300:
            # 尝试按分号和冒号分割
            alt_sentences = re.split(r'[;:]\s+', text)
            if len(alt_sentences) > 1:
                return [s.strip() for s in alt_sentences if s.strip()]
        
        return restored_sentences
    
    def _create_segment_translation_prompt(self, segment: str, title: str, category: str, 
                                         segment_index: int, total_segments: int) -> str:
        """为文本段落创建上下文感知的翻译提示"""
        
        strategy = self.category_strategies.get(category, {
            'focus': '完整传达新闻内容',
            'tone': '客观、详细',
            'keywords': ['详情', '内容', '信息']
        })
        
        context_info = f"\n标题参考：{title}" if title else ""
        segment_info = f"（第 {segment_index + 1}/{total_segments} 段）" if total_segments > 1 else ""
        
        prompt = f"""你是一位专业的科技新闻翻译专家。请翻译以下新闻内容片段{segment_info}，要求：

【翻译原则】
1. 保持内容的完整性和准确性
2. 确保上下文逻辑连贯
3. 使用自然流畅的中文表达
4. 保留重要的专业术语和关键信息

【类别特点】{category}
- 内容重点：{strategy['focus']}
- 表达风格：{strategy['tone']}{context_info}

【处理要求】
- 保持段落的逻辑结构
- 专业术语使用准确的中文翻译
- 保留数字、日期、引用等关键信息
- 确保翻译的连贯性和可读性

【格式要求】
只返回翻译后的中文内容，保持原有结构。

英文片段：{segment}

翻译："""
        
        return prompt
    
    def _merge_translated_segments(self, segments: List[str]) -> str:
        """合并翻译后的段落，保持逻辑连贯性"""
        if not segments:
            return ""
        
        # 简单合并，保持段落结构
        merged = []
        for segment in segments:
            if segment.strip():
                merged.append(segment.strip())
        
        return "\n\n".join(merged)
    
    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'zh') -> TranslationResult:
        """通用文本翻译接口"""
        return self.translate_news_title(text)  # 默认使用标题翻译逻辑
    
    def translate_batch(self, texts: List[str], source_lang: str = 'en', target_lang: str = 'zh') -> List[TranslationResult]:
        """批量翻译"""
        results = []
        for text in texts:
            result = self.translate_text(text, source_lang, target_lang)
            results.append(result)
            # 添加小延迟避免频率限制
            time.sleep(0.1)
        return results
    
    def get_service_status(self) -> ServiceStatus:
        """获取服务状态"""
        try:
            test_result = self.translate_news_title("AI breakthrough in technology")
            
            if test_result.error_message:
                error_msg = test_result.error_message.lower()
                if any(keyword in error_msg for keyword in ['rate', 'limit', 'quota']):
                    return ServiceStatus.DEGRADED
                elif any(keyword in error_msg for keyword in ['unauthorized', 'forbidden']):
                    return ServiceStatus.UNAVAILABLE
                else:
                    return ServiceStatus.DEGRADED
            else:
                return ServiceStatus.HEALTHY
                
        except Exception:
            return ServiceStatus.UNAVAILABLE