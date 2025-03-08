from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Request

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.crud.cache_repository import get_key_from_cache, set_key_to_cache
from auth_service.crud.sql_repository import get_user_by_id, get_user_full_info_by_id
from auth_service.db.redis_db import get_redis
from auth_service.exceptions.exceptions import NotEnoughRights
from config.constants import SERVICE_AUTH_HEADER, USER_AUTH_HEADER, USERFULL_REDIS_KEY
from infrastructure.models.user import UserPosition
from security.identification import (
    identificate_service,
    identificate_user,
    identify_user_and_check_role,
)
from infrastructure.schemas.user import UserBase
from db.sql_db import get_session


user_router = APIRouter()


@user_router.get('/me', response_model=UserBase)
async def get_myself(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    user_authorization_header = request.headers.get(USER_AUTH_HEADER)
    if not user_authorization_header:
        raise NotEnoughRights
    current_user = await identificate_user(user_authorization_header, session, redis)

    return current_user


@user_router.get('/{user_id}')
async def get_user_full_info(
    user_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    str_user_id = str(user_id)
    user_authorization_header = request.headers.get(USER_AUTH_HEADER)
    service_authorization_header = request.headers.get(SERVICE_AUTH_HEADER)

    if user_authorization_header:
        permission = await identify_user_and_check_role(
            user_id,
            user_authorization_header,
            [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER],
            session,
            redis,
        )
    elif service_authorization_header:
        permission = identificate_service(service_authorization_header)
    else:
        raise NotEnoughRights

    if permission:
        cached_user = await get_key_from_cache(USERFULL_REDIS_KEY, str_user_id, redis)
        if cached_user:
            return UserBase.model_validate_json(cached_user)

        user = await get_user_full_info_by_id(session, user_id)

        json_user = UserBase.model_validate(user).model_dump_json()
        await set_key_to_cache(USERFULL_REDIS_KEY, str_user_id, json_user, redis)

        return user
    raise NotEnoughRights
