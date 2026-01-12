

import hashlib
import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from threading import Lock

logger = logging.getLogger(__name__)

class CacheManager:
    
    
    def __init__(
        self,
        cache_file: str = "cache.json",
        ttl_hours: int = 24
    ):
        
        self.cache_file = cache_file
        self.ttl_hours = ttl_hours
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0
        self._lock = Lock()
        
        self._load_cache()
        
        self._cleanup_expired()
        
        logger.info(f"CacheManager initialized with {len(self.cache)} entries, TTL={ttl_hours}h")
    
    def _generate_key(self, text: str) -> str:
        
        normalized = text.lower().strip()
        hash_obj = hashlib.md5(normalized.encode('utf-8'))
        return hash_obj.hexdigest()[:12]
    
    def _load_cache(self) -> None:
        
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.debug(f"Loaded {len(self.cache)} entries from cache file")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load cache file: {e}")
            self.cache = {}
    
    def _save_cache(self) -> None:
        
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, default=str)
            logger.debug(f"Saved {len(self.cache)} entries to cache file")
        except IOError as e:
            logger.error(f"Failed to save cache file: {e}")
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        
        try:
            timestamp_str = entry.get('timestamp')
            if not timestamp_str:
                return True
            
            timestamp = datetime.fromisoformat(timestamp_str)
            expiry = timestamp + timedelta(hours=self.ttl_hours)
            return datetime.now() > expiry
        except (ValueError, TypeError):
            return True
    
    def _cleanup_expired(self) -> None:
        
        with self._lock:
            original_count = len(self.cache)
            self.cache = {
                key: value
                for key, value in self.cache.items()
                if not self._is_expired(value)
            }
            removed = original_count - len(self.cache)
            if removed > 0:
                logger.info(f"Cleaned up {removed} expired cache entries")
                self._save_cache()
    
    def get(self, text: str) -> Optional[Dict[str, Any]]:
        
        key = self._generate_key(text)
        
        if hash(key) % 100 == 0:
            self._cleanup_expired()
        
        with self._lock:
            entry = self.cache.get(key)
            
            if entry is None:
                self.misses += 1
                return None
            
            if self._is_expired(entry):
                self.misses += 1
                del self.cache[key]
                self._save_cache()
                return None
            
            self.hits += 1
            result = entry.get('result')
            if result:
                result['cached'] = True
            return result
    
    def set(self, text: str, result: Dict[str, Any]) -> None:
        
        key = self._generate_key(text)
        
        with self._lock:
            self.cache[key] = {
                'timestamp': datetime.now().isoformat(),
                'text_preview': text[:100] + '...' if len(text) > 100 else text,
                'result': result
            }
            
            self._save_cache()
            
            logger.debug(f"Cached result with key {key}")
    
    def clear(self) -> None:
        
        with self._lock:
            self.cache = {}
            self.hits = 0
            self.misses = 0
            self._save_cache()
            logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        try:
            size_bytes = os.path.getsize(self.cache_file) if os.path.exists(self.cache_file) else 0
        except OSError:
            size_bytes = 0
        
        return {
            "total_entries": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 4),
            "size_bytes": size_bytes,
            "ttl_hours": self.ttl_hours
        }
    
    def get_recent_entries(self, limit: int = 10) -> list:
        
        entries = []
        for key, value in self.cache.items():
            entries.append({
                "key": key,
                "timestamp": value.get("timestamp"),
                "preview": value.get("text_preview", ""),
                "prediction": value.get("result", {}).get("prediction", "N/A")
            })
        
        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return entries[:limit]
