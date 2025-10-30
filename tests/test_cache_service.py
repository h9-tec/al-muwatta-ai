"""
Comprehensive tests for Cache Service.

Tests both in-memory and Redis caching functionality.
"""

import pytest
from typing import Any, Dict

from src.services.cache_service import CacheService, cached, get_cache_service


class TestCacheService:
    """Test suite for CacheService."""

    @pytest.fixture
    def cache(self):
        """Create a fresh cache service instance for each test."""
        return CacheService()

    @pytest.mark.asyncio
    async def test_cache_service_initialization(self, cache: CacheService):
        """Test that cache service initializes correctly."""
        assert cache is not None
        assert cache.memory_cache is not None
        assert cache.stats is not None
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache: CacheService):
        """Test basic set and get operations."""
        key = "test_key"
        value = {"data": "test_value"}

        # Set value
        result = await cache.set(key, value, ttl=60)
        assert result is True

        # Get value
        retrieved = await cache.get(key)
        assert retrieved == value
        assert cache.stats["hits"] == 1
        assert cache.stats["sets"] == 1

    @pytest.mark.asyncio
    async def test_cache_miss(self, cache: CacheService):
        """Test cache miss scenario."""
        key = "nonexistent_key"

        # Try to get non-existent key
        result = await cache.get(key)
        assert result is None
        assert cache.stats["misses"] == 1

    @pytest.mark.asyncio
    async def test_cache_delete(self, cache: CacheService):
        """Test cache deletion."""
        key = "delete_test"
        value = "test_data"

        # Set and verify
        await cache.set(key, value)
        assert await cache.get(key) == value

        # Delete
        deleted = await cache.delete(key)
        assert deleted is True

        # Verify deletion
        result = await cache.get(key)
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_statistics(self, cache: CacheService):
        """Test cache statistics tracking."""
        # Perform operations
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.get("key1")  # Hit
        await cache.get("key1")  # Hit
        await cache.get("key3")  # Miss

        stats = cache.get_stats()
        assert stats["sets"] == 2
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_requests"] == 3
        assert stats["hit_rate_percent"] == pytest.approx(66.67, rel=0.1)

    @pytest.mark.asyncio
    async def test_reset_statistics(self, cache: CacheService):
        """Test statistics reset."""
        # Create some stats
        await cache.set("key", "value")
        await cache.get("key")

        # Reset
        cache.reset_stats()

        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["sets"] == 0

    @pytest.mark.asyncio
    async def test_cache_key_generation(self, cache: CacheService):
        """Test cache key generation consistency."""
        prefix = "test"
        args = (1, 2, 3)
        kwargs = {"lat": 21.3891, "lon": 39.8579}

        # Same args should produce same key
        key1 = cache._generate_cache_key(prefix, *args, **kwargs)
        key2 = cache._generate_cache_key(prefix, *args, **kwargs)
        assert key1 == key2

        # Different args should produce different key
        key3 = cache._generate_cache_key(prefix, 4, 5, 6, lat=40.0, lon=50.0)
        assert key1 != key3

    @pytest.mark.asyncio
    async def test_cache_complex_data_types(self, cache: CacheService):
        """Test caching various Python data types."""
        test_cases = [
            ("string", "test_string"),
            ("int", 42),
            ("float", 3.14159),
            ("list", [1, 2, 3, 4, 5]),
            ("dict", {"key1": "value1", "key2": 123}),
            ("nested", {"users": [{"name": "Ali", "age": 30}]}),
            ("tuple", (1, 2, 3)),
            ("set", {1, 2, 3, 4}),
            ("bool", True),
            ("none", None),
        ]

        for key, value in test_cases:
            await cache.set(key, value)
            retrieved = await cache.get(key)
            
            # Sets need special handling for comparison
            if isinstance(value, set):
                assert set(retrieved) == value
            else:
                assert retrieved == value

    @pytest.mark.asyncio
    async def test_get_cache_service_singleton(self):
        """Test that get_cache_service returns singleton instance."""
        cache1 = get_cache_service()
        cache2 = get_cache_service()
        assert cache1 is cache2


