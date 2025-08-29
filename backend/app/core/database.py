"""
Redis database connection and utilities
"""
import logging
from typing import Optional
import redis.asyncio as redis
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Global Redis client instance
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        settings = get_settings()
        redis_client = redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            decode_responses=True,
            encoding="utf-8"
        )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


# Initialize client on import
redis_client = None


async def ping_redis() -> bool:
    """Check Redis connectivity"""
    try:
        client = await get_redis_client()
        await client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis ping failed: {e}")
        return False


class RedisService:
    """Redis service for document metadata and caching"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def get_client(self) -> redis.Redis:
        """Get Redis client"""
        if self.client is None:
            self.client = await get_redis_client()
        return self.client
    
    async def set_document_metadata(self, document_id: str, metadata: dict, expire_seconds: int = 3600) -> bool:
        """Store document metadata"""
        try:
            client = await self.get_client()
            key = f"doc_metadata:{document_id}"
            await client.hset(key, mapping=metadata)
            await client.expire(key, expire_seconds)
            return True
        except Exception as e:
            logger.error(f"Error storing document metadata: {e}")
            return False
    
    async def get_document_metadata(self, document_id: str) -> Optional[dict]:
        """Retrieve document metadata"""
        try:
            client = await self.get_client()
            key = f"doc_metadata:{document_id}"
            metadata = await client.hgetall(key)
            return dict(metadata) if metadata else None
        except Exception as e:
            logger.error(f"Error retrieving document metadata: {e}")
            return None
    
    async def cache_agent_result(self, task_id: str, result: str, expire_seconds: int = 1800) -> bool:
        """Cache agent execution result"""
        try:
            client = await self.get_client()
            key = f"agent_result:{task_id}"
            await client.set(key, result, ex=expire_seconds)
            return True
        except Exception as e:
            logger.error(f"Error caching agent result: {e}")
            return False
    
    async def get_cached_agent_result(self, task_id: str) -> Optional[str]:
        """Get cached agent result"""
        try:
            client = await self.get_client()
            key = f"agent_result:{task_id}"
            result = await client.get(key)
            return result
        except Exception as e:
            logger.error(f"Error retrieving cached agent result: {e}")
            return None


# Global service instance
redis_service = RedisService()
