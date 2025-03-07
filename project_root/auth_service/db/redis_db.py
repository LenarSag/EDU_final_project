from redis.asyncio import from_url, Redis

from project_root.config.config import settings


async def get_redis() -> Redis:
    redis = await from_url(settings.redis_test, encoding='utf-8', decode_responses=True)
    return redis
