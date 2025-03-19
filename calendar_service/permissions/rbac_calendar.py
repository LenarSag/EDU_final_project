from functools import wraps

from fastapi import Depends, Request
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from meeting_service.security.identification import identificate_user
from infrastructure.db.redis_db import get_redis
from infrastructure.db.sql_db import get_session
from infrastructure.exceptions.auth_exceptions import NotEnoughRightsException
from config.constants import USER_AUTH_HEADER
from infrastructure.models.user import UserStatus


def require_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        params=None,
        calendar_id=None,
        current_user=None,
        event_type=None,
    ):
        user_authorization_header = request.headers.get(USER_AUTH_HEADER)

        if not user_authorization_header:
            raise NotEnoughRightsException
        current_user = await identificate_user(
            user_authorization_header, session, redis
        )
        if current_user.status != UserStatus.ACTIVE:
            raise NotEnoughRightsException

        args_list = [request, session, redis]
        if params:
            args_list.append(params)
        if calendar_id:
            args_list.append(calendar_id)
        if current_user:
            args_list.append(current_user)
        if event_type:
            args_list.append(event_type)

        return await func(*args_list)

    return wrapper
