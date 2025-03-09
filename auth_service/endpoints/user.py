from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, APIRouter, Request, Body

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.crud.cache_repository import (
    delete_key_from_cache,
    get_key_from_cache,
    set_key_to_cache,
)
from auth_service.crud.sql_repository import (
    get_team,
    get_user_by_id,
    get_user_full_info_by_id,
    update_user_data,
)
from auth_service.db.redis_db import get_redis
from auth_service.exceptions.exceptions import NotEnoughRights, UserNotFoundException
from config.constants import (
    SERVICE_AUTH_HEADER,
    USER_AUTH_HEADER,
    USER_REDIS_KEY,
)
from infrastructure.models.user import UserPosition
from infrastructure.schemas.team import TeamFull
from permissions.rbac import require_position_authentication, require_authentication
from security.identification import (
    identificate_service,
    identificate_user,
    identify_user_and_check_role,
)
from infrastructure.schemas.user import (
    UserEditManager,
    UserMinimal,
    UserEditSelf,
    UserFull,
)
from db.sql_db import get_session


user_router = APIRouter()


@user_router.get('/me', response_model=UserMinimal)
@require_authentication
async def get_myself(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    current_user=None,
):
    return current_user


@user_router.patch('/me', response_model=UserMinimal)
@require_authentication
async def edit_myself(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    new_user_data: UserEditSelf,
    current_user=None,
):
    updated_user = await update_user_data(
        session,
        current_user.id,
        new_user_data,
    )
    str_user_id = str(current_user.id)

    await set_key_to_cache(
        USER_REDIS_KEY,
        str_user_id,
        UserMinimal.model_validate(updated_user).model_dump_json(),
        redis,
    )

    return updated_user


@user_router.get('/{user_id}', response_model=UserFull)
@require_position_authentication(
    [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER]
)
async def get_user_full_info(
    user_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    user = await get_user_full_info_by_id(session, user_id)
    return user


@user_router.patch('/{user_id}', response_model=UserMinimal)
@require_position_authentication(
    [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER]
)
async def edit_user_info(
    user_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    new_user_data: UserEditManager,
):
    edited_user = await update_user_data(session, user_id, new_user_data)
    if edited_user is None:
        raise UserNotFoundException
    return edited_user


# @user_router.patch('/{user_id}', response_model=UserFull)
# async def edit_user_info(
#     user_id: UUID,
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
#     new_user_data: UserEditManager,
# ):
#     user_authorization_header = request.headers.get(USER_AUTH_HEADER)
#     service_authorization_header = request.headers.get(SERVICE_AUTH_HEADER)

#     if user_authorization_header:
#         permission = await identify_user_and_check_role(
#             user_id,
#             user_authorization_header,
#             [UserPosition.ADMIN, UserPosition.CEO],
#             session,
#             redis,
#         )
#     elif service_authorization_header:
#         permission = identificate_service(service_authorization_header)
#     else:
#         raise NotEnoughRights

#     if permission:
#         user_to_edit = await get_user_by_id(session, user_id)
#     raise NotEnoughRights


@user_router.delete('/{user_id}', response_model=UserFull)
async def delete_user(
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
            [UserPosition.ADMIN, UserPosition.CEO],
            session,
            redis,
        )
    elif service_authorization_header:
        permission = identificate_service(service_authorization_header)
    else:
        raise NotEnoughRights

    if permission:
        user_to_edit = await get_user_by_id(session, user_id)
    raise NotEnoughRights
