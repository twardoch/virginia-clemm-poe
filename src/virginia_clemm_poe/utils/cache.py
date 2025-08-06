# this_file: src/virginia_clemm_poe/utils/cache.py
"""Caching utilities for Virginia Clemm Poe.

This module provides caching utilities with configurable TTL (Time To Live)
to reduce API calls and improve performance. Targets 80% cache hit rate
for optimal performance while maintaining data freshness.
"""

import asyncio
import hashlib
import json
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from loguru import logger

from ..utils.logger import log_performance_metric

T = TypeVar("T")

# Cache configuration
DEFAULT_TTL_SECONDS = 300  # 5 minutes default TTL
API_CACHE_TTL_SECONDS = 600  # 10 minutes for API responses
MODEL_CACHE_TTL_SECONDS = 1800  # 30 minutes for model data
SCRAPING_CACHE_TTL_SECONDS = 3600  # 1 hour for scraped data
MAX_CACHE_SIZE = 1000  # Maximum number of cached items
CACHE_CLEANUP_INTERVAL = 300  # Clean up expired items every 5 minutes


class CacheEntry:
    """Represents a cached item with metadata."""

    def __init__(self, key: str, value: Any, ttl_seconds: float, timestamp: float | None = None):
        """Initialize cache entry.

        Args:
            key: Cache key
            value: Cached value
            ttl_seconds: Time to live in seconds
            timestamp: When the item was cached (defaults to now)
        """
        self.key = key
        self.value = value
        self.ttl_seconds = ttl_seconds
        self.timestamp = timestamp or time.time()
        self.hit_count = 0
        self.last_accessed = self.timestamp

    def is_expired(self) -> bool:
        """Check if the cache entry has expired.

        Returns:
            True if the entry has expired
        """
        return time.time() - self.timestamp > self.ttl_seconds

    def access(self) -> Any:
        """Access the cached value and update statistics.

        Returns:
            The cached value
        """
        self.hit_count += 1
        self.last_accessed = time.time()
        return self.value

    def age_seconds(self) -> float:
        """Get the age of the cache entry in seconds.

        Returns:
            Age in seconds
        """
        return time.time() - self.timestamp


class Cache:
    """In-memory cache with TTL and LRU eviction."""

    def __init__(self, max_size: int = MAX_CACHE_SIZE, default_ttl: float = DEFAULT_TTL_SECONDS):
        """Initialize the cache.

        Args:
            max_size: Maximum number of items to cache
            default_ttl: Default TTL in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expired_removals": 0,
        }

    def _generate_key(self, *args: Any, **kwargs: Any) -> str:
        """Generate a cache key from function arguments.

        Args:
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Cache key string
        """
        # Create a stable representation of the arguments
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()) if kwargs else {},
        }

        # Serialize to JSON and hash
        key_json = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_json.encode()).hexdigest()[:16]

        return f"cache_{key_hash}"

    async def get(self, key: str) -> Any | None:
        """Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._stats["misses"] += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._stats["expired_removals"] += 1
                self._stats["misses"] += 1
                logger.debug(f"Cache entry {key} expired and removed")
                return None

            self._stats["hits"] += 1
            logger.debug(f"Cache hit for key {key} (age: {entry.age_seconds():.1f}s)")
            return entry.access()

    async def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        """Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
        """
        async with self._lock:
            ttl = ttl or self.default_ttl

            # Remove oldest entries if we're at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                await self._evict_lru()

            entry = CacheEntry(key, value, ttl)
            self._cache[key] = entry

            logger.debug(f"Cached entry {key} with TTL {ttl}s")

    async def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._cache:
            return

        # Find the entry with the oldest last_accessed time
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
        del self._cache[lru_key]
        self._stats["evictions"] += 1

        logger.debug(f"Evicted LRU cache entry {lru_key}")

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            cleared_count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared {cleared_count} cache entries")

    async def cleanup_expired(self) -> int:
        """Remove expired entries from the cache.

        Returns:
            Number of entries removed
        """
        async with self._lock:
            expired_keys = [key for key, entry in self._cache.items() if entry.is_expired()]

            for key in expired_keys:
                del self._cache[key]
                self._stats["expired_removals"] += 1

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

            return len(expired_keys)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate_percent": hit_rate,
            "total_requests": total_requests,
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "evictions": self._stats["evictions"],
            "expired_removals": self._stats["expired_removals"],
            "entries": [
                {
                    "key": entry.key,
                    "age_seconds": entry.age_seconds(),
                    "hit_count": entry.hit_count,
                    "ttl_seconds": entry.ttl_seconds,
                }
                for entry in list(self._cache.values())[:10]  # Show first 10 entries
            ],
        }


