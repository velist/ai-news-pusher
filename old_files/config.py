import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GNews API配置
    GNEWS_API_KEY = os.getenv('GNEWS_API_KEY', 'c3cb6fef0f86251ada2b515017b97143')
    GNEWS_BASE_URL = 'https://gnews.io/api/v4'
    
    # 飞书配置
    FEISHU_APP_ID = os.getenv('FEISHU_APP_ID', 'cli_a8f4efb90f3a1013')
    FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET', 'lCVIsMEiXI6yaOCHa0OkFgOjWcCpy3t8')
    FEISHU_TABLE_URL = os.getenv('FEISHU_TABLE_URL', 'https://jcnew7lc4a8b.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b')
    
    # 从飞书表格URL解析出app_token和table_id
    @property
    def FEISHU_APP_TOKEN(self):
        # 从URL中提取app_token: https://xxx.feishu.cn/base/TXkMb0FBwaD52ese70ScPLn5n5b
        url = self.FEISHU_TABLE_URL
        if '/base/' in url:
            return url.split('/base/')[1].split('/')[0]
        return None
    
    # OpenAI配置（可选，用于更好的AI分析）
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # 新闻搜索配置
    NEWS_KEYWORDS = ['artificial intelligence', 'AI', 'machine learning', 'deep learning', 'neural network', 'ChatGPT', 'OpenAI', 'tech innovation']
    MAX_NEWS_COUNT = 10
    
    # 飞书API基础URL
    FEISHU_BASE_URL = 'https://open.feishu.cn/open-apis'