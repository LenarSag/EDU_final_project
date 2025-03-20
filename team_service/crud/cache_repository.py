from redis import Redis


async def get_key_from_cache(key_name: str, key_id: str, redis: Redis):
    async with redis.client() as conn:
        key = await conn.get(f'{key_name}:{key_id}')
        if key:
            return key
        return None


async def set_key_to_cache(key_name: str, key_id: str, json_data, redis: Redis) -> None:
    async with redis.client() as conn:
        await conn.set(f'{key_name}:{key_id}', json_data, ex=10)


async def delete_key_from_cache(key_name: str, key_id: str, redis: Redis) -> None:
    async with redis.client() as conn:
        await conn.delete(
            f'{key_name}:{key_id}',
        )
