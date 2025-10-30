"""
Cache Service for Al-Muwatta API.

Implements a dual-layer caching strategy:
1. Redis (primary) - Distributed, persistent cache
2. In-Memory (fallback) - Local LRU cache when Redis unavailable

This service provides significant performance improvements for external API calls.
"""

import hashlib
import json
import pickle
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast
from datetime import timedelta

from loguru import logger

try:
    import redis.asyncio as aioredis
    from redis.asyncio import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis.asyncio not available, falling back to in-memory cache")

from cachetools import TTLCache

from ..config import settings


# Type variable for generic function decoration
F = TypeVar('F', bound=Callable[..., Any])


class CacheService:
    """
    Dual-layer caching service with Redis primary and in-memory fallback.
    
    Features:
    - Async Redis operations
    - In-memory LRU cache with TTL
    - Automatic serialization/deserialization
    - Cache key generation with hashing
    - Statistics tracking
    
    Example:
        >>> cache = CacheService()
        >>> await cache.set("prayer_times:cairo", data, ttl=86400)
        >>> result = await cache.get("prayer_times:cairo")
    """
    
    def __init__(self) -> None:
        """Initialize cache service with Redis and in-memory stores."""
        self.redis_client: Optional[Redis] = None
        self.redis_enabled = False
        
        # In-memory cache: 1000 items, 1 hour default TTL
        self.memory_cache: TTLCache = TTLCache(maxsize=1000, ttl=3600)
        
        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "redis_hits": 0,
            "memory_hits": 0,
            "sets": 0,
            "errors": 0,
        }
        
        logger.info("🔧 Cache service initialized (in-memory mode)")
    
    async def connect_redis(self) -> None:
        """
        Connect to Redis if available and configured.
        
        This should be called during application startup.
        """
        if not REDIS_AVAILABLE:
            logger.warning("Redis library not installed, using in-memory cache only")
            return
        
        if not settings.redis_url:
            logger.info("No Redis URL configured, using in-memory cache only")
            return
        
        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=False,  # We'll handle serialization
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            
            # Test connection
            await self.redis_client.ping()
            self.redis_enabled = True
            logger.info(f"✅ Redis connected: {settings.redis_url}")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}, using in-memory cache only")
            self.redis_client = None
            self.redis_enabled = False
    
    async def disconnect_redis(self) -> None:
        """Disconnect from Redis gracefully."""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
    
    def _generate_cache_key(self, prefix: str, *args: Any, **kwargs: Any) -> str:
        """
        Generate a consistent cache key from function arguments.
        
        Args:
            prefix: Cache key prefix (e.g., "quran", "prayer_times")
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Hashed cache key string
        """
        # Create deterministic string from args and kwargs
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()),  # Sort for consistency
        }
        
        # JSON serialize and hash
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:16]
        
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (tries Redis first, then in-memory).
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        try:
            # Try Redis first
            if self.redis_enabled and self.redis_client:
                try:
                    value = await self.redis_client.get(key)
                    if value is not None:
                        self.stats["hits"] += 1
                        self.stats["redis_hits"] += 1
                        # Deserialize from pickle
                        return pickle.loads(value)
                except Exception as e:
                    logger.error(f"Redis get error: {e}")
                    self.stats["errors"] += 1
            
            # Fallback to in-memory cache
            if key in self.memory_cache:
                self.stats["hits"] += 1
                self.stats["memory_hits"] += 1
                return self.memory_cache[key]
            
            # Cache miss
            self.stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats["errors"] += 1
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache (both Redis and in-memory).
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default from settings)
        
        Returns:
            True if successful
        """
        try:
            ttl_seconds = ttl or settings.cache_ttl
            self.stats["sets"] += 1
            
            # Store in Redis
            if self.redis_enabled and self.redis_client:
                try:
                    serialized = pickle.dumps(value)
                    await self.redis_client.setex(
                        key,
                        ttl_seconds,
                        serialized,
                    )
                except Exception as e:
                    logger.error(f"Redis set error: {e}")
                    self.stats["errors"] += 1
            
            # Always store in memory cache as backup
            self.memory_cache[key] = value
            
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
        
        Returns:
            True if deleted
        """
        try:
            # Delete from Redis
            if self.redis_enabled and self.redis_client:
                try:
                    await self.redis_client.delete(key)
                except Exception as e:
                    logger.error(f"Redis delete error: {e}")
            
            # Delete from memory
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """
        Clear all keys matching pattern (Redis only).
        
        Args:
            pattern: Key pattern (e.g., "prayer_times:*")
        
        Returns:
            Number of keys deleted
        """
        if not self.redis_enabled or not self.redis_client:
            return 0
        
        try:
            cursor = 0
            deleted = 0
            
            while True:
                cursor, keys = await self.redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100,
                )
                
                if keys:
                    deleted += await self.redis_client.delete(*keys)
                
                if cursor == 0:
                    break
            
            logger.info(f"Cleared {deleted} keys matching pattern: {pattern}")
            return deleted
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "redis_hits": self.stats["redis_hits"],
            "memory_hits": self.stats["memory_hits"],
            "sets": self.stats["sets"],
            "errors": self.stats["errors"],
            "total_requests": total_requests,
            "hit_rate_percent": round(hit_rate, 2),
            "redis_enabled": self.redis_enabled,
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
        }
    
    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self.stats = {
            "hits": 0,
            "misses": 0,
            "redis_hits": 0,
            "memory_hits": 0,
            "sets": 0,
            "errors": 0,
        }
        logger.info("Cache statistics reset")


# Global cache service instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """
    Get or create the global cache service instance.
    
    Returns:
        CacheService instance
    """
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


def cached(
    prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable[..., str]] = None,
) -> Callable[[F], F]:
    """
    Decorator to cache async function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time-to-live in seconds
        key_builder: Optional custom key builder function
    
    Returns:
        Decorated function
    
    Example:
        >>> @cached(prefix="quran", ttl=86400)
        >>> async def get_surah(surah_number: int):
        ...     return await api.get(f"/surah/{surah_number}")
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache_service()
            
            # Generate cache key
            if key_builder:
                cache_key = key_builder(*args, **kwargs)
            else:
                cache_key = cache._generate_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value
            
            # Cache miss - call function
            logger.debug(f"Cache MISS: {cache_key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                await cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return cast(F, wrapper)
    
    return decorator

