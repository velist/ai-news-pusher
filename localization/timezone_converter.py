#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时区转换器 - 处理UTC到北京时间的转换和中文时间格式化
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import re

class TimezoneConverter:
    """时区转换和中文时间格式化处理器"""
    
    def __init__(self):
        # 北京时间时区 (UTC+8)
        self.beijing_tz = timezone(timedelta(hours=8))
        
        # 中文时间表达映射
        self.chinese_time_units = {
            'seconds': '秒',
            'minutes': '分钟', 
            'hours': '小时',
            'days': '天',
            'weeks': '周',
            'months': '个月',
            'years': '年'
        }
        
        # 中文星期映射
        self.chinese_weekdays = {
            0: '周一', 1: '周二', 2: '周三', 3: '周四',
            4: '周五', 5: '周六', 6: '周日'
        }
    
    def parse_time_string(self, time_str: str) -> Optional[datetime]:
        """解析各种格式的时间字符串"""
        if not time_str:
            return None
            
        # 常见的时间格式模式
        patterns = [
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})Z',  # ISO格式 UTC
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\+00:00',  # ISO格式带时区
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',  # ISO格式无时区
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',  # 标准格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_str)
            if match:
                time_part = match.group(1)
                try:
                    # 尝试解析时间
                    if 'T' in time_part:
                        dt = datetime.fromisoformat(time_part)
                    else:
                        dt = datetime.strptime(time_part, '%Y-%m-%d %H:%M:%S')
                    
                    # 如果没有时区信息，假设为UTC
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    
                    return dt
                except ValueError:
                    continue
        
        # 如果所有格式都失败，返回None
        return None
    
    def utc_to_beijing(self, utc_time: Union[str, datetime]) -> Optional[datetime]:
        """将UTC时间转换为北京时间"""
        try:
            if isinstance(utc_time, str):
                dt = self.parse_time_string(utc_time)
                if dt is None:
                    return None
            else:
                dt = utc_time
            
            # 确保时间有时区信息
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            # 转换为北京时间
            beijing_time = dt.astimezone(self.beijing_tz)
            return beijing_time
            
        except Exception as e:
            print(f"时区转换失败: {e}")
            return None
    
    def format_chinese_time(self, beijing_time: datetime, include_seconds: bool = False) -> str:
        """格式化为中文时间显示"""
        if not beijing_time:
            return "时间未知"
        
        try:
            if include_seconds:
                return beijing_time.strftime('%Y年%m月%d日 %H:%M:%S')
            else:
                return beijing_time.strftime('%Y年%m月%d日 %H:%M')
        except Exception:
            return "时间格式错误"
    
    def get_relative_time_chinese(self, beijing_time: datetime) -> str:
        """获取中文相对时间表达"""
        if not beijing_time:
            return "时间未知"
        
        try:
            now = datetime.now(self.beijing_tz)
            diff = now - beijing_time
            
            # 处理未来时间
            if diff.total_seconds() < 0:
                return "刚刚"
            
            seconds = int(diff.total_seconds())
            
            # 小于1分钟
            if seconds < 60:
                return "刚刚"
            
            # 小于1小时
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes}分钟前"
            
            # 小于24小时
            elif seconds < 86400:
                hours = seconds // 3600
                return f"{hours}小时前"
            
            # 小于7天
            elif seconds < 604800:
                days = seconds // 86400
                if days == 1:
                    return "昨天"
                elif days == 2:
                    return "前天"
                else:
                    return f"{days}天前"
            
            # 小于30天
            elif seconds < 2592000:
                weeks = seconds // 604800
                return f"{weeks}周前"
            
            # 小于365天
            elif seconds < 31536000:
                months = seconds // 2592000
                return f"{months}个月前"
            
            # 超过1年
            else:
                years = seconds // 31536000
                return f"{years}年前"
                
        except Exception as e:
            print(f"相对时间计算失败: {e}")
            return "时间计算错误"
    
    def is_fresh_news(self, beijing_time: datetime, hours: int = 24) -> bool:
        """判断新闻是否新鲜（在指定小时数内）"""
        if not beijing_time:
            return False
        
        try:
            now = datetime.now(self.beijing_tz)
            diff = now - beijing_time
            return diff.total_seconds() <= (hours * 3600)
        except Exception:
            return False
    
    def get_freshness_score(self, beijing_time: datetime) -> float:
        """计算新闻新鲜度评分 (0-1, 1为最新)"""
        if not beijing_time:
            return 0.0
        
        try:
            now = datetime.now(self.beijing_tz)
            diff = now - beijing_time
            hours_old = diff.total_seconds() / 3600
            
            # 24小时内的新闻评分较高
            if hours_old <= 1:
                return 1.0
            elif hours_old <= 6:
                return 0.9
            elif hours_old <= 12:
                return 0.8
            elif hours_old <= 24:
                return 0.7
            elif hours_old <= 48:
                return 0.5
            elif hours_old <= 72:
                return 0.3
            else:
                return 0.1
                
        except Exception:
            return 0.0
    
    def format_news_time(self, utc_time: Union[str, datetime], show_relative: bool = True) -> dict:
        """格式化新闻时间，返回多种格式"""
        beijing_time = self.utc_to_beijing(utc_time)
        
        if not beijing_time:
            return {
                'beijing_time': None,
                'formatted': '时间未知',
                'relative': '时间未知',
                'is_fresh': False,
                'freshness_score': 0.0
            }
        
        return {
            'beijing_time': beijing_time,
            'formatted': self.format_chinese_time(beijing_time),
            'relative': self.get_relative_time_chinese(beijing_time),
            'is_fresh': self.is_fresh_news(beijing_time),
            'freshness_score': self.get_freshness_score(beijing_time)
        }
    
    def get_current_beijing_time(self) -> datetime:
        """获取当前北京时间"""
        return datetime.now(self.beijing_tz)
    
    def format_update_time(self) -> str:
        """格式化当前更新时间"""
        current_time = self.get_current_beijing_time()
        return f"最后更新：{self.format_chinese_time(current_time)}"