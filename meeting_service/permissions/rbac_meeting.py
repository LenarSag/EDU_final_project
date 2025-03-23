from functools import wraps
from typing import Optional

from fastapi import BackgroundTasks, Depends, Request
from fastapi_pagination import Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.schemas.meeting import MeetingCreate, MeetingEdit
from infrastructure.schemas.user import UserMinimal
from meeting_service.security.identification import identify_user
from infrastructure.db.redis_db import get_redis
from infrastructure.db.sql_db import get_session
from infrastructure.exceptions.auth_exceptions import NotEnoughRightsException
from config.constants import USER_AUTH_HEADER
from infrastructure.models.user import UserStatus


async def get_current_user(request: Request, session: AsyncSession, redis: Redis):
    user_authorization_header = request.headers.get(USER_AUTH_HEADER)
    if not user_authorization_header:
        raise NotEnoughRightsException
    current_user = await identify_user(user_authorization_header, session, redis)
    if current_user.status != UserStatus.ACTIVE:
        raise NotEnoughRightsException
    return current_user


def require_position_authentication(position: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            request: Request,
            background_tasks=BackgroundTasks,
            session: AsyncSession = Depends(get_session),
            redis: Redis = Depends(get_redis),
            new_meeting_data: Optional[MeetingCreate] = None,
            current_user: Optional[UserMinimal] = None,
        ):
            current_user = await get_current_user(request, session, redis)
            if position and current_user.position not in position:
                raise NotEnoughRightsException

            args_list = [request, background_tasks, session, redis]
            if new_meeting_data is not None:
                args_list.append(new_meeting_data)
            args_list.append(current_user)

            return await func(*args_list)

        return wrapper

    return decorator


def require_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        params: Optional[Params] = None,
        current_user: Optional[UserMinimal] = None,
    ):
        current_user = await get_current_user(request, session, redis)

        args_list = [request, session, redis]
        if params is not None:
            args_list.append(params)
        if current_user is not None:
            args_list.append(current_user)

        return await func(*args_list)

    return wrapper


def require_user_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        background_tasks=BackgroundTasks,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        meeting_id: Optional[int] = None,
        new_meeting_data: Optional[MeetingEdit] = None,
        current_user: Optional[UserMinimal] = None,
    ):
        current_user = await get_current_user(request, session, redis)

        args_list = [request, background_tasks, session, redis]
        if meeting_id is not None:
            args_list.append(meeting_id)
        if new_meeting_data is not None:
            args_list.append(new_meeting_data)
        if current_user is not None:
            args_list.append(current_user)

        return await func(*args_list)

    return wrapper