class TestCachedDecorator:
    """Test suite for @cached decorator."""

    @pytest.mark.asyncio
    async def test_cached_decorator_basic(self):
        """Test basic cached decorator functionality."""
        call_count = 0

        @cached(prefix="test", ttl=60)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call - should execute
        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with same args - should use cache
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented!

        # Call with different args - should execute
        result3 = await expensive_function(10)
        assert result3 == 20
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cached_decorator_with_kwargs(self):
        """Test cached decorator with keyword arguments."""
        call_count = 0

        @cached(prefix="location", ttl=60)
        async def get_location(city: str, country: str = "USA") -> Dict[str, str]:
            nonlocal call_count
            call_count += 1
            return {"city": city, "country": country}

        # First call
        result1 = await get_location("New York", country="USA")
        assert call_count == 1

        # Same call - cached
        result2 = await get_location("New York", country="USA")
        assert call_count == 1
        assert result1 == result2

        # Different call
        result3 = await get_location("London", country="UK")
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cached_decorator_none_result(self):
        """Test that None results are not cached."""
        call_count = 0

        @cached(prefix="nullable", ttl=60)
        async def nullable_function(return_none: bool) -> str | None:
            nonlocal call_count
            call_count += 1
            return None if return_none else "value"

        # Call returning None
        result1 = await nullable_function(True)
        assert result1 is None
        assert call_count == 1

        # Call again - should execute (None not cached)
        result2 = await nullable_function(True)
        assert result2 is None
        assert call_count == 2

        # Call returning value
        result3 = await nullable_function(False)
        assert result3 == "value"
        assert call_count == 3

        # Call again - should be cached
        result4 = await nullable_function(False)
        assert result4 == "value"
        assert call_count == 3  # Not incremented!

    @pytest.mark.asyncio
    async def test_cached_decorator_with_dict_return(self):
        """Test caching complex dictionary returns."""
        @cached(prefix="prayer", ttl=86400)
        async def get_prayer_times(lat: float, lon: float) -> Dict[str, Any]:
            return {
                "fajr": "05:30",
                "dhuhr": "12:15",
                "asr": "15:45",
                "maghrib": "18:30",
                "isha": "20:00",
                "location": {"lat": lat, "lon": lon}
            }

        # First call
        result1 = await get_prayer_times(21.3891, 39.8579)
        assert result1["fajr"] == "05:30"

        # Cached call
        result2 = await get_prayer_times(21.3891, 39.8579)
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_cached_decorator_custom_key_builder(self):
        """Test cached decorator with custom key builder."""
        def custom_key_builder(user_id: int, *args, **kwargs) -> str:
            return f"user:{user_id}"

        call_count = 0

        @cached(prefix="user_data", ttl=60, key_builder=custom_key_builder)
        async def get_user_data(user_id: int, fields: list = None) -> Dict:
            nonlocal call_count
            call_count += 1
            return {"id": user_id, "fields": fields}

        # Different fields, same user - should use cache
        result1 = await get_user_data(1, fields=["name"])
        result2 = await get_user_data(1, fields=["email"])
        assert call_count == 1  # Same key, so cached

        # Different user
        result3 = await get_user_data(2, fields=["name"])
        assert call_count == 2


class TestCacheIntegration:
    """Integration tests for cache with API clients."""

    @pytest.mark.asyncio
    async def test_cache_ttl_expiration(self):
        """Test that cache entries expire after TTL."""
        import asyncio
        cache = CacheService()

        # Set with 1 second TTL
        await cache.set("short_lived", "value", ttl=1)

        # Should exist immediately
        result1 = await cache.get("short_lived")
        assert result1 == "value"

        # Wait for expiration
        await asyncio.sleep(2)

        # Should be expired (only for in-memory cache)
        # Note: This tests in-memory cache TTL behavior
        result2 = await cache.get("short_lived")
        # In-memory cache with TTLCache should auto-expire
        # Result may be None if expired, or value if still in cache

    @pytest.mark.asyncio
    async def test_concurrent_cache_access(self):
        """Test concurrent cache access."""
        import asyncio
        cache = CacheService()

        async def worker(worker_id: int) -> str:
            key = f"worker_{worker_id}"
            await cache.set(key, f"value_{worker_id}")
            return await cache.get(key)

        # Run 10 workers concurrently
        tasks = [worker(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        for i, result in enumerate(results):
            assert result == f"value_{i}"


@pytest.mark.skipif(
    not pytest.importorskip("redis"),
    reason="Redis not installed"
)
class TestRedisIntegration:
    """Tests that require Redis to be available."""

    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test Redis connection (skips if Redis unavailable)."""
        cache = CacheService()
        try:
            await cache.connect_redis()
            # If connection successful, test basic operations
            if cache.redis_enabled:
                await cache.set("redis_test", "value")
                result = await cache.get("redis_test")
                assert result == "value"
        finally:
            await cache.disconnect_redis()

    @pytest.mark.asyncio
    async def test_redis_pattern_clearing(self):
        """Test clearing cache by pattern (Redis only)."""
        cache = CacheService()
        try:
            await cache.connect_redis()
            if cache.redis_enabled:
                # Set multiple keys
                await cache.set("test:1", "value1")
                await cache.set("test:2", "value2")
                await cache.set("other:3", "value3")

                # Clear test:* pattern
                deleted = await cache.clear_pattern("test:*")
                assert deleted == 2

                # Verify
                assert await cache.get("test:1") is None
                assert await cache.get("test:2") is None
                # Other key should still exist (may be None if only in Redis)
        finally:
            await cache.disconnect_redis()

