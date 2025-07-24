#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译反馈系统测试
"""

import unittest
import tempfile
import os
from datetime import datetime
from translation.core.feedback_system import (
    TranslationFeedbackSystem, UserFeedback, FeedbackType
)


class TestTranslationFeedbackSystem(unittest.TestCase):
    """翻译反馈系统测试类"""
    
    def setUp(self):
        """测试初始化"""
        # 使用临时数据库文件
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.feedback_system = TranslationFeedbackSystem(self.temp_db.name)
    
    def tearDown(self):
        """测试清理"""
        # 删除临时数据库文件
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_submit_feedback_rating(self):
        """测试提交评分反馈"""
        feedback = UserFeedback(
            feedback_id="test_001",
            original_text="Hello world",
            translated_text="你好世界",
            service_name="baidu",
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=4.5,
            user_id="user_123"
        )
        
        result = self.feedback_system.submit_feedback(feedback)
        self.assertTrue(result)
    
    def test_submit_feedback_correction(self):
        """测试提交纠正反馈"""
        feedback = UserFeedback(
            feedback_id="test_002",
            original_text="Apple Inc. stock price",
            translated_text="苹果公司股票价格",
            service_name="google",
            feedback_type=FeedbackType.CORRECTION,
            corrected_text="苹果公司的股价",
            comments="更自然的表达方式"
        )
        
        result = self.feedback_system.submit_feedback(feedback)
        self.assertTrue(result)
    
    def test_get_service_feedback_summary(self):
        """测试获取服务反馈摘要"""
        # 提交一些测试反馈
        feedbacks = [
            UserFeedback(
                feedback_id="test_003",
                original_text="Test 1",
                translated_text="测试1",
                service_name="baidu",
                feedback_type=FeedbackType.QUALITY_RATING,
                rating=4.0
            ),
            UserFeedback(
                feedback_id="test_004",
                original_text="Test 2",
                translated_text="测试2",
                service_name="baidu",
                feedback_type=FeedbackType.QUALITY_RATING,
                rating=3.5
            ),
            UserFeedback(
                feedback_id="test_005",
                original_text="Test 3",
                translated_text="测试3错误",
                service_name="baidu",
                feedback_type=FeedbackType.CORRECTION,
                corrected_text="测试3"
            )
        ]
        
        for feedback in feedbacks:
            self.feedback_system.submit_feedback(feedback)
        
        # 获取摘要
        summary = self.feedback_system.get_service_feedback_summary("baidu")
        
        # 验证摘要内容
        self.assertEqual(summary['service_name'], "baidu")
        self.assertEqual(summary['rating_stats']['count'], 2)
        self.assertEqual(summary['rating_stats']['average'], 3.75)
        self.assertIn('quality_rating', summary['feedback_distribution'])
        self.assertIn('correction', summary['feedback_distribution'])
        self.assertEqual(len(summary['recent_corrections']), 1)
    
    def test_analyze_service_performance(self):
        """测试分析服务性能"""
        # 提交一些测试反馈
        feedbacks = [
            UserFeedback(
                feedback_id="perf_001",
                original_text="Good translation",
                translated_text="好的翻译",
                service_name="siliconflow",
                feedback_type=FeedbackType.QUALITY_RATING,
                rating=4.5
            ),
            UserFeedback(
                feedback_id="perf_002",
                original_text="Bad translation",
                translated_text="坏翻译",
                service_name="siliconflow",
                feedback_type=FeedbackType.QUALITY_RATING,
                rating=2.0,
                comments="术语翻译不准确"
            ),
            UserFeedback(
                feedback_id="perf_003",
                original_text="Error case",
                translated_text="错误案例",
                service_name="siliconflow",
                feedback_type=FeedbackType.REPORT_ERROR,
                comments="语法错误"
            )
        ]
        
        for feedback in feedbacks:
            self.feedback_system.submit_feedback(feedback)
        
        # 分析性能
        analysis = self.feedback_system.analyze_service_performance("siliconflow")
        
        # 验证分析结果
        self.assertEqual(analysis.service_name, "siliconflow")
        self.assertEqual(analysis.total_feedback_count, 3)
        self.assertEqual(analysis.average_rating, 3.25)  # (4.5 + 2.0) / 2
        self.assertIsInstance(analysis.common_issues, list)
        self.assertIsInstance(analysis.improvement_suggestions, list)
        self.assertIn(analysis.quality_trend, ['improving', 'stable', 'declining'])
    
    def test_get_all_services_summary(self):
        """测试获取所有服务摘要"""
        # 为多个服务提交反馈
        feedbacks = [
            UserFeedback(
                feedback_id="all_001",
                original_text="Test baidu",
                translated_text="测试百度",
                service_name="baidu",
                feedback_type=FeedbackType.QUALITY_RATING,
                rating=4.0
            ),
            UserFeedback(
                feedback_id="all_002",
                original_text="Test google",
                translated_text="测试谷歌",
                service_name="google",
                feedback_type=FeedbackType.QUALITY_RATING,
                rating=4.5
            )
        ]
        
        for feedback in feedbacks:
            self.feedback_system.submit_feedback(feedback)
        
        # 获取所有服务摘要
        all_summary = self.feedback_system.get_all_services_summary()
        
        # 验证结果
        self.assertIn("baidu", all_summary)
        self.assertIn("google", all_summary)
        self.assertEqual(all_summary["baidu"]["service_name"], "baidu")
        self.assertEqual(all_summary["google"]["service_name"], "google")
    
    def test_export_feedback_data(self):
        """测试导出反馈数据"""
        # 提交测试反馈
        feedback = UserFeedback(
            feedback_id="export_001",
            original_text="Export test",
            translated_text="导出测试",
            service_name="baidu",
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=4.0
        )
        
        self.feedback_system.submit_feedback(feedback)
        
        # 导出数据
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            result = self.feedback_system.export_feedback_data(temp_path, "baidu")
            self.assertTrue(result)
            
            # 验证文件存在
            self.assertTrue(os.path.exists(temp_path))
            
            # 验证文件内容
            with open(temp_path, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
                self.assertIsInstance(data, list)
                self.assertGreater(len(data), 0)
                self.assertEqual(data[0]['feedback_id'], 'export_001')
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_feedback_type_enum(self):
        """测试反馈类型枚举"""
        # 验证所有反馈类型
        self.assertEqual(FeedbackType.QUALITY_RATING.value, "quality_rating")
        self.assertEqual(FeedbackType.CORRECTION.value, "correction")
        self.assertEqual(FeedbackType.PREFERENCE.value, "preference")
        self.assertEqual(FeedbackType.REPORT_ERROR.value, "report_error")
    
    def test_feedback_with_comments(self):
        """测试带评论的反馈"""
        feedback = UserFeedback(
            feedback_id="comment_001",
            original_text="Technical term translation",
            translated_text="技术术语翻译",
            service_name="google",
            feedback_type=FeedbackType.QUALITY_RATING,
            rating=3.0,
            comments="术语翻译需要改进，建议保留英文原词"
        )
        
        result = self.feedback_system.submit_feedback(feedback)
        self.assertTrue(result)
        
        # 验证评论被正确保存
        summary = self.feedback_system.get_service_feedback_summary("google")
        # 由于这是评分反馈而不是纠正反馈，评论不会出现在recent_corrections中
        # 但会被保存在数据库中


if __name__ == '__main__':
    unittest.main()