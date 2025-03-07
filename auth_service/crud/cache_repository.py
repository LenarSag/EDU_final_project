import json
from typing import Optional

from redis import Redis


async def get_key_from_cache(key_name: str, key_id: str, redis: Redis):
    key = await redis.get(f'{key_name}:{key_id}')
    if key:
        return key
    return None


async def set_key_to_cache(key_name: str, key_id: str, json_data, redis: Redis) -> None:
    await redis.set(f'{key_name}:{key_id}', json_data, ex=3600)
