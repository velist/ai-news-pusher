#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI新闻自动推送系统
每日获取最新AI科技新闻并推送到飞书多维表格
"""

import sys
import os
from datetime import datetime
import logging
from typing import List, Dict

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from news_fetcher import NewsFetcher
from ai_analyzer import AIAnalyzer
from feishu_client import FeishuClient
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('news_push.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class NewsProcessor:
    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.ai_analyzer = AIAnalyzer()
        self.feishu_client = FeishuClient()
        self.config = Config()
    
    def process_and_push_news(self) -> bool:
        """
        处理并推送新闻的主要流程
        """
        try:
            logger.info("开始执行AI新闻推送任务")
            
            # 1. 获取新闻
            logger.info("正在获取AI科技新闻...")
            raw_news = self.news_fetcher.get_today_news()
            
            if not raw_news:
                logger.warning("未获取到新闻数据")
                return False
            
            logger.info(f"获取到 {len(raw_news)} 条原始新闻")
            
            # 2. 处理新闻（添加AI分析）
            logger.info("正在进行AI分析和点评...")
            processed_news = []
            
            for news_item in raw_news:
                try:
                    # 获取AI分析结果（包含中文标题翻译）
                    analysis = self.ai_analyzer.generate_commentary_and_analysis(news_item)
                    
                    # 合并数据，确保包含chinese_title
                    enhanced_news = {**news_item, **analysis}
                    processed_news.append(enhanced_news)
                    
                    logger.debug(f"完成分析: {enhanced_news.get('chinese_title', news_item.get('title', ''))[:50]}...")
                    
                except Exception as e:
                    logger.error(f"处理新闻时出错: {str(e)}")
                    # 即使分析失败，也要尝试翻译标题
                    try:
                        chinese_title = self.ai_analyzer._translate_title_to_chinese(news_item.get('title', ''))
                    except:
                        chinese_title = news_item.get('title', '')
                    
                    enhanced_news = {
                        **news_item,
                        'chinese_title': chinese_title,
                        'commentary': '暂无AI点评',
                        'china_impact_analysis': '暂无影响分析'
                    }
                    processed_news.append(enhanced_news)
            
            logger.info(f"完成 {len(processed_news)} 条新闻的AI分析")
            
            # 3. 推送到飞书
            logger.info("正在推送到飞书多维表格...")
            success = self.feishu_client.push_news_to_table(processed_news)
            
            if success:
                logger.info(f"任务完成！成功推送 {len(processed_news)} 条新闻到飞书表格")
                return True
            else:
                logger.error("推送到飞书失败")
                return False
                
        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}")
            return False
    
    def test_components(self):
        """
        测试各个组件是否正常工作
        """
        print("开始组件测试...")
        
        # 测试新闻获取
        print("1. 测试新闻获取...")
        news = self.news_fetcher.get_today_news()
        print(f"   获取到 {len(news)} 条新闻")
        
        if news:
            # 测试AI分析
            print("2. 测试AI分析...")
            analysis = self.ai_analyzer.generate_commentary_and_analysis(news[0])
            print(f"   点评: {analysis['commentary'][:50]}...")
            print(f"   影响: {analysis['china_impact_analysis'][:50]}...")
            
            # 测试飞书连接
            print("3. 测试飞书连接...")
            # 只测试获取token，不实际推送
            token = self.feishu_client._get_access_token()
            print(f"   飞书连接: {'成功' if token else '失败'}")
        
        print("组件测试完成")

def main():
    """
    主函数
    """
    processor = NewsProcessor()
    
    # 如果传入test参数，则运行测试
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        processor.test_components()
        return
    
    # 正常运行推送任务
    success = processor.process_and_push_news()
    
    if success:
        print(f"✅ AI新闻推送任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(0)
    else:
        print(f"❌ AI新闻推送任务失败 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(1)

if __name__ == "__main__":
    main()