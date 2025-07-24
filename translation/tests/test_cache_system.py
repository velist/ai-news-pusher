#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译缓存系统测试
"""

import unittest
import tempfile
import shutil
import os
from datetime import datetime, timedelta
from translation.core.cache_system import (
    MemoryCache, FileCache, DatabaseCache, SmartTranslationCache
)
from translation.core.interfaces import TranslationResult, CachedTranslation


class TestMemoryCache(unittest.TestCase):
    """内存缓存测试"""
    
    def setUp(self):
        """测试初始化"""
        self.cache = MemoryCache(max_size=3, ttl_seconds=2)
        self.test_translation = CachedTranslation(
            content_hash="test_hash",
            translation_result=TranslationResult(
                original_text="Hello",
                translated_text="你好",
                source_language="en",
                target_language="zh",
                service_name="test",
                confidence_score=0.9,
                timestamp=datetime.now()
            ),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            usage_count=0
        )
    
    def test_put_and_get(self):
        """测试存储和获取"""
        self.cache.put("key1", self.test_translation)
        result = self.cache.get("key1")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.content_hash, "test_hash")
        self.assertEqual(result.usage_count, 1)  # 访问后计数增加
    
    def test_lru_eviction(self):
        """测试LRU淘汰策略"""
        # 填满缓存
        for i in range(3):
            translation = CachedTranslation(
                content_hash=f"hash_{i}",
                translation_result=TranslationResult(
                    original_text=f"Text {i}",
                    translated_text=f"文本 {i}",
                    source_language="en",
                    target_language="zh",
                    service_name="test",
                    confidence_score=0.9,
                    timestamp=datetime.now()
                ),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1),
                usage_count=0
            )
            self.cache.put(f"key_{i}", translation)
        
        # 访问key_1，使其成为最近访问的
        self.cache.get("key_1")
        
        # 添加新项，应该淘汰key_0（最久未访问）
        self.cache.put("key_3", self.test_translation)
        
        self.assertIsNone(self.cache.get("key_0"))  # 应该被淘汰
        self.assertIsNotNone(self.cache.get("key_1"))  # 应该还在
        self.assertIsNotNone(self.cache.get("key_3"))  # 新添加的
    
    def test_ttl_expiration(self):
        """测试TTL过期"""
        import time
        
        self.cache.put("key1", self.test_translation)
        self.assertIsNotNone(self.cache.get("key1"))
        
        # 等待过期
        time.sleep(3)
        self.assertIsNone(self.cache.get("key1"))


class TestFileCache(unittest.TestCase):
    """文件缓存测试"""
    
    def setUp(self):
        """测试初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = FileCache(cache_dir=self.temp_dir, max_files=5)
        self.test_translation = CachedTranslation(
            content_hash="test_hash",
            translation_result=TranslationResult(
                original_text="Hello",
                translated_text="你好",
                source_language="en",
                target_language="zh",
                service_name="test",
                confidence_score=0.9,
                timestamp=datetime.now()
            ),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            usage_count=0
        )
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_put_and_get(self):
        """测试存储和获取"""
        self.cache.put("test_key", self.test_translation)
        result = self.cache.get("test_key")
        
        self.assertIsNotNone(result)
        self.assertEqual(result.content_hash, "test_hash")
    
    def test_expired_item_removal(self):
        """测试过期项自动删除"""
        # 创建已过期的翻译
        expired_translation = CachedTranslation(
            content_hash="expired_hash",
            translation_result=TranslationResult(
                original_text="Expired",
                translated_text="过期",
                source_language="en",
                target_language="zh",
                service_name="test",
                confidence_score=0.9,
                timestamp=datetime.now()
            ),
            created_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),  # 已过期
            usage_count=0
        )
        
        self.cache.put("expired_key", expired_translation)
        result = self.cache.get("expired_key")
        
        self.assertIsNone(result)  # 应该返回None因为已过期


class TestDatabaseCache(unittest.TestCase):
    """数据库缓存测试"""
    
    def setUp(self):
        """测试初始化"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.cache = DatabaseCache(db_path=self.temp_db.name)
        self.test_translation = CachedTranslation(
            content_hash="test_hash",
            translation_result=TranslationResult(
                original_text="Hello",
                translated_text="你好",
                source_language="en",
                target_language="zh",
                service_name="test",
                confidence_score=0.9,
                timestamp=datetime.now()
            ),
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1),
            usage_count=0
        )
    
    def tearDown(self):
        """测试清理"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_put_and_get(self):
        """测试存储和获取"""
        # 使用CachedTranslation的content_hash作为key
        key = self.test_translation.content_hash
        self.cache.put(key, self.test_translation)
        result = self.cache.get(key)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.content_hash, "test_hash")
        self.assertEqual(result.usage_count, 1)  # 访问后计数增加
    
    def test_cache_stats(self):
        """测试缓存统计"""
        self.cache.put("key1", self.test_translation)
        stats = self.cache.get_cache_stats()
        
        self.assertEqual(stats['total_items'], 1)
        self.assertEqual(stats['valid_items'], 1)
        self.assertIn('test', stats['service_distribution'])


