from redis.asyncio import from_url, Redis

from config.config import settings


# async def get_redis() -> Redis:
#     print('redis starts')
#     redis = await from_url(settings.redis_test, encoding='utf-8', decode_responses=True)
#     return redis


async def get_redis() -> Redis:
    print('redis starts')
    redis = await from_url(settings.redis_url, encoding='utf-8', decode_responses=True)
    return redis
