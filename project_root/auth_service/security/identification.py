from datetime import datetime, timezone
import logging
import uuid
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, Request
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from project_root.config.config import settings
from project_root.auth_service.db.redis_db import get_redis
from project_root.auth_service.db.sql_db import get_session
from project_root.auth_service.exceptions.exceptions import (
    InvalidTokenException,
    TokenExpiredException,
    TokenNotFoundException,
    UserNotFoundException,
)
from project_root.auth_service.crud.cache_repository import (
    get_user_by_id_from_cache,
    set_user_to_redis,
)
from project_root.auth_service.crud.user_repository import get_user_by_id
from project_root.infrastructure.schemas.user import UserOut


async def identificate_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    inner_request: bool = True,
    outer_header: Optional[str] = None,
) -> Optional[UserOut]:
    if inner_request:
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            raise TokenNotFoundException
    else:
        authorization_header = outer_header

    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except InvalidTokenError:
        raise InvalidTokenException
    except IndexError:
        raise TokenNotFoundException

    expire = payload.get('exp')
    if not expire:
        raise InvalidTokenException
    try:
        expiring_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    except ValueError:
        raise InvalidTokenError
    if expiring_time < datetime.now(timezone.utc):
        raise TokenExpiredException

    user_id = uuid.UUID(payload.get('sub'))
    if user_id is None:
        raise InvalidTokenException

    cached_user = await get_user_by_id_from_cache(redis, user_id)
    if cached_user:
        return cached_user

    user = await get_user_by_id(session, user_id)
    if user is None:
        raise UserNotFoundException

    user_pydantic = UserOut.model_validate(user)

    await set_user_to_redis(redis, user_pydantic)

    return user_pydantic
