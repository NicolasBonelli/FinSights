"""
Redis client configuration and management
"""
import logging
import aioredis
from typing import Optional
from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
class RedisClient:
    """Redis client wrapper with connection management"""
    
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None
        self._settings = get_settings()
    
    async def connect(self):
        """Establish Redis connection"""
        try:
            self._client = await aioredis.from_url(
                settings.redis_url,  
                decode_responses=True,
                encoding="utf-8"
            )
            
            # Test connection
            await self._client.ping()
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    async def close(self):
        """Close Redis connection"""
        if self._client:
            try:
                await self._client.close()
                self._client = None
                logger.info("🛑 Redis connection closed")
            except Exception as e:
                logger.error(f"❌ Error closing Redis connection: {e}")
    
    @property
    def client(self) -> Optional[aioredis.Redis]:
        """Get Redis client instance"""
        return self._client
    
    async def ping(self) -> bool:
        """Test Redis connection"""
        if not self._client:
            return False
        try:
            await self._client.ping()
            return True
        except Exception:
            return False
    
    async def set(self, key: str, value: str, expire: Optional[int] = None):
        """Set key-value pair with optional expiration"""
        if not self._client:
            raise ConnectionError("Redis client not connected")
        await self._client.set(key, value, ex=expire)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        if not self._client:
            raise ConnectionError("Redis client not connected")
        return await self._client.get(key)
    
    async def delete(self, key: str):
        """Delete key"""
        if not self._client:
            raise ConnectionError("Redis client not connected")
        await self._client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self._client:
            return False
        return await self._client.exists(key)

# Global instance
redis_client = RedisClient()

# Convenience functions
async def get_redis_client() -> RedisClient:
    """Get Redis client instance"""
    return redis_client

async def connect_redis():
    """Connect to Redis"""
    await redis_client.connect()

async def close_redis():
    """Close Redis connection"""
    await redis_client.close()