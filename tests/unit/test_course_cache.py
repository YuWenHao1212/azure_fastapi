"""Test Course Cache Service"""
import time

from src.services.course_cache import CourseSearchCache


def test_cache_basic_operations():
    """測試快取基本操作"""
    cache = CourseSearchCache(ttl_seconds=2)
    
    # 測試生成鍵值
    key = cache.get_cache_key("Python", "for data science", "Tech", 0.7)
    assert isinstance(key, str)
    assert len(key) == 32  # MD5 hash length
    
    # 測試存取資料
    test_data = {"test": "data"}
    cache.set(key, test_data)
    
    retrieved = cache.get(key)
    assert retrieved == test_data
    
    # 測試快取過期
    time.sleep(3)
    expired = cache.get(key)
    assert expired is None


def test_cache_size_limit():
    """測試快取大小限制"""
    cache = CourseSearchCache(ttl_seconds=300, max_size=3)
    
    # 加入 4 個項目，第一個應該被移除
    for i in range(4):
        key = f"key_{i}"
        cache.set(key, {"value": i})
        time.sleep(0.1)  # 確保時間戳不同
    
    # 檢查快取大小
    assert cache.stats()["size"] == 3
    
    # 第一個項目應該被移除
    assert cache.get("key_0") is None
    assert cache.get("key_1") is not None
    assert cache.get("key_3") is not None


def test_cache_clear():
    """測試清空快取"""
    cache = CourseSearchCache()
    
    # 加入資料
    cache.set("key1", {"data": 1})
    cache.set("key2", {"data": 2})
    
    assert cache.stats()["size"] == 2
    
    # 清空快取
    cache.clear()
    assert cache.stats()["size"] == 0
    assert cache.get("key1") is None


def test_cache_key_consistency():
    """測試鍵值一致性"""
    cache = CourseSearchCache()
    
    # 相同輸入應該產生相同鍵值
    key1 = cache.get_cache_key("Python", "data analysis", "Tech", 0.7)
    key2 = cache.get_cache_key("Python", "data analysis", "Tech", 0.7)
    assert key1 == key2
    
    # 不同輸入應該產生不同鍵值
    key3 = cache.get_cache_key("Python", "web development", "Tech", 0.7)
    assert key1 != key3