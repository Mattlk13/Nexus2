"""
Redis Caching Service for NEXUS
Provides 100x speed boost for frequently accessed data
"""
import logging
import json
from typing import Any, Optional, Callable, TypeVar
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RedisCacheService:
    """High-performance caching service using Redis"""
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.redis: Optional[redis.Redis] = None
        self.prefix = "nexus:"
    
    async def initialize(self):
        """Initialize Redis connection pool"""
        try:
            self.pool = redis.ConnectionPool(
                host="localhost",
                port=6379,
                db=0,
                max_connections=50,
                decode_responses=True,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True
            )
            self.redis = redis.Redis(connection_pool=self.pool)
            await self.redis.ping()
            logger.info("✓ Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis unavailable, caching disabled: {e}")
            self.redis = None
    
    async def close(self):
        """Close Redis connections"""
        if self.pool:
            await self.pool.disconnect()
    
    def _key(self, name: str) -> str:
        """Generate namespaced cache key"""
        return f"{self.prefix}{name}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        try:
            data = await self.redis.get(self._key(key))
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default 5 min)
        """
        if not self.redis:
            return False
        try:
            await self.redis.setex(
                self._key(key),
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis:
            return False
        try:
            await self.redis.delete(self._key(key))
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis:
            return 0
        try:
            keys = await self.redis.keys(self._key(pattern))
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error: {e}")
            return 0
    
    async def remember(
        self,
        key: str,
        ttl: int,
        callback: Callable[[], T]
    ) -> T:
        """
        Cache-aside pattern: get from cache or execute callback
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            callback: Function to call on cache miss
        """
        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Cache miss - execute callback
        if asyncio.iscoroutinefunction(callback):
            result = await callback()
        else:
            result = await asyncio.to_thread(callback)
        
        # Store in cache
        await self.set(key, result, ttl)
        return result
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        if not self.redis:
            return 0
        try:
            return await self.redis.incrby(self._key(key), amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return 0
    
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        if not self.redis:
            return {"status": "disabled"}
        try:
            info = await self.redis.info("stats")
            return {
                "status": "active",
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": round(
                    info.get("keyspace_hits", 0) / 
                    max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                    2
                )
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"status": "error", "error": str(e)}

# Create singleton instance
cache_service = RedisCacheService()

# Decorator for caching endpoint results
def cached(ttl: int = 300, key_prefix: str = "endpoint"):
    """
    Decorator to cache endpoint results
    
    Usage:
        @cached(ttl=600, key_prefix="products")
        async def get_products():
            return expensive_operation()
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and args
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try cache
            result = await cache_service.get(cache_key)
            if result is not None:
                return result
            
            # Cache miss - execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
