#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能翻译缓存系统 - 多级缓存架构实现
"""

import hashlib
import json
import sqlite3
import pickle
import threading
import time
import os
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from translation.core.interfaces import ITranslationCache, TranslationResult, CachedTranslation


@dataclass
class CacheStats:
    """缓存统计信息"""
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    memory_cache_hits: int = 0
    file_cache_hits: int = 0
    db_cache_hits: int = 0
    total_cached_items: int = 0
    cache_size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests
    
    @property
    def memory_hit_rate(self) -> float:
        """内存缓存命中率"""
        if self.total_requests == 0:
            return 0.0
        return self.memory_cache_hits / self.total_requests


class MemoryCache:
    """内存缓存层"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存项数
            ttl_seconds: 生存时间（秒）
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[CachedTranslation, float]] = {}
        self.access_times: Dict[str, float] = {}
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CachedTranslation]:
        """获取缓存项"""
        with self.lock:
            if key not in self.cache:
                return None
            
            cached_item, timestamp = self.cache[key]
            
            # 检查是否过期
            if time.time() - timestamp > self.ttl_seconds:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                return None
            
            # 更新访问时间
            self.access_times[key] = time.time()
            cached_item.usage_count += 1
            
            return cached_item
    
    def put(self, key: str, value: CachedTranslation):
        """存储缓存项"""
        with self.lock:
            current_time = time.time()
            
            # 如果缓存已满，移除最久未访问的项
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()
            
            self.cache[key] = (value, current_time)
            self.access_times[key] = current_time
    
    def _evict_lru(self):
        """移除最久未访问的项"""
        if not self.access_times:
            return
        
        # 找到最久未访问的键
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # 移除该项
        if lru_key in self.cache:
            del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def clear_expired(self) -> int:
        """清理过期项"""
        with self.lock:
            current_time = time.time()
            expired_keys = []
            
            for key, (_, timestamp) in self.cache.items():
                if current_time - timestamp > self.ttl_seconds:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
            
            return len(expired_keys)
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()


class FileCache:
    """文件缓存层"""
    
    def __init__(self, cache_dir: str = "translation_cache", max_files: int = 10000):
        """
        初始化文件缓存
        
        Args:
            cache_dir: 缓存目录
            max_files: 最大文件数
        """
        self.cache_dir = Path(cache_dir)
        self.max_files = max_files
        self.cache_dir.mkdir(exist_ok=True)
        self.lock = threading.RLock()
    
    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        # 使用哈希值的前两位作为子目录，避免单个目录文件过多
        hash_prefix = key[:2]
        subdir = self.cache_dir / hash_prefix
        subdir.mkdir(exist_ok=True)
        return subdir / f"{key}.cache"
    
    def get(self, key: str) -> Optional[CachedTranslation]:
        """获取缓存项"""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'rb') as f:
                cached_item = pickle.load(f)
            
            # 检查是否过期
            if datetime.now() > cached_item.expires_at:
                file_path.unlink(missing_ok=True)
                return None
            
            # 更新访问时间
            file_path.touch()
            cached_item.usage_count += 1
            
            # 重新保存以更新使用计数
            with open(file_path, 'wb') as f:
                pickle.dump(cached_item, f)
            
            return cached_item
        
        except Exception as e:
            logging.warning(f"读取文件缓存失败 {file_path}: {e}")
            file_path.unlink(missing_ok=True)
            return None
    
    def put(self, key: str, value: CachedTranslation):
        """存储缓存项"""
        with self.lock:
            # 检查文件数量限制
            if self._count_files() >= self.max_files:
                self._cleanup_old_files()
            
            file_path = self._get_file_path(key)
            
            try:
                with open(file_path, 'wb') as f:
                    pickle.dump(value, f)
            except Exception as e:
                logging.error(f"写入文件缓存失败 {file_path}: {e}")
    
    def _count_files(self) -> int:
        """统计缓存文件数量"""
        count = 0
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                count += len(list(subdir.glob("*.cache")))
        return count
    
    def _cleanup_old_files(self, cleanup_ratio: float = 0.2):
        """清理旧文件"""
        files_with_mtime = []
        
        # 收集所有缓存文件及其修改时间
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                for cache_file in subdir.glob("*.cache"):
                    try:
                        mtime = cache_file.stat().st_mtime
                        files_with_mtime.append((cache_file, mtime))
                    except OSError:
                        continue
        
        # 按修改时间排序，删除最旧的文件
        files_with_mtime.sort(key=lambda x: x[1])
        cleanup_count = int(len(files_with_mtime) * cleanup_ratio)
        
        for cache_file, _ in files_with_mtime[:cleanup_count]:
            try:
                cache_file.unlink()
            except OSError:
                continue
    
    def clear_expired(self) -> int:
        """清理过期文件"""
        expired_count = 0
        current_time = datetime.now()
        
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                for cache_file in subdir.glob("*.cache"):
                    try:
                        with open(cache_file, 'rb') as f:
                            cached_item = pickle.load(f)
                        
                        if current_time > cached_item.expires_at:
                            cache_file.unlink()
                            expired_count += 1
                    
                    except Exception:
                        # 如果文件损坏，也删除它
                        cache_file.unlink(missing_ok=True)
                        expired_count += 1
        
        return expired_count
    
    def clear(self):
        """清空文件缓存"""
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                for cache_file in subdir.glob("*.cache"):
                    cache_file.unlink(missing_ok=True)


