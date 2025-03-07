from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Request

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.crud.cache_repository import get_key_from_cache, set_key_to_cache
from auth_service.crud.sql_repository import get_user_by_id
from auth_service.db.redis_db import get_redis
from auth_service.exceptions.exceptions import NotEnoughRights
from config.constants import SERVICE_AUTH_HEADER, USER_AUTH_HEADER
from infrastructure.models.user import UserPosition
from security.identification import (
    identificate_service,
    identificate_user,
    identify_user_and_check_role,
)
from infrastructure.schemas.user import UserOut
from db.sql_db import get_session


user_router = APIRouter()


@user_router.get('/te')
async def get_myself(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    current_user = await get_user_by_id(
        session, UUID('68fc3888e72f432c9d56a7634990b3c3')
    )
    return current_user


@user_router.get('/me', response_model=UserOut)
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


@user_router.get('/{user_id}', response_model=UserOut)
async def get_user(
    user_id: str,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    uuid_user_id = UUID(user_id)
    user_authorization_header = request.headers.get(USER_AUTH_HEADER)
    service_authorization_header = request.headers.get(SERVICE_AUTH_HEADER)

    if user_authorization_header:
        permission = await identify_user_and_check_role(
            uuid_user_id,
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
        cached_user = await get_key_from_cache('user', user_id, redis)
        if cached_user:
            return UserOut.model_validate_json(cached_user)

        user = await get_user_by_id(session, uuid_user_id)

        json_user = UserOut.model_validate(user).model_dump_json()
        await set_key_to_cache('user', user_id, json_user, redis)

        return user
    raise NotEnoughRights
