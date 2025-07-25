#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中文本地化处理器 - 处理界面元素的中文化和本地化
"""

import re
from typing import Dict, Optional

class ChineseLocalizer:
    """中文本地化处理器"""
    
    def __init__(self):
        # 新闻分类中英文映射
        self.category_mapping = {
            'technology': 'AI科技',
            'tech': 'AI科技',
            'ai': 'AI科技',
            'artificial intelligence': 'AI科技',
            'gaming': '游戏资讯',
            'games': '游戏资讯',
            'game': '游戏资讯',
            'business': '经济新闻',
            'economy': '经济新闻',
            'finance': '金融财经',
            'general': '综合新闻',
            'news': '综合新闻',
            'entertainment': '娱乐资讯',
            'sports': '体育新闻',
            'health': '健康医疗',
            'science': '科学研究',
            'politics': '政治新闻',
            'world': '国际新闻'
        }
        
        # UI界面文本映射
        self.ui_text_mapping = {
            'read_more': '阅读更多',
            'read_full': '查看全文',
            'original_text': '查看原文',
            'original_link': '原文链接',
            'translation_quality': '翻译质量',
            'translation_confidence': '翻译置信度',
            'last_updated': '最后更新',
            'updated_at': '更新时间',
            'published_at': '发布时间',
            'source': '来源',
            'category': '分类',
            'loading': '加载中...',
            'error': '加载失败',
            'retry': '重试',
            'refresh': '刷新',
            'back_to_top': '返回顶部',
            'share': '分享',
            'bookmark': '收藏',
            'search': '搜索',
            'filter': '筛选',
            'sort': '排序',
            'newest': '最新',
            'oldest': '最早',
            'most_relevant': '最相关',
            'settings': '设置',
            'theme': '主题',
            'font_size': '字体大小',
            'language': '语言',
            'timezone': '时区',
            'light_theme': '浅色主题',
            'dark_theme': '深色主题',
            'auto_theme': '自动主题',
            'small_font': '小字体',
            'medium_font': '中字体',
            'large_font': '大字体'
        }
        
        # 翻译质量等级映射
        self.quality_levels = {
            (0.9, 1.0): '优秀',
            (0.8, 0.9): '良好',
            (0.7, 0.8): '一般',
            (0.6, 0.7): '较差',
            (0.0, 0.6): '需要改进'
        }
        
        # 阅读时间估算（中文）
        self.reading_speed_chinese = 300  # 每分钟300个中文字符
    
    def localize_category(self, category: str) -> str:
        """本地化新闻分类名称"""
        if not category:
            return '未分类'
        
        # 转换为小写进行匹配
        category_lower = category.lower().strip()
        
        # 直接匹配
        if category_lower in self.category_mapping:
            return self.category_mapping[category_lower]
        
        # 模糊匹配
        for key, value in self.category_mapping.items():
            if key in category_lower or category_lower in key:
                return value
        
        # 如果没有匹配，返回首字母大写的原文
        return category.title()
    
    def localize_ui_text(self, key: str) -> str:
        """本地化UI界面文本"""
        return self.ui_text_mapping.get(key.lower(), key)
    
    def format_quality_score(self, score: float) -> str:
        """格式化翻译质量评分为中文描述"""
        if not isinstance(score, (int, float)) or score < 0 or score > 1:
            return '未知'
        
        for (min_score, max_score), description in self.quality_levels.items():
            if min_score <= score < max_score:
                return description
        
        return '未知'
    
    def get_quality_description(self, score: float) -> dict:
        """获取详细的质量描述信息"""
        quality_text = self.format_quality_score(score)
        
        # 根据评分提供详细描述
        if score >= 0.9:
            detail = "翻译准确，语言流畅，完全符合中文表达习惯"
            color = "#10B981"  # 绿色
        elif score >= 0.8:
            detail = "翻译较为准确，偶有小瑕疵，整体质量良好"
            color = "#059669"  # 深绿色
        elif score >= 0.7:
            detail = "翻译基本准确，可能存在一些表达不够自然的地方"
            color = "#F59E0B"  # 黄色
        elif score >= 0.6:
            detail = "翻译存在一些问题，建议对照原文阅读"
            color = "#EF4444"  # 红色
        else:
            detail = "翻译质量较差，强烈建议查看原文"
            color = "#DC2626"  # 深红色
        
        return {
            'score': score,
            'text': quality_text,
            'detail': detail,
            'color': color,
            'percentage': f"{int(score * 100)}%"
        }
    
    def get_reading_time_estimate(self, content: str) -> str:
        """估算中文内容的阅读时间"""
        if not content:
            return "0分钟"
        
        # 计算中文字符数（排除标点和空格）
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        
        # 计算英文单词数
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', content))
        
        # 总字符数（中文字符 + 英文单词数 * 5）
        total_chars = chinese_chars + english_words * 5
        
        # 计算阅读时间（分钟）
        reading_minutes = max(1, round(total_chars / self.reading_speed_chinese))
        
        if reading_minutes < 60:
            return f"{reading_minutes}分钟"
        else:
            hours = reading_minutes // 60
            minutes = reading_minutes % 60
            if minutes == 0:
                return f"{hours}小时"
            else:
                return f"{hours}小时{minutes}分钟"
    
    def localize_source_name(self, source_name: str) -> str:
        """本地化新闻源名称"""
        # 常见英文新闻源的中文名称映射
        source_mapping = {
            'techcrunch': 'TechCrunch',
            'the verge': 'The Verge',
            'wired': 'Wired 连线',
            'ars technica': 'Ars Technica',
            'engadget': 'Engadget 瘾科技',
            'reuters': '路透社',
            'bloomberg': '彭博社',
            'wall street journal': '华尔街日报',
            'financial times': '金融时报',
            'bbc': 'BBC',
            'cnn': 'CNN',
            'associated press': '美联社',
            'new york times': '纽约时报',
            'washington post': '华盛顿邮报'
        }
        
        if not source_name:
            return '未知来源'
        
        source_lower = source_name.lower().strip()
        return source_mapping.get(source_lower, source_name)
    
    def format_news_summary(self, news_item: dict) -> dict:
        """格式化新闻摘要信息为中文显示"""
        summary = {
            'title': news_item.get('title', '无标题'),
            'description': news_item.get('description', '无描述'),
            'category': self.localize_category(news_item.get('category', '')),
            'source': self.localize_source_name(news_item.get('source', {}).get('name', '')),
            'reading_time': self.get_reading_time_estimate(
                news_item.get('description', '') + news_item.get('content', '')
            )
        }
        
        # 处理翻译质量信息
        if 'ai_translation' in news_item:
            translation_info = news_item['ai_translation']
            if 'translation_confidence' in translation_info:
                confidence = translation_info['translation_confidence']
                if isinstance(confidence, dict):
                    # 取标题和描述置信度的平均值
                    avg_confidence = (
                        confidence.get('title', 0) + 
                        confidence.get('description', 0)
                    ) / 2
                    summary['quality'] = self.get_quality_description(avg_confidence)
                else:
                    summary['quality'] = self.get_quality_description(confidence)
        
        return summary
    
    def get_localized_config(self) -> dict:
        """获取本地化配置信息"""
        return {
            'language': 'zh-CN',
            'region': 'CN',
            'timezone': 'Asia/Shanghai',
            'currency': 'CNY',
            'date_format': '%Y年%m月%d日',
            'time_format': '%H:%M',
            'datetime_format': '%Y年%m月%d日 %H:%M',
            'number_format': 'zh-CN',
            'reading_direction': 'ltr',
            'font_family': '"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif'
        }