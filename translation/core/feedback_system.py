#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译质量反馈系统 - 收集和处理用户反馈以持续优化翻译质量
"""

import json
import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum


class FeedbackType(Enum):
    """反馈类型"""
    QUALITY_RATING = "quality_rating"  # 质量评分
    CORRECTION = "correction"          # 翻译纠正
    PREFERENCE = "preference"          # 偏好选择
    REPORT_ERROR = "report_error"      # 错误报告


@dataclass
class UserFeedback:
    """用户反馈数据模型"""
    feedback_id: str
    original_text: str
    translated_text: str
    service_name: str
    feedback_type: FeedbackType
    rating: Optional[float] = None  # 1-5分评分
    corrected_text: Optional[str] = None  # 用户纠正的翻译
    comments: Optional[str] = None  # 用户评论
    user_id: Optional[str] = None  # 用户ID（可选）
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class FeedbackAnalysis:
    """反馈分析结果"""
    service_name: str
    total_feedback_count: int
    average_rating: float
    common_issues: List[str]
    improvement_suggestions: List[str]
    quality_trend: str  # 'improving', 'stable', 'declining'


class TranslationFeedbackSystem:
    """翻译反馈系统"""
    
    def __init__(self, db_path: str = "translation_feedback.db"):
        """
        初始化反馈系统
        
        Args:
            db_path: SQLite数据库路径
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
        
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    original_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    rating REAL,
                    corrected_text TEXT,
                    comments TEXT,
                    user_id TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_analysis (
                    service_name TEXT PRIMARY KEY,
                    analysis_data TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            # 创建索引以提高查询性能
            conn.execute("CREATE INDEX IF NOT EXISTS idx_service_name ON user_feedback(service_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON user_feedback(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_feedback_type ON user_feedback(feedback_type)")
    
    def submit_feedback(self, feedback: UserFeedback) -> bool:
        """
        提交用户反馈
        
        Args:
            feedback: 用户反馈对象
            
        Returns:
            bool: 是否成功提交
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_feedback 
                    (feedback_id, original_text, translated_text, service_name, 
                     feedback_type, rating, corrected_text, comments, user_id, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback.feedback_id,
                    feedback.original_text,
                    feedback.translated_text,
                    feedback.service_name,
                    feedback.feedback_type.value,
                    feedback.rating,
                    feedback.corrected_text,
                    feedback.comments,
                    feedback.user_id,
                    feedback.timestamp.isoformat()
                ))
            
            self.logger.info(f"用户反馈已提交: {feedback.feedback_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"提交反馈失败: {e}")
            return False
    
    def get_service_feedback_summary(self, service_name: str, 
                                   days: int = 30) -> Dict[str, any]:
        """
        获取服务反馈摘要
        
        Args:
            service_name: 服务名称
            days: 统计天数
            
        Returns:
            Dict: 反馈摘要
        """
        since_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # 获取评分统计
            rating_stats = conn.execute("""
                SELECT COUNT(*), AVG(rating), MIN(rating), MAX(rating)
                FROM user_feedback 
                WHERE service_name = ? AND rating IS NOT NULL 
                AND timestamp >= ?
            """, (service_name, since_date.isoformat())).fetchone()
            
            # 获取反馈类型分布
            type_distribution = conn.execute("""
                SELECT feedback_type, COUNT(*) 
                FROM user_feedback 
                WHERE service_name = ? AND timestamp >= ?
                GROUP BY feedback_type
            """, (service_name, since_date.isoformat())).fetchall()
            
            # 获取最近的纠正建议
            corrections = conn.execute("""
                SELECT original_text, translated_text, corrected_text, comments
                FROM user_feedback 
                WHERE service_name = ? AND feedback_type = 'correction' 
                AND timestamp >= ? AND corrected_text IS NOT NULL
                ORDER BY timestamp DESC LIMIT 10
            """, (service_name, since_date.isoformat())).fetchall()
        
        return {
            'service_name': service_name,
            'period_days': days,
            'rating_stats': {
                'count': rating_stats[0] or 0,
                'average': rating_stats[1] or 0,
                'min': rating_stats[2] or 0,
                'max': rating_stats[3] or 0
            },
            'feedback_distribution': dict(type_distribution),
            'recent_corrections': [
                {
                    'original': correction[0],
                    'translated': correction[1],
                    'corrected': correction[2],
                    'comments': correction[3]
                }
                for correction in corrections
            ]
        }
    
    def analyze_service_performance(self, service_name: str) -> FeedbackAnalysis:
        """
        分析服务性能
        
        Args:
            service_name: 服务名称
            
        Returns:
            FeedbackAnalysis: 分析结果
        """
        with sqlite3.connect(self.db_path) as conn:
            # 获取总反馈数
            total_count = conn.execute("""
                SELECT COUNT(*) FROM user_feedback WHERE service_name = ?
            """, (service_name,)).fetchone()[0]
            
            # 获取平均评分
            avg_rating = conn.execute("""
                SELECT AVG(rating) FROM user_feedback 
                WHERE service_name = ? AND rating IS NOT NULL
            """, (service_name,)).fetchone()[0] or 0
            
            # 分析常见问题
            common_issues = self._analyze_common_issues(service_name)
            
            # 生成改进建议
            improvement_suggestions = self._generate_improvement_suggestions(service_name)
            
            # 分析质量趋势
            quality_trend = self._analyze_quality_trend(service_name)
        
        return FeedbackAnalysis(
            service_name=service_name,
            total_feedback_count=total_count,
            average_rating=avg_rating,
            common_issues=common_issues,
            improvement_suggestions=improvement_suggestions,
            quality_trend=quality_trend
        )
    
    def _analyze_common_issues(self, service_name: str) -> List[str]:
        """分析常见问题"""
        issues = []
        
        with sqlite3.connect(self.db_path) as conn:
            # 获取低评分反馈的评论
            low_rating_comments = conn.execute("""
                SELECT comments FROM user_feedback 
                WHERE service_name = ? AND rating <= 2 AND comments IS NOT NULL
            """, (service_name,)).fetchall()
            
            # 获取错误报告
            error_reports = conn.execute("""
                SELECT comments FROM user_feedback 
                WHERE service_name = ? AND feedback_type = 'report_error' 
                AND comments IS NOT NULL
            """, (service_name,)).fetchall()
        
        # 简单的关键词分析
        all_comments = [comment[0] for comment in low_rating_comments + error_reports]
        issue_keywords = {
            '术语翻译': ['术语', '专业词汇', '技术词汇', '名词'],
            '语法错误': ['语法', '句法', '表达不通', '不通顺'],
            '语义错误': ['意思', '语义', '理解错误', '翻译错误'],
            '格式问题': ['格式', '标点', '换行', '排版']
        }
        
        for issue_type, keywords in issue_keywords.items():
            count = sum(1 for comment in all_comments 
                       if any(keyword in comment for keyword in keywords))
            if count > 0:
                issues.append(f"{issue_type} ({count}次提及)")
        
        return issues
    
    def _generate_improvement_suggestions(self, service_name: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        with sqlite3.connect(self.db_path) as conn:
            # 获取纠正建议
            corrections = conn.execute("""
                SELECT original_text, translated_text, corrected_text 
                FROM user_feedback 
                WHERE service_name = ? AND feedback_type = 'correction' 
                AND corrected_text IS NOT NULL
                LIMIT 20
            """, (service_name,)).fetchall()
            
            # 获取平均评分
            avg_rating = conn.execute("""
                SELECT AVG(rating) FROM user_feedback 
                WHERE service_name = ? AND rating IS NOT NULL
            """, (service_name,)).fetchone()[0] or 0
        
        if avg_rating < 3.0:
            suggestions.append("整体翻译质量需要提升，建议优化翻译模型或提示词")
        
        if len(corrections) > 5:
            suggestions.append("用户频繁提供翻译纠正，建议分析纠正模式并优化翻译逻辑")
        
        # 分析纠正模式
        if corrections:
            # 简单分析：如果很多纠正都涉及专有名词，建议改进术语处理
            proper_noun_corrections = sum(1 for correction in corrections 
                                        if any(word.isupper() for word in correction[0].split()))
            if proper_noun_corrections > len(corrections) * 0.3:
                suggestions.append("建议改进专有名词和术语的翻译处理")
        
        return suggestions
    
    def _analyze_quality_trend(self, service_name: str) -> str:
        """分析质量趋势"""
        with sqlite3.connect(self.db_path) as conn:
            # 获取最近30天和之前30天的平均评分
            now = datetime.now()
            recent_30_days = now - timedelta(days=30)
            previous_30_days = now - timedelta(days=60)
            
            recent_rating = conn.execute("""
                SELECT AVG(rating) FROM user_feedback 
                WHERE service_name = ? AND rating IS NOT NULL 
                AND timestamp >= ?
            """, (service_name, recent_30_days.isoformat())).fetchone()[0]
            
            previous_rating = conn.execute("""
                SELECT AVG(rating) FROM user_feedback 
                WHERE service_name = ? AND rating IS NOT NULL 
                AND timestamp >= ? AND timestamp < ?
            """, (service_name, previous_30_days.isoformat(), recent_30_days.isoformat())).fetchone()[0]
        
        if recent_rating is None or previous_rating is None:
            return "stable"  # 数据不足
        
        diff = recent_rating - previous_rating
        if diff > 0.2:
            return "improving"
        elif diff < -0.2:
            return "declining"
        else:
            return "stable"
    
    def get_all_services_summary(self) -> Dict[str, Dict]:
        """获取所有服务的反馈摘要"""
        with sqlite3.connect(self.db_path) as conn:
            services = conn.execute("""
                SELECT DISTINCT service_name FROM user_feedback
            """).fetchall()
        
        summary = {}
        for service in services:
            service_name = service[0]
            summary[service_name] = self.get_service_feedback_summary(service_name)
        
        return summary
    
    def export_feedback_data(self, output_path: str, service_name: Optional[str] = None) -> bool:
        """
        导出反馈数据
        
        Args:
            output_path: 输出文件路径
            service_name: 服务名称，如果为None则导出所有数据
            
        Returns:
            bool: 是否成功导出
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                if service_name:
                    cursor = conn.execute("""
                        SELECT * FROM user_feedback WHERE service_name = ?
                        ORDER BY timestamp DESC
                    """, (service_name,))
                else:
                    cursor = conn.execute("""
                        SELECT * FROM user_feedback ORDER BY timestamp DESC
                    """)
                
                # 获取列名
                columns = [description[0] for description in cursor.description]
                
                # 导出为JSON格式
                data = []
                for row in cursor.fetchall():
                    data.append(dict(zip(columns, row)))
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"反馈数据已导出到: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"导出反馈数据失败: {e}")
            return False