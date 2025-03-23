from functools import wraps
from tkinter import EventType
from typing import Optional

from fastapi import Depends, Request
from fastapi_pagination import Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from calendar_service.security.identification import identify_user
from infrastructure.db.redis_db import get_redis
from infrastructure.db.sql_db import get_session
from infrastructure.exceptions.auth_exceptions import NotEnoughRightsException
from config.constants import USER_AUTH_HEADER
from infrastructure.models.user import UserStatus
from infrastructure.schemas.user import UserMinimal


async def get_current_user(request: Request, session: AsyncSession, redis: Redis):
    user_authorization_header = request.headers.get(USER_AUTH_HEADER)
    if not user_authorization_header:
        raise NotEnoughRightsException
    current_user = await identify_user(user_authorization_header, session, redis)
    if current_user.status != UserStatus.ACTIVE:
        raise NotEnoughRightsException
    return current_user


def require_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        params: Optional[Params] = None,
        calendar_id: Optional[int] = None,
        current_user: Optional[UserMinimal] = None,
        event_type=Optional[EventType],
    ):
        current_user = await get_current_user(request, session, redis)

        args_list = [request, session, redis]
        if params is not None:
            args_list.append(params)
        if calendar_id is not None:
            args_list.append(calendar_id)
        if current_user is not None:
            args_list.append(current_user)
        if event_type is not None:
            args_list.append(event_type)

        return await func(*args_list)

    return wrapper
