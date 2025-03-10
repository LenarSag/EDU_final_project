from datetime import datetime, timezone
import uuid
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.constants import USER_REDIS_KEY
from exceptions.exceptions import (
    InvalidTokenException,
    InvalidServiceSecretKeyException,
    NotEnoughRightsException,
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


def check_jwt(authorization_header: str, secret_key: str) -> str:
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

    subject = payload.get('sub')
    if subject is None:
        raise InvalidTokenException

    return subject


def identificate_service(
    authorization_header: str,
) -> bool:
    services_secret_key = check_jwt(
        authorization_header, settings.SERVICE_JWT_SECRET_KEY
    )
    if services_secret_key != settings.SERVICES_COMMON_SECRET_KEY:
        raise InvalidServiceSecretKeyException
    return True


async def identificate_user(
    authorization_header: str, session: AsyncSession, redis: Redis
) -> Optional[UserMinimal]:
    user_id = check_jwt(authorization_header, settings.USER_JWT_SECRET_KEY)

    cached_user = await get_key_from_cache(USER_REDIS_KEY, user_id, redis)
    if cached_user:
        return UserMinimal.model_validate_json(cached_user)

    user = await get_user_by_id(session, uuid.UUID(user_id))
    if user is None:
        raise UserNotFoundException

    user_pydantic = UserMinimal.model_validate(user)

    await set_key_to_cache(
        USER_REDIS_KEY, user_id, user_pydantic.model_dump_json(), redis
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
    if user.status != UserStatus.ACTIVE:
        raise NotEnoughRightsException
    if user.id == user_id:
        return True
    if roles and user.position not in roles:
        raise NotEnoughRightsException

    return True
