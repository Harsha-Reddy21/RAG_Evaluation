import aioredis
import logging
import json
from typing import Optional, Any, Dict
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, CACHE_TTL_REALTIME, CACHE_TTL_HISTORICAL

# Configure logging
logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache manager for the financial RAG system"""
    
    def __init__(self):
        self.redis = None
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def connect(self):
        """Initialize Redis connection"""
        try:
            # Create Redis connection
            redis_url = f"redis://{':' + REDIS_PASSWORD + '@' if REDIS_PASSWORD else ''}{REDIS_HOST}:{REDIS_PORT}"
            self.redis = await aioredis.create_redis_pool(redis_url)
            logger.info(f"Redis connection established to {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.redis:
            await self.connect()
        
        try:
            value = await self.redis.get(key)
            if value:
                self.cache_hits += 1
                return value.decode('utf-8')
            else:
                self.cache_misses += 1
                return None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            self.cache_misses += 1
            return None
    
    async def set(self, key: str, value: str, is_real_time: bool = True):
        """Set value in cache with appropriate TTL"""
        if not self.redis:
            await self.connect()
        
        try:
            # Use different TTL based on whether data is real-time or historical
            ttl = CACHE_TTL_REALTIME if is_real_time else CACHE_TTL_HISTORICAL
            await self.redis.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_ratio = self.cache_hits / total_requests if total_requests > 0 else 0
        
        # Get cache size (number of keys)
        cache_size = 0
        if self.redis:
            try:
                cache_size = await self.redis.dbsize()
            except Exception as e:
                logger.error(f"Redis dbsize error: {str(e)}")
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio": hit_ratio,
            "cache_size": cache_size
        }
    
    def get_cache_key(self, company: str, question: str) -> str:
        """Generate a cache key for a financial query"""
        # Normalize the question to improve cache hit ratio
        normalized_question = question.lower().strip()
        return f"financial_rag:{company}:{normalized_question}"

# Create a cache instance
cache = RedisCache() 