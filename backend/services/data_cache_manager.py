"""
Data Cache Manager
SQLite-based caching with TTL management
"""
import sqlite3
import json
import time
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import os

class DataCacheManager:
    def __init__(self, db_path: str = "data/cache.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with cache tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                category TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                expires_at INTEGER NOT NULL
            )
        ''')
        
        # Create index on expiration
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expires_at ON cache(expires_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def set(self, key: str, value: Any, category: str = "general", ttl: int = 3600):
        """
        Store value in cache
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            category: Cache category (fundamentals, news, etc.)
            ttl: Time to live in seconds
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = int(time.time())
        expires_at = now + ttl
        
        cursor.execute('''
            INSERT OR REPLACE INTO cache (key, value, category, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (key, json.dumps(value), category, now, expires_at))
        
        conn.commit()
        conn.close()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = int(time.time())
        
        cursor.execute('''
            SELECT value, expires_at FROM cache WHERE key = ?
        ''', (key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            return None
        
        value, expires_at = result
        
        # Check if expired
        if expires_at < now:
            self.delete(key)
            return None
        
        return json.loads(value)
    
    def delete(self, key: str):
        """Delete cache entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
        conn.commit()
        conn.close()
    
    def clear_expired(self):
        """Remove all expired cache entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = int(time.time())
        cursor.execute('DELETE FROM cache WHERE expires_at < ?', (now,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_category(self, category: str):
        """Clear all cache entries in a category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cache WHERE category = ?', (category,))
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = int(time.time())
        
        # Total entries
        cursor.execute('SELECT COUNT(*) FROM cache')
        total = cursor.fetchone()[0]
        
        # Valid entries
        cursor.execute('SELECT COUNT(*) FROM cache WHERE expires_at >= ?', (now,))
        valid = cursor.fetchone()[0]
        
        # Expired entries
        expired = total - valid
        
        # By category
        cursor.execute('''
            SELECT category, COUNT(*) 
            FROM cache 
            WHERE expires_at >= ?
            GROUP BY category
        ''', (now,))
        by_category = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total": total,
            "valid": valid,
            "expired": expired,
            "by_category": by_category
        }


# Singleton instance
_cache_manager = None

def get_cache() -> DataCacheManager:
    """Get or create cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = DataCacheManager()
    return _cache_manager