class DatabaseCache:
    """数据库缓存层（持久化存储）"""
    
    def __init__(self, db_path: str = "translation_cache.db"):
        """
        初始化数据库缓存
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.lock = threading.RLock()
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS translation_cache (
                    content_hash TEXT PRIMARY KEY,
                    original_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    source_language TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    quality_score REAL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            
            # 创建索引
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON translation_cache(expires_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_service_name ON translation_cache(service_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_last_accessed ON translation_cache(last_accessed)")
    
    def get(self, key: str) -> Optional[CachedTranslation]:
        """获取缓存项"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM translation_cache WHERE content_hash = ?
            """, (key,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # 检查是否过期
            expires_at = datetime.fromisoformat(row[9])
            if datetime.now() > expires_at:
                # 删除过期项
                conn.execute("DELETE FROM translation_cache WHERE content_hash = ?", (key,))
                return None
            
            # 更新访问信息
            usage_count = row[10] + 1
            conn.execute("""
                UPDATE translation_cache 
                SET usage_count = ?, last_accessed = ?
                WHERE content_hash = ?
            """, (usage_count, datetime.now().isoformat(), key))
            
            # 构造返回对象
            translation_result = TranslationResult(
                original_text=row[1],
                translated_text=row[2],
                source_language=row[3],
                target_language=row[4],
                service_name=row[5],
                confidence_score=row[6],
                timestamp=datetime.fromisoformat(row[8]),
                quality_score=row[7]
            )
            
            cached_translation = CachedTranslation(
                content_hash=row[0],
                translation_result=translation_result,
                created_at=datetime.fromisoformat(row[8]),
                expires_at=expires_at,
                usage_count=usage_count
            )
            # 确保content_hash与数据库中的一致
            cached_translation.content_hash = row[0]
            return cached_translation
    
    def put(self, key: str, value: CachedTranslation):
        """存储缓存项"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO translation_cache 
                (content_hash, original_text, translated_text, source_language, 
                 target_language, service_name, confidence_score, quality_score,
                 created_at, expires_at, usage_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                value.content_hash,  # 使用CachedTranslation中的content_hash
                value.translation_result.original_text,
                value.translation_result.translated_text,
                value.translation_result.source_language,
                value.translation_result.target_language,
                value.translation_result.service_name,
                value.translation_result.confidence_score,
                value.translation_result.quality_score,
                value.created_at.isoformat(),
                value.expires_at.isoformat(),
                value.usage_count,
                datetime.now().isoformat()
            ))
    
    def clear_expired(self) -> int:
        """清理过期项"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                DELETE FROM translation_cache WHERE expires_at < ?
            """, (datetime.now().isoformat(),))
            
            return cursor.rowcount
    
    def get_cache_stats(self) -> Dict[str, int]:
        """获取缓存统计信息"""
        with sqlite3.connect(self.db_path) as conn:
            # 总缓存项数
            total_items = conn.execute("SELECT COUNT(*) FROM translation_cache").fetchone()[0]
            
            # 过期项数
            expired_items = conn.execute("""
                SELECT COUNT(*) FROM translation_cache WHERE expires_at < ?
            """, (datetime.now().isoformat(),)).fetchone()[0]
            
            # 各服务的缓存项数
            service_stats = conn.execute("""
                SELECT service_name, COUNT(*) FROM translation_cache 
                WHERE expires_at >= ?
                GROUP BY service_name
            """, (datetime.now().isoformat(),)).fetchall()
            
            return {
                'total_items': total_items,
                'expired_items': expired_items,
                'valid_items': total_items - expired_items,
                'service_distribution': dict(service_stats)
            }


