import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
    
    def fetch_ai_tech_news(self) -> List[Dict]:
        """
        获取AI科技相关的最新新闻
        """
        try:
            # GNews API参数
            params = {
                'apikey': self.config.GNEWS_API_KEY,
                'q': 'artificial intelligence OR AI OR machine learning OR ChatGPT OR OpenAI',
                'lang': 'en',
                'country': 'us',
                'max': self.config.MAX_NEWS_COUNT,
                'sortby': 'publishedAt'
            }
            
            url = f"{self.config.GNEWS_BASE_URL}/search"
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            processed_news = []
            for article in articles:
                news_item = {
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'content': article.get('content', ''),
                    'url': article.get('url', ''),
                    'image': article.get('image', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', ''),
                    'source_url': article.get('source', {}).get('url', '')
                }
                processed_news.append(news_item)
            
            logger.info(f"成功获取 {len(processed_news)} 条AI科技新闻")
            return processed_news
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取新闻失败: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"处理新闻数据失败: {str(e)}")
            return []
    
    def get_today_news(self) -> List[Dict]:
        """
        获取今日AI科技新闻
        """
        return self.fetch_ai_tech_news()

if __name__ == "__main__":
    fetcher = NewsFetcher()
    news = fetcher.get_today_news()
    
    print(f"获取到 {len(news)} 条新闻:")
    for i, item in enumerate(news[:3], 1):  # 显示前3条
        print(f"{i}. {item['title'][:100]}...")
        print(f"   来源: {item['source']}")
        print(f"   时间: {item['publishedAt']}")
        print("---")