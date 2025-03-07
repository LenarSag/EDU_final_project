import json
from typing import Optional
from uuid import UUID

from redis import Redis

from project_root.infrastructure.schemas.user import UserOut


async def get_user_by_id_from_cache(redis, id: UUID) -> Optional[UserOut]:
    user = await redis.get(f'user:{id}')
    if user:
        return UserOut(**json.loads(user))
    return None


async def set_user_to_redis(redis: Redis, user: UserOut) -> None:
    await redis.set(f'user:{user.id}', user.model_dump_json(), ex=3600)