class CachedFunction:
    """Wrapper for functions with caching."""

    def __init__(self, func: Callable[..., Awaitable[T]], cache: Cache, ttl: float | None = None, key_prefix: str = ""):
        """Initialize cached function.

        Args:
            func: Function to cache
            cache: Cache instance to use
            ttl: TTL for cached results
            key_prefix: Prefix for cache keys
        """
        self.func = func
        self.cache = cache
        self.ttl = ttl
        self.key_prefix = key_prefix

    def __get__(self, instance: Any, owner: type) -> Callable[..., Awaitable[T]]:
        """Descriptor protocol to handle method access.

        This ensures that when a cached method is accessed on an instance,
        it's properly bound with the instance as the first argument.
        """
        if instance is None:
            return self

        import functools

        return functools.partial(self.__call__, instance)

    async def __call__(self, *args: Any, **kwargs: Any) -> T:
        """Call the function with caching.

        Args:
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result (from cache or fresh call)
        """
        # Generate cache key
        key = f"{self.key_prefix}_{self.cache._generate_key(*args, **kwargs)}"

        # Try to get from cache
        cached_result = await self.cache.get(key)
        if cached_result is not None:
            logger.debug(f"Cache hit for {self.func.__name__}")
            return cached_result

        # Call function and cache result
        logger.debug(f"Cache miss for {self.func.__name__}, calling function")
        result = await self.func(*args, **kwargs)
        await self.cache.set(key, result, self.ttl)

        return result


def cached(
    cache: Cache | None = None, ttl: float | None = None, key_prefix: str = ""
) -> Callable[[Callable[..., Awaitable[T]]], CachedFunction]:
    """Decorator to add caching to async functions.

    Args:
        cache: Cache instance (uses global cache if None)
        ttl: TTL for cached results
        key_prefix: Prefix for cache keys

    Returns:
        Decorated function with caching

    Example:
        ```python
        @cached(ttl=600, key_prefix="api")
        async def fetch_data(url: str) -> dict:
            # This will be cached for 10 minutes
            return await make_api_request(url)
        ```
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> CachedFunction:
        cache_instance = cache or get_global_cache()
        return CachedFunction(func, cache_instance, ttl, key_prefix or func.__name__)

    return decorator


# Global cache instances
_global_cache: Cache | None = None
_api_cache: Cache | None = None
_scraping_cache: Cache | None = None


def get_global_cache() -> Cache:
    """Get or create the global cache instance.

    Returns:
        The global cache instance
    """
    global _global_cache

    if _global_cache is None:
        _global_cache = Cache()
        logger.info("Initialized global cache")

    return _global_cache


def get_api_cache() -> Cache:
    """Get or create the API cache instance.

    Returns:
        The API cache instance with longer TTL
    """
    global _api_cache

    if _api_cache is None:
        _api_cache = Cache(default_ttl=API_CACHE_TTL_SECONDS)
        logger.info("Initialized API cache")

    return _api_cache


def get_scraping_cache() -> Cache:
    """Get or create the scraping cache instance.

    Returns:
        The scraping cache instance with longer TTL
    """
    global _scraping_cache

    if _scraping_cache is None:
        _scraping_cache = Cache(default_ttl=SCRAPING_CACHE_TTL_SECONDS)
        logger.info("Initialized scraping cache")

    return _scraping_cache


async def cleanup_all_caches() -> dict[str, int]:
    """Clean up expired entries in all caches.

    Returns:
        Dictionary with cleanup results
    """
    results = {}

    if _global_cache:
        results["global"] = await _global_cache.cleanup_expired()

    if _api_cache:
        results["api"] = await _api_cache.cleanup_expired()

    if _scraping_cache:
        results["scraping"] = await _scraping_cache.cleanup_expired()

    total_cleaned = sum(results.values())
    if total_cleaned > 0:
        logger.info(f"Cleaned up {total_cleaned} expired cache entries across all caches")

    return results


async def get_all_cache_stats() -> dict[str, dict[str, Any]]:
    """Get statistics for all cache instances.

    Returns:
        Dictionary with stats for each cache
    """
    stats = {}

    if _global_cache:
        stats["global"] = _global_cache.get_stats()

    if _api_cache:
        stats["api"] = _api_cache.get_stats()

    if _scraping_cache:
        stats["scraping"] = _scraping_cache.get_stats()

    # Log cache performance metrics
    for cache_name, cache_stats in stats.items():
        log_performance_metric(
            f"cache_hit_rate_{cache_name}",
            cache_stats["hit_rate_percent"],
            "percent",
            {
                "cache_size": cache_stats["size"],
                "total_requests": cache_stats["total_requests"],
            },
        )

    return stats


async def start_cache_cleanup_task() -> asyncio.Task[None]:
    """Start background task to clean up expired cache entries.

    Returns:
        The cleanup task
    """

    async def cleanup_loop() -> None:
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(CACHE_CLEANUP_INTERVAL)
                await cleanup_all_caches()
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")

    task = asyncio.create_task(cleanup_loop())
    logger.info(f"Started cache cleanup task (interval: {CACHE_CLEANUP_INTERVAL}s)")
    return task