class TestSmartTranslationCache(unittest.TestCase):
    """智能翻译缓存系统测试"""
    
    def setUp(self):
        """测试初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        config = {
            'memory_cache_size': 10,
            'file_cache_dir': self.temp_dir,
            'db_cache_path': self.temp_db.name,
            'auto_cleanup': False  # 禁用自动清理以便测试
        }
        
        self.cache = SmartTranslationCache(config)
        self.test_translation = TranslationResult(
            original_text="Hello world",
            translated_text="你好世界",
            source_language="en",
            target_language="zh",
            service_name="test",
            confidence_score=0.9,
            timestamp=datetime.now()
        )
    
    def tearDown(self):
        """测试清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_cache_and_retrieve(self):
        """测试缓存和检索"""
        text = "Hello world"
        
        # 缓存翻译
        success = self.cache.cache_translation(text, self.test_translation)
        self.assertTrue(success)
        
        # 检索翻译
        cached_result = self.cache.get_cached_translation(text)
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result.translation_result.translated_text, "你好世界")
    
    def test_multi_level_cache(self):
        """测试多级缓存"""
        text = "Multi-level cache test"
        translation = TranslationResult(
            original_text=text,
            translated_text="多级缓存测试",
            source_language="en",
            target_language="zh",
            service_name="test",
            confidence_score=0.9,
            timestamp=datetime.now()
        )
        
        # 缓存翻译
        self.cache.cache_translation(text, translation)
        
        # 清空内存缓存
        self.cache.memory_cache.clear()
        
        # 应该能从文件缓存或数据库缓存中获取
        cached_result = self.cache.get_cached_translation(text)
        self.assertIsNotNone(cached_result)
        self.assertEqual(cached_result.translation_result.translated_text, "多级缓存测试")
    
    def test_cache_statistics(self):
        """测试缓存统计"""
        # 执行一些缓存操作
        texts = ["Text 1", "Text 2", "Text 3"]
        
        for i, text in enumerate(texts):
            translation = TranslationResult(
                original_text=text,
                translated_text=f"文本 {i+1}",
                source_language="en",
                target_language="zh",
                service_name="test",
                confidence_score=0.9,
                timestamp=datetime.now()
            )
            self.cache.cache_translation(text, translation)
        
        # 访问一些缓存项
        self.cache.get_cached_translation("Text 1")
        self.cache.get_cached_translation("Text 2")
        self.cache.get_cached_translation("Non-existent text")  # 缓存未命中
        
        # 获取统计信息
        stats = self.cache.get_cache_statistics()
        
        self.assertGreater(stats['total_requests'], 0)
        self.assertGreater(stats['cache_hits'], 0)
        self.assertGreater(stats['cache_misses'], 0)
        self.assertTrue(0 <= stats['hit_rate'] <= 1)
    
    def test_cache_key_generation(self):
        """测试缓存键生成"""
        key1 = self.cache._generate_cache_key("Hello", "en", "zh")
        key2 = self.cache._generate_cache_key("Hello", "en", "zh")
        key3 = self.cache._generate_cache_key("Hello", "en", "ja")
        
        # 相同内容应该生成相同的键
        self.assertEqual(key1, key2)
        
        # 不同内容应该生成不同的键
        self.assertNotEqual(key1, key3)
    
    def test_performance_optimization(self):
        """测试性能优化"""
        # 添加一些缓存项
        for i in range(5):
            text = f"Test text {i}"
            translation = TranslationResult(
                original_text=text,
                translated_text=f"测试文本 {i}",
                source_language="en",
                target_language="zh",
                service_name="test",
                confidence_score=0.9,
                timestamp=datetime.now()
            )
            self.cache.cache_translation(text, translation)
        
        # 执行性能优化
        optimization_results = self.cache.optimize_cache_performance()
        
        self.assertIn('actions_taken', optimization_results)
        self.assertIn('before_stats', optimization_results)
        self.assertIn('after_stats', optimization_results)


if __name__ == '__main__':
    unittest.main()