from datetime import date, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Request, status
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.crud.cache_repository import (
    delete_key_from_cache,
    set_key_to_cache,
)
from auth_service.crud.sql_repository import (
    delete_user_by_object,
    fire_user_db,
    get_user_by_email,
    get_user_by_id,
    get_user_full_info_by_id,
    rehire_user_db,
    update_user_data,
)
from infrastructure.db.redis_db import get_redis
from auth_service.exceptions.exceptions import (
    AlreadyFiredException,
    EmailAlreadyExistsException,
    NotAllowedToDeleteException,
    NotAllowedToFireException,
    NotAllowedToRehireException,
    NotFiredToRehireException,
    NotFoundException,
    UserNotFoundException,
)
from config.constants import DAYS_TILL_DELETE, USER_REDIS_KEY
from infrastructure.models.user import UserPosition, UserStatus
from permissions.rbac import require_position_authentication, require_authentication
from infrastructure.schemas.user import (
    UserEditManager,
    UserMinimal,
    UserEditSelf,
    UserFull,
)
from infrastructure.db.sql_db import get_session


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


@user_router.post('/rehire/{user_id}', response_model=UserMinimal)
@require_position_authentication(
    [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER], editing=True
)
async def rehire_user(
    user_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    user_to_rehire = await get_user_by_id(session, user_id)
    if user_to_rehire is None:
        raise NotFoundException
    if user_to_rehire.fired_at is None:
        raise NotFiredToRehireException
    if user_to_rehire.fired_at + timedelta(days=DAYS_TILL_DELETE) < date.today():
        raise NotAllowedToRehireException

    user_to_rehire = await rehire_user_db(session, user_to_rehire)
    user_pydantic = UserMinimal.model_validate(user_to_rehire)
    await set_key_to_cache(
        USER_REDIS_KEY,
        str(user_id),
        user_pydantic.model_dump_json(),
        redis,
    )

    return user_pydantic


@user_router.post('/fire/{user_id}', response_model=UserMinimal)
@require_position_authentication(
    [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER], editing=True
)
async def fire_user(
    user_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    user_to_fire = await get_user_by_id(session, user_id)
    if user_to_fire is None:
        raise NotFoundException
    if user_to_fire.status == UserStatus.FIRED:
        raise AlreadyFiredException
    if user_to_fire.position in [UserPosition.ADMIN, UserPosition.CEO]:
        raise NotAllowedToFireException

    user_to_fire = await fire_user_db(session, user_to_fire)
    user_pydantic = UserMinimal.model_validate(user_to_fire)
    await set_key_to_cache(
        USER_REDIS_KEY,
        str(user_id),
        user_pydantic.model_dump_json(),
        redis,
    )

    return user_pydantic


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
    if user is None:
        raise NotFoundException
    return user


@user_router.patch('/{user_id}', response_model=UserMinimal)
@require_position_authentication(
    [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER], editing=True
)
async def edit_user_info(
    user_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    new_user_data: UserEditManager,
):
    if new_user_data.email:
        email_owner = await get_user_by_email(session, new_user_data.email)
        if email_owner:
            if email_owner.id != user_id:
                raise EmailAlreadyExistsException

    edited_user = await update_user_data(session, user_id, new_user_data)
    if edited_user is None:
        raise UserNotFoundException

    await set_key_to_cache(
        USER_REDIS_KEY,
        str(edited_user.id),
        UserMinimal.model_validate(edited_user).model_dump_json(),
        redis,
    )

    return edited_user


@user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
@require_position_authentication([UserPosition.ADMIN, UserPosition.CEO], editing=True)
async def delete_user(
    user_id: UUID,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
):
    user_to_delete = await get_user_by_id(session, user_id)
    if not user_to_delete:
        raise NotFoundException
    if user_to_delete.fired_at is None:
        raise NotAllowedToDeleteException
    if user_to_delete.fired_at + timedelta(days=DAYS_TILL_DELETE) > date.today():
        raise NotAllowedToDeleteException

    await delete_user_by_object(session, user_to_delete)
    await delete_key_from_cache(USER_REDIS_KEY, str(user_id), redis)
