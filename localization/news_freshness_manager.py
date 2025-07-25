#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻新鲜度管理器 - 管理新闻的时效性和排序
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from localization.timezone_converter import TimezoneConverter

class NewsFreshnessManager:
    """新闻新鲜度管理器"""
    
    def __init__(self):
        self.timezone_converter = TimezoneConverter()
        
        # 新鲜度权重配置
        self.freshness_weights = {
            'time_factor': 0.7,      # 时间因素权重
            'category_factor': 0.2,  # 分类因素权重
            'quality_factor': 0.1    # 质量因素权重
        }
        
        # 分类优先级（数值越高优先级越高）
        self.category_priority = {
            'AI科技': 1.0,
            'technology': 1.0,
            'ai': 1.0,
            '游戏资讯': 0.8,
            'gaming': 0.8,
            '经济新闻': 0.9,
            'business': 0.9,
            '综合新闻': 0.7,
            'general': 0.7,
            '娱乐资讯': 0.6,
            'entertainment': 0.6
        }
    
    def filter_fresh_news(self, news_list: List[dict], hours: int = 24) -> List[dict]:
        """过滤出指定时间内的新鲜新闻"""
        if not news_list:
            return []
        
        fresh_news = []
        current_time = self.timezone_converter.get_current_beijing_time()
        
        for news_item in news_list:
            # 获取新闻发布时间
            published_time = self._get_news_time(news_item)
            if not published_time:
                continue
            
            # 转换为北京时间
            beijing_time = self.timezone_converter.utc_to_beijing(published_time)
            if not beijing_time:
                continue
            
            # 检查是否在指定时间范围内
            time_diff = current_time - beijing_time
            if time_diff.total_seconds() <= (hours * 3600):
                # 添加北京时间信息到新闻项
                news_item['beijing_time'] = beijing_time
                news_item['time_info'] = self.timezone_converter.format_news_time(published_time)
                fresh_news.append(news_item)
        
        return fresh_news
    
    def sort_by_freshness(self, news_list: List[dict]) -> List[dict]:
        """按新鲜度排序新闻列表"""
        if not news_list:
            return []
        
        # 为每个新闻计算新鲜度评分
        scored_news = []
        for news_item in news_list:
            score = self.calculate_freshness_score(news_item)
            news_item['freshness_score'] = score
            scored_news.append(news_item)
        
        # 按评分降序排序
        sorted_news = sorted(scored_news, key=lambda x: x['freshness_score'], reverse=True)
        return sorted_news
    
    def calculate_freshness_score(self, news_item: dict) -> float:
        """计算新闻的综合新鲜度评分"""
        try:
            # 1. 时间因素评分
            time_score = self._calculate_time_score(news_item)
            
            # 2. 分类因素评分
            category_score = self._calculate_category_score(news_item)
            
            # 3. 质量因素评分
            quality_score = self._calculate_quality_score(news_item)
            
            # 综合评分
            total_score = (
                time_score * self.freshness_weights['time_factor'] +
                category_score * self.freshness_weights['category_factor'] +
                quality_score * self.freshness_weights['quality_factor']
            )
            
            return min(1.0, max(0.0, total_score))
            
        except Exception as e:
            print(f"计算新鲜度评分失败: {e}")
            return 0.0
    
    def _get_news_time(self, news_item: dict) -> Optional[str]:
        """从新闻项中提取发布时间"""
        time_fields = ['publishedAt', 'published_at', 'pubDate', 'date', 'timestamp']
        
        for field in time_fields:
            if field in news_item and news_item[field]:
                return news_item[field]
        
        return None
    
    def _calculate_time_score(self, news_item: dict) -> float:
        """计算时间因素评分"""
        published_time = self._get_news_time(news_item)
        if not published_time:
            return 0.0
        
        beijing_time = self.timezone_converter.utc_to_beijing(published_time)
        if not beijing_time:
            return 0.0
        
        return self.timezone_converter.get_freshness_score(beijing_time)
    
    def _calculate_category_score(self, news_item: dict) -> float:
        """计算分类因素评分"""
        category = news_item.get('category', '').lower()
        
        # 检查中文分类
        for cat, priority in self.category_priority.items():
            if cat.lower() in category or category in cat.lower():
                return priority
        
        # 默认评分
        return 0.5
    
    def _calculate_quality_score(self, news_item: dict) -> float:
        """计算质量因素评分"""
        # 检查是否有AI翻译质量信息
        if 'ai_translation' in news_item:
            translation_info = news_item['ai_translation']
            if 'translation_confidence' in translation_info:
                confidence = translation_info['translation_confidence']
                
                if isinstance(confidence, dict):
                    # 取平均置信度
                    avg_confidence = sum(confidence.values()) / len(confidence)
                    return avg_confidence
                elif isinstance(confidence, (int, float)):
                    return confidence
        
        # 检查其他质量指标
        quality_indicators = 0
        total_indicators = 0
        
        # 检查是否有图片
        if news_item.get('image') or news_item.get('urlToImage'):
            quality_indicators += 1
        total_indicators += 1
        
        # 检查描述长度
        description = news_item.get('description', '')
        if len(description) > 50:
            quality_indicators += 1
        total_indicators += 1
        
        # 检查来源信息
        if news_item.get('source', {}).get('name'):
            quality_indicators += 1
        total_indicators += 1
        
        return quality_indicators / total_indicators if total_indicators > 0 else 0.5
    
    def get_update_status(self) -> dict:
        """获取更新状态信息"""
        current_time = self.timezone_converter.get_current_beijing_time()
        
        return {
            'last_update': current_time,
            'formatted_time': self.timezone_converter.format_chinese_time(current_time),
            'update_text': self.timezone_converter.format_update_time(),
            'timezone': 'Asia/Shanghai',
            'timezone_name': '北京时间'
        }
    
    def categorize_by_freshness(self, news_list: List[dict]) -> dict:
        """按新鲜度将新闻分类"""
        if not news_list:
            return {
                'breaking': [],      # 突发新闻（1小时内）
                'recent': [],        # 最新新闻（6小时内）
                'today': [],         # 今日新闻（24小时内）
                'yesterday': [],     # 昨日新闻（48小时内）
                'older': []          # 更早新闻
            }
        
        categorized = {
            'breaking': [],
            'recent': [],
            'today': [],
            'yesterday': [],
            'older': []
        }
        
        current_time = self.timezone_converter.get_current_beijing_time()
        
        for news_item in news_list:
            published_time = self._get_news_time(news_item)
            if not published_time:
                categorized['older'].append(news_item)
                continue
            
            beijing_time = self.timezone_converter.utc_to_beijing(published_time)
            if not beijing_time:
                categorized['older'].append(news_item)
                continue
            
            time_diff = current_time - beijing_time
            hours_old = time_diff.total_seconds() / 3600
            
            if hours_old <= 1:
                categorized['breaking'].append(news_item)
            elif hours_old <= 6:
                categorized['recent'].append(news_item)
            elif hours_old <= 24:
                categorized['today'].append(news_item)
            elif hours_old <= 48:
                categorized['yesterday'].append(news_item)
            else:
                categorized['older'].append(news_item)
        
        return categorized
    
    def get_freshness_summary(self, news_list: List[dict]) -> dict:
        """获取新闻新鲜度摘要统计"""
        if not news_list:
            return {
                'total_count': 0,
                'fresh_count': 0,
                'fresh_percentage': 0,
                'average_age_hours': 0,
                'newest_time': None,
                'oldest_time': None
            }
        
        current_time = self.timezone_converter.get_current_beijing_time()
        fresh_count = 0
        total_age_hours = 0
        valid_times = []
        
        for news_item in news_list:
            published_time = self._get_news_time(news_item)
            if not published_time:
                continue
            
            beijing_time = self.timezone_converter.utc_to_beijing(published_time)
            if not beijing_time:
                continue
            
            valid_times.append(beijing_time)
            
            time_diff = current_time - beijing_time
            hours_old = time_diff.total_seconds() / 3600
            total_age_hours += hours_old
            
            if hours_old <= 24:  # 24小时内算新鲜
                fresh_count += 1
        
        valid_count = len(valid_times)
        
        return {
            'total_count': len(news_list),
            'fresh_count': fresh_count,
            'fresh_percentage': (fresh_count / len(news_list) * 100) if news_list else 0,
            'average_age_hours': total_age_hours / valid_count if valid_count > 0 else 0,
            'newest_time': max(valid_times) if valid_times else None,
            'oldest_time': min(valid_times) if valid_times else None
        }