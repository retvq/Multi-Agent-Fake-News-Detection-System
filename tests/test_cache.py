

import pytest
import sys
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cache import CacheManager

@pytest.fixture
def temp_cache_file():
    
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def cache_manager(temp_cache_file):
    
    return CacheManager(cache_file=temp_cache_file, ttl_hours=24)

class TestCacheBasicOperations:
    
    
    def test_set_and_get(self, cache_manager):
        
        text = "Sample news article for testing"
        result = {"prediction": "REAL", "fake_probability": 0.2}
        
        cache_manager.set(text, result)
        cached = cache_manager.get(text)
        
        assert cached is not None
        assert cached['prediction'] == "REAL"
        assert cached['fake_probability'] == 0.2
    
    def test_get_nonexistent(self, cache_manager):
        
        cached = cache_manager.get("This text does not exist in cache")
        assert cached is None
    
    def test_cache_miss_counter(self, cache_manager):
        
        cache_manager.get("Nonexistent text")
        
        stats = cache_manager.stats()
        assert stats['misses'] >= 1
    
    def test_cache_hit_counter(self, cache_manager):
        
        text = "Test article"
        cache_manager.set(text, {"prediction": "FAKE"})
        cache_manager.get(text)
        
        stats = cache_manager.stats()
        assert stats['hits'] >= 1

class TestCacheNormalization:
    
    
    def test_case_insensitive(self, cache_manager):
        
        text_lower = "this is a test article"
        text_upper = "THIS IS A TEST ARTICLE"
        
        result = {"prediction": "REAL"}
        cache_manager.set(text_lower, result)
        
        cached = cache_manager.get(text_upper)
        assert cached is not None
        assert cached['prediction'] == "REAL"
    
    def test_whitespace_normalized(self, cache_manager):
        
        text_with_spaces = "  Test article with spaces  "
        text_stripped = "Test article with spaces"
        
        result = {"prediction": "FAKE"}
        cache_manager.set(text_with_spaces, result)
        
        cached = cache_manager.get(text_stripped)
        assert cached is not None

class TestCacheExpiration:
    
    
    def test_fresh_entry_not_expired(self, cache_manager):
        
        text = "Fresh news article"
        result = {"prediction": "REAL"}
        
        cache_manager.set(text, result)
        cached = cache_manager.get(text)
        
        assert cached is not None
    
    def test_expired_entry_returns_none(self, temp_cache_file):
        
        cache_manager = CacheManager(cache_file=temp_cache_file, ttl_hours=0)
        
        text = "Old news article"
        result = {"prediction": "FAKE"}
        
        old_timestamp = (datetime.now() - timedelta(hours=25)).isoformat()
        cache_manager.cache = {
            "test_key": {
                "timestamp": old_timestamp,
                "result": result
            }
        }
        
        assert cache_manager._is_expired({"timestamp": old_timestamp})

class TestCachePersistence:
    
    
    def test_save_to_file(self, temp_cache_file, cache_manager):
        
        cache_manager.set("Test", {"prediction": "REAL"})
        
        assert os.path.exists(temp_cache_file)
        
        with open(temp_cache_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) > 0
    
    def test_load_from_file(self, temp_cache_file):
        
        test_data = {
            "abc123": {
                "timestamp": datetime.now().isoformat(),
                "result": {"prediction": "FAKE"}
            }
        }
        
        with open(temp_cache_file, 'w') as f:
            json.dump(test_data, f)
        
        cache_manager = CacheManager(cache_file=temp_cache_file)
        
        assert len(cache_manager.cache) == 1

class TestCacheStatistics:
    
    
    def test_stats_structure(self, cache_manager):
        
        stats = cache_manager.stats()
        
        assert 'total_entries' in stats
        assert 'hits' in stats
        assert 'misses' in stats
        assert 'hit_rate' in stats
        assert 'size_bytes' in stats
        assert 'ttl_hours' in stats
    
    def test_hit_rate_calculation(self, cache_manager):
        
        text = "Test article"
        cache_manager.set(text, {"prediction": "REAL"})
        
        cache_manager.get(text)
        cache_manager.get(text)
        
        cache_manager.get("Nonexistent")
        
        stats = cache_manager.stats()
        
        assert stats['hit_rate'] > 0.6
    
    def test_zero_requests_hit_rate(self, cache_manager):
        
        stats = cache_manager.stats()
        assert stats['hit_rate'] == 0.0

class TestCacheClear:
    
    
    def test_clear_removes_entries(self, cache_manager):
        
        cache_manager.set("Article 1", {"prediction": "FAKE"})
        cache_manager.set("Article 2", {"prediction": "REAL"})
        
        assert len(cache_manager.cache) == 2
        
        cache_manager.clear()
        
        assert len(cache_manager.cache) == 0
    
    def test_clear_resets_counters(self, cache_manager):
        
        cache_manager.set("Test", {"prediction": "REAL"})
        cache_manager.get("Test")
        cache_manager.get("Other")
        
        cache_manager.clear()
        
        stats = cache_manager.stats()
        assert stats['hits'] == 0
        assert stats['misses'] == 0

class TestCacheRecentEntries:
    
    
    def test_get_recent_entries(self, cache_manager):
        
        for i in range(5):
            cache_manager.set(f"Article {i}", {"prediction": "REAL"})
        
        recent = cache_manager.get_recent_entries(limit=3)
        
        assert len(recent) == 3
        assert all('key' in entry for entry in recent)
        assert all('timestamp' in entry for entry in recent)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