class SmartTranslationCache(ITranslationCache):
    """智能翻译缓存系统 - 多级缓存架构"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化智能缓存系统
        
        Args:
            config: 缓存配置
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化各级缓存
        self.memory_cache = MemoryCache(
            max_size=self.config.get('memory_cache_size', 1000),
            ttl_seconds=self.config.get('memory_ttl_seconds', 3600)
        )
        
        self.file_cache = FileCache(
            cache_dir=self.config.get('file_cache_dir', 'translation_cache'),
            max_files=self.config.get('max_cache_files', 10000)
        )
        
        self.db_cache = DatabaseCache(
            db_path=self.config.get('db_cache_path', 'translation_cache.db')
        )
        
        # 缓存统计
        self.stats = CacheStats()
        
        # 自动清理配置
        self.auto_cleanup_enabled = self.config.get('auto_cleanup', True)
        self.cleanup_interval = self.config.get('cleanup_interval_hours', 24)
        self.last_cleanup = datetime.now()
        
        # 启动后台清理任务
        if self.auto_cleanup_enabled:
            self._start_cleanup_thread()
    
    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """生成缓存键（基于内容哈希）"""
        content = f"{text}|{source_lang}|{target_lang}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def get_translation(self, content_hash: str) -> Optional[CachedTranslation]:
        """获取缓存的翻译"""
        self.stats.total_requests += 1
        
        # 1. 首先检查内存缓存
        cached_item = self.memory_cache.get(content_hash)
        if cached_item:
            self.stats.cache_hits += 1
            self.stats.memory_cache_hits += 1
            return cached_item
        
        # 2. 检查文件缓存
        cached_item = self.file_cache.get(content_hash)
        if cached_item:
            self.stats.cache_hits += 1
            self.stats.file_cache_hits += 1
            # 将结果放入内存缓存
            self.memory_cache.put(content_hash, cached_item)
            return cached_item
        
        # 3. 检查数据库缓存
        cached_item = self.db_cache.get(content_hash)
        if cached_item:
            self.stats.cache_hits += 1
            self.stats.db_cache_hits += 1
            # 将结果放入上级缓存
            self.file_cache.put(content_hash, cached_item)
            self.memory_cache.put(content_hash, cached_item)
            return cached_item
        
        # 缓存未命中
        self.stats.cache_misses += 1
        return None
    
    def save_translation(self, content_hash: str, translation: TranslationResult) -> bool:
        """保存翻译到缓存"""
        try:
            # 创建缓存项
            expires_at = datetime.now() + timedelta(
                days=self.config.get('cache_ttl_days', 30)
            )
            
            cached_translation = CachedTranslation(
                content_hash=content_hash,
                translation_result=translation,
                created_at=datetime.now(),
                expires_at=expires_at,
                usage_count=0
            )
            
            # 保存到所有缓存层
            self.memory_cache.put(content_hash, cached_translation)
            self.file_cache.put(content_hash, cached_translation)
            self.db_cache.put(content_hash, cached_translation)
            
            self.stats.total_cached_items += 1
            return True
        
        except Exception as e:
            self.logger.error(f"保存缓存失败: {e}")
            return False
    
    def get_cached_translation(self, text: str, source_lang: str = 'en', 
                             target_lang: str = 'zh') -> Optional[CachedTranslation]:
        """根据文本内容获取缓存的翻译"""
        content_hash = self._generate_cache_key(text, source_lang, target_lang)
        return self.get_translation(content_hash)
    
    def cache_translation(self, text: str, translation: TranslationResult,
                         source_lang: str = 'en', target_lang: str = 'zh') -> bool:
        """缓存翻译结果"""
        content_hash = self._generate_cache_key(text, source_lang, target_lang)
        return self.save_translation(content_hash, translation)
    
    def clear_expired_cache(self) -> int:
        """清理过期缓存"""
        total_cleared = 0
        
        # 清理各级缓存的过期项
        total_cleared += self.memory_cache.clear_expired()
        total_cleared += self.file_cache.clear_expired()
        total_cleared += self.db_cache.clear_expired()
        
        self.logger.info(f"清理了 {total_cleared} 个过期缓存项")
        return total_cleared
    
    def get_cache_statistics(self) -> Dict[str, any]:
        """获取缓存统计信息"""
        db_stats = self.db_cache.get_cache_stats()
        
        return {
            'hit_rate': self.stats.hit_rate,
            'memory_hit_rate': self.stats.memory_hit_rate,
            'total_requests': self.stats.total_requests,
            'cache_hits': self.stats.cache_hits,
            'cache_misses': self.stats.cache_misses,
            'memory_cache_hits': self.stats.memory_cache_hits,
            'file_cache_hits': self.stats.file_cache_hits,
            'db_cache_hits': self.stats.db_cache_hits,
            'memory_cache_size': self.memory_cache.size(),
            'database_stats': db_stats,
            'last_cleanup': self.last_cleanup.isoformat()
        }
    
    def _start_cleanup_thread(self):
        """启动后台清理线程"""
        def cleanup_worker():
            while True:
                try:
                    # 等待清理间隔
                    time.sleep(self.cleanup_interval * 3600)  # 转换为秒
                    
                    # 执行清理
                    self.clear_expired_cache()
                    self.last_cleanup = datetime.now()
                    
                except Exception as e:
                    self.logger.error(f"后台清理任务失败: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        self.logger.info("后台清理线程已启动")
    
    def optimize_cache_performance(self) -> Dict[str, any]:
        """优化缓存性能"""
        optimization_results = {
            'actions_taken': [],
            'before_stats': self.get_cache_statistics()
        }
        
        # 清理过期缓存
        expired_count = self.clear_expired_cache()
        if expired_count > 0:
            optimization_results['actions_taken'].append(f"清理了 {expired_count} 个过期项")
        
        # 如果内存缓存命中率低，可以考虑增加内存缓存大小
        if self.stats.memory_hit_rate < 0.3 and self.stats.total_requests > 100:
            optimization_results['actions_taken'].append("建议增加内存缓存大小以提高命中率")
        
        # 如果总命中率低，建议检查缓存策略
        if self.stats.hit_rate < 0.5 and self.stats.total_requests > 50:
            optimization_results['actions_taken'].append("建议检查缓存策略，当前命中率较低")
        
        optimization_results['after_stats'] = self.get_cache_statistics()
        return optimization_results