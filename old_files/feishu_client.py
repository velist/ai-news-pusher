import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from config import Config
import logging

logger = logging.getLogger(__name__)

class FeishuClient:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self._access_token = None
        self._token_expires_at = 0
        
    def _get_access_token(self) -> str:
        """
        获取飞书访问令牌
        """
        current_time = int(time.time())
        
        # 如果token未过期，直接返回
        if self._access_token and current_time < self._token_expires_at:
            return self._access_token
            
        try:
            url = f"{self.config.FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.config.FEISHU_APP_ID,
                "app_secret": self.config.FEISHU_APP_SECRET
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                self._access_token = data.get('tenant_access_token')
                expires_in = data.get('expire', 7200)  # 默认2小时
                self._token_expires_at = current_time + expires_in - 300  # 提前5分钟刷新
                
                logger.info("飞书访问令牌获取成功")
                return self._access_token
            else:
                logger.error(f"获取飞书访问令牌失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取飞书访问令牌异常: {str(e)}")
            return None
    
    def _get_table_info(self) -> Dict:
        """
        获取多维表格信息
        """
        token = self._get_access_token()
        if not token:
            return {}
            
        app_token = self.config.FEISHU_APP_TOKEN
        if not app_token:
            logger.error("无法从URL中提取app_token")
            return {}
            
        try:
            url = f"{self.config.FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                tables = data.get('data', {}).get('items', [])
                if tables:
                    # 返回第一个表格的信息
                    return tables[0]
            
            logger.error(f"获取表格信息失败: {data}")
            return {}
            
        except Exception as e:
            logger.error(f"获取表格信息异常: {str(e)}")
            return {}
    
    def _create_table_fields(self, table_id: str) -> bool:
        """
        创建表格字段（如果不存在）
        """
        token = self._get_access_token()
        if not token:
            return False
            
        app_token = self.config.FEISHU_APP_TOKEN
        
        # 定义需要的字段
        fields = [
            {"field_name": "标题", "type": 1},  # 文本
            {"field_name": "摘要", "type": 1},  # 文本
            {"field_name": "图片", "type": 17}, # URL
            {"field_name": "点评", "type": 1},  # 文本
            {"field_name": "中国影响分析", "type": 1},  # 文本
            {"field_name": "来源链接", "type": 17}, # URL
            {"field_name": "发布时间", "type": 5},  # 日期时间
            {"field_name": "来源", "type": 1}   # 文本
        ]
        
        try:
            for field in fields:
                url = f"{self.config.FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "field_name": field["field_name"],
                    "type": field["type"]
                }
                
                response = self.session.post(url, headers=headers, json=payload)
                # 不检查响应，因为字段可能已存在
                
            logger.info("表格字段检查/创建完成")
            return True
            
        except Exception as e:
            logger.error(f"创建表格字段异常: {str(e)}")
            return False
    
    def _get_max_timestamp(self, table_id: str) -> int:
        """
        获取表格中的最大时间戳
        """
        token = self._get_access_token()
        if not token:
            return int(time.time() * 1000)
            
        app_token = self.config.FEISHU_APP_TOKEN
        
        try:
            url = f"{self.config.FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                records = data.get('data', {}).get('items', [])
                max_timestamp = int(time.time() * 1000)  # 默认当前时间
                
                for record in records:
                    update_date = record.get('fields', {}).get('更新日期', 0)
                    if isinstance(update_date, (int, float)) and update_date > max_timestamp:
                        max_timestamp = int(update_date)
                
                logger.info(f"获取到最大时间戳: {max_timestamp}")
                return max_timestamp
            else:
                logger.warning(f"获取记录失败: {data}")
                return int(time.time() * 1000)
                
        except Exception as e:
            logger.error(f"获取最大时间戳异常: {str(e)}")
            return int(time.time() * 1000)
    
    def push_news_to_table(self, news_list: List[Dict]) -> bool:
        """
        推送新闻到飞书多维表格
        """
        if not news_list:
            logger.warning("没有新闻数据可推送")
            return True
            
        # 获取表格信息
        table_info = self._get_table_info()
        if not table_info:
            logger.error("无法获取表格信息")
            return False
            
        table_id = table_info.get('table_id')
        if not table_id:
            logger.error("无法获取table_id")
            return False
            
        # 确保字段存在
        self._create_table_fields(table_id)
        
        # 获取当前最大时间戳，确保新记录显示在顶部
        max_timestamp = self._get_max_timestamp(table_id)
        
        # 推送数据，使用递增的时间戳确保正确排序
        success_count = 0
        for i, news_item in enumerate(news_list):
            # 为每条新闻分配递增的时间戳，确保最新的在最上面
            future_timestamp = max_timestamp + (len(news_list) - i) * 60000  # 每条新闻间隔1分钟
            news_item['future_timestamp'] = future_timestamp
            
            if self._add_news_record(table_id, news_item):
                success_count += 1
            time.sleep(0.5)  # 避免频率限制
            
        logger.info(f"成功推送 {success_count}/{len(news_list)} 条新闻到飞书表格")
        return success_count > 0
    
    def _add_news_record(self, table_id: str, news_item: Dict) -> bool:
        """
        添加单条新闻记录
        """
        token = self._get_access_token()
        if not token:
            return False
            
        app_token = self.config.FEISHU_APP_TOKEN
        
        try:
            url = f"{self.config.FEISHU_BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 构建记录数据 - 使用现有表格字段映射，优先使用中文标题
            record_data = {
                "fields": {
                    "标题": news_item.get('chinese_title') or news_item.get('title', ''),
                    "摘要": news_item.get('description', ''),
                    "AI观点": news_item.get('commentary', ''),
                    "中国影响分析": news_item.get('china_impact_analysis', ''),
                    "更新日期": news_item.get('future_timestamp') or self._format_datetime(news_item.get('publishedAt', '')),
                    "来源": {
                        "link": news_item.get('url', ''),
                        "text": news_item.get('source', '新闻来源')
                    }
                }
            }
            
            response = self.session.post(url, headers=headers, json=record_data)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                logger.debug(f"成功添加新闻记录: {news_item.get('title', '')[:50]}...")
                return True
            else:
                logger.error(f"添加新闻记录失败: {data}")
                return False
                
        except Exception as e:
            logger.error(f"添加新闻记录异常: {str(e)}")
            return False
    
    def _format_datetime(self, datetime_str: str) -> int:
        """
        格式化时间为时间戳（毫秒），确保最新记录有最新时间戳
        """
        if not datetime_str:
            return int(time.time() * 1000)
            
        try:
            # 尝试解析ISO 8601格式
            if 'T' in datetime_str:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                parsed_timestamp = int(dt.timestamp() * 1000)
                
                # 确保时间戳不会比当前时间早太多（避免排序问题）
                current_timestamp = int(time.time() * 1000)
                if parsed_timestamp < current_timestamp - 86400000:  # 如果早于1天前
                    return current_timestamp  # 使用当前时间
                    
                return parsed_timestamp
        except:
            pass
            
        return int(time.time() * 1000)

if __name__ == "__main__":
    client = FeishuClient()
    
    # 测试数据
    test_news = [{
        'title': '测试新闻标题',
        'description': '这是一条测试新闻的摘要内容',
        'image': 'https://example.com/image.jpg',
        'commentary': '这是AI生成的点评内容',
        'china_impact_analysis': '这是对中国影响的分析',
        'url': 'https://example.com/news',
        'publishedAt': datetime.now().isoformat(),
        'source': '测试来源'
    }]
    
    success = client.push_news_to_table(test_news)
    print(f"推送结果: {'成功' if success else '失败'}")