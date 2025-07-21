import requests
import json
from typing import Dict, List
from config import Config
import logging

logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self):
        self.config = Config()
    
    def generate_commentary_and_analysis(self, news_item: Dict) -> Dict:
        """
        为新闻生成点评和对中国行业影响分析
        """
        title = news_item.get('title', '')
        description = news_item.get('description', '')
        content = news_item.get('content', '')
        
        # 翻译英文标题为中文
        chinese_title = self._translate_title_to_chinese(title)
        
        # 使用简单的关键词分析生成点评（免费方案）
        commentary = self._generate_simple_commentary(title, description)
        china_impact = self._analyze_china_impact(title, description, content)
        
        return {
            'chinese_title': chinese_title,
            'commentary': commentary,
            'china_impact_analysis': china_impact
        }
    
    def _translate_title_to_chinese(self, title: str) -> str:
        """
        将英文标题翻译为中文（基于关键词映射）
        """
        if not title:
            return title
            
        # 常用AI相关词汇翻译表
        translations = {
            # 公司名称
            'OpenAI': 'OpenAI',
            'Google': '谷歌',
            'Microsoft': '微软',
            'Meta': 'Meta',
            'Apple': '苹果',
            'Amazon': '亚马逊',
            'Tesla': '特斯拉',
            'NVIDIA': '英伟达',
            'Anthropic': 'Anthropic',
            
            # AI技术词汇
            'Artificial Intelligence': '人工智能',
            'AI': 'AI',
            'Machine Learning': '机器学习',
            'Deep Learning': '深度学习',
            'Neural Network': '神经网络',
            'Large Language Model': '大语言模型',
            'LLM': '大语言模型',
            'ChatGPT': 'ChatGPT',
            'GPT': 'GPT',
            'GPT-4': 'GPT-4',
            'GPT-5': 'GPT-5',
            'Gemini': 'Gemini',
            'Bard': 'Bard',
            'Copilot': 'Copilot',
            
            # 动作词汇
            'Launches': '发布',
            'Releases': '发布',
            'Announces': '宣布',
            'Introduces': '推出',
            'Unveils': '揭晓',
            'Updates': '更新',
            'Improves': '改进',
            'Enhances': '增强',
            'Develops': '开发',
            'Creates': '创建',
            'Builds': '构建',
            
            # 技术特性
            'Breakthrough': '突破',
            'Innovation': '创新',
            'Revolution': '革命',
            'Advanced': '先进的',
            'New': '全新',
            'Latest': '最新',
            'Next-Generation': '下一代',
            'Powerful': '强大的',
            'Smart': '智能',
            'Intelligent': '智能的',
            
            # 应用领域
            'Healthcare': '医疗',
            'Education': '教育',
            'Finance': '金融',
            'Automotive': '汽车',
            'Robotics': '机器人',
            'Gaming': '游戏',
            'Research': '研究',
            'Development': '开发',
        }
        
        # 开始翻译
        chinese_title = title
        
        # 替换关键词
        for en_word, zh_word in translations.items():
            # 不区分大小写替换
            chinese_title = chinese_title.replace(en_word, zh_word)
            chinese_title = chinese_title.replace(en_word.lower(), zh_word)
            chinese_title = chinese_title.replace(en_word.upper(), zh_word)
        
        # 如果翻译后还大量包含英文，添加中文前缀
        english_chars = sum(1 for c in chinese_title if c.isascii() and c.isalpha())
        total_chars = len(chinese_title.replace(' ', ''))
        
        if total_chars > 0 and english_chars / total_chars > 0.6:  # 如果60%以上是英文
            # 根据内容类型添加适当的中文描述
            if any(word in title.lower() for word in ['release', 'launch', 'announce']):
                chinese_title = f"🚀 最新发布：{chinese_title}"
            elif any(word in title.lower() for word in ['breakthrough', 'innovation']):
                chinese_title = f"💡 技术突破：{chinese_title}"
            elif any(word in title.lower() for word in ['update', 'improve', 'enhance']):
                chinese_title = f"🔄 重大更新：{chinese_title}"
            else:
                chinese_title = f"📰 AI资讯：{chinese_title}"
        
        return chinese_title
    
    def _generate_simple_commentary(self, title: str, description: str) -> str:
        """
        基于关键词生成简单点评
        """
        text = (title + ' ' + description).lower()
        
        # AI技术发展相关
        if any(keyword in text for keyword in ['breakthrough', 'innovation', 'advancement', 'new model']):
            return "这项AI技术突破值得关注，可能会推动行业发展进入新阶段。"
        
        # 商业应用相关
        elif any(keyword in text for keyword in ['business', 'enterprise', 'commercial', 'market']):
            return "该AI应用的商业化进展显示了技术落地的实际价值，值得产业界密切关注。"
        
        # 监管政策相关
        elif any(keyword in text for keyword in ['regulation', 'policy', 'government', 'law']):
            return "AI监管政策的变化将对整个行业生态产生深远影响，需要持续跟踪。"
        
        # 技术竞争相关
        elif any(keyword in text for keyword in ['competition', 'vs', 'rivalry', 'race']):
            return "技术竞争加剧反映了AI领域的快速发展，各方都在争夺技术制高点。"
        
        # 默认点评
        else:
            return "这一AI技术发展动向值得行业从业者关注，可能带来新的机遇与挑战。"
    
    def _analyze_china_impact(self, title: str, description: str, content: str) -> str:
        """
        分析对中国国内行业的相关影响
        """
        text = (title + ' ' + description + ' ' + content).lower()
        
        # 大模型相关
        if any(keyword in text for keyword in ['gpt', 'llm', 'large language model', 'chatbot']):
            return """对中国影响：
1. 技术追赶：促进国内大模型技术发展，加速产业升级
2. 商业机会：为国内AI企业提供新的商业模式参考
3. 监管思考：可能推动相关监管政策的完善和调整"""
        
        # 自动驾驶相关
        elif any(keyword in text for keyword in ['autonomous', 'self-driving', 'vehicle', 'car']):
            return """对中国影响：
1. 产业协同：推动国内汽车与AI产业深度融合
2. 基础设施：加速智能交通基础设施建设
3. 政策导向：可能影响自动驾驶相关法规制定"""
        
        # 芯片半导体相关
        elif any(keyword in text for keyword in ['chip', 'semiconductor', 'processor', 'gpu']):
            return """对中国影响：
1. 技术自主：推动国产AI芯片技术发展
2. 供应链：影响半导体产业链布局和投资方向
3. 战略重要性：凸显AI芯片在国家科技战略中的地位"""
        
        # 医疗健康相关
        elif any(keyword in text for keyword in ['health', 'medical', 'drug', 'diagnosis']):
            return """对中国影响：
1. 医疗升级：推动国内智慧医疗产业发展
2. 监管完善：促进AI医疗相关标准和规范建立
3. 投资热点：可能成为新的投资和创业方向"""
        
        # 教育相关
        elif any(keyword in text for keyword in ['education', 'learning', 'student', 'teacher']):
            return """对中国影响：
1. 教育变革：推动传统教育模式向智能化转型
2. 产业机遇：为教育科技企业带来新发展机会
3. 人才培养：影响AI相关人才培养模式和课程设计"""
        
        # 金融科技相关
        elif any(keyword in text for keyword in ['finance', 'bank', 'trading', 'fintech']):
            return """对中国影响：
1. 金融创新：推动国内金融科技应用创新
2. 风控升级：提升金融风险管理智能化水平
3. 监管适应：需要金融监管框架与AI技术协调发展"""
        
        # 默认分析
        else:
            return """对中国影响：
1. 技术借鉴：为国内AI技术发展提供参考和启发
2. 市场机遇：可能为相关产业带来新的商业机会
3. 竞争态势：需要评估对国内AI产业竞争格局的影响"""

if __name__ == "__main__":
    analyzer = AIAnalyzer()
    
    # 测试用例
    test_news = {
        'title': 'OpenAI Launches New GPT-4 Model with Advanced Capabilities',
        'description': 'The new model shows significant improvements in reasoning and multimodal understanding.',
        'content': 'OpenAI has released an updated version of GPT-4 that demonstrates enhanced capabilities...'
    }
    
    result = analyzer.generate_commentary_and_analysis(test_news)
    print("点评:", result['commentary'])
    print("\n影响分析:", result['china_impact_analysis'])