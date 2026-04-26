import redis.asyncio as redis
from core.config import settings

# Global Redis client instance
redis_client: redis.Redis | None = None

async def init_redis():
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.ping()
    print("INFO: Connected to Redis successfully.")

async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        print("INFO: Redis connection closed.")

def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized")
    return redis_client