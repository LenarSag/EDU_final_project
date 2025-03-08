from datetime import datetime, timezone
import uuid
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.constants import USERMINIMAL_REDIS_KEY
from exceptions.exceptions import (
    InvalidTokenException,
    InvalidServiceSecretKey,
    NotEnoughRights,
    TokenExpiredException,
    TokenNotFoundException,
    UserNotFoundException,
)
from crud.cache_repository import (
    get_key_from_cache,
    set_key_to_cache,
)
from auth_service.crud.sql_repository import get_user_by_id
from infrastructure.models.user import UserPosition, UserStatus
from infrastructure.schemas.user import UserMinimal


def check_jwt(authorization_header: str, secret_key: str):
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(access_token, secret_key, algorithms=[settings.ALGORITHM])

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
    return payload


def identificate_service(
    authorization_header: str,
) -> bool:
    payload = check_jwt(authorization_header, settings.SERVICE_JWT_SECRET_KEY)

    services_secret_key = payload.get('sub')
    if (
        services_secret_key is None
        or services_secret_key != settings.SERVICES_COMMON_SECRET_KEY
    ):
        raise InvalidServiceSecretKey
    return True


async def identificate_user(
    authorization_header: str, session: AsyncSession, redis: Redis
) -> Optional[UserMinimal]:
    payload = check_jwt(authorization_header, settings.USER_JWT_SECRET_KEY)

    user_id = payload.get('sub')
    if user_id is None:
        raise InvalidTokenException

    cached_user = await get_key_from_cache(USERMINIMAL_REDIS_KEY, user_id, redis)
    if cached_user:
        return UserMinimal.model_validate_json(cached_user)

    user = await get_user_by_id(session, uuid.UUID(user_id))
    if user is None:
        raise UserNotFoundException

    user_pydantic = UserMinimal.model_validate(user)

    await set_key_to_cache(
        USERMINIMAL_REDIS_KEY, user_id, user_pydantic.model_dump_json(), redis
    )

    return user_pydantic


async def identify_user_and_check_role(
    user_id: uuid.UUID,
    user_authorization_header: str,
    roles: list[UserPosition],
    session: AsyncSession,
    redis: Redis,
) -> bool:
    user = await identificate_user(user_authorization_header, session, redis)

    if user.id != user_id:
        if user.position not in roles or user.status != UserStatus.ACTIVE:
            raise NotEnoughRights

    return True
