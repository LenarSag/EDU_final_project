from functools import wraps

from fastapi import Depends, Request
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.security.identification import identificate_user
from infrastructure.db.redis_db import get_redis
from infrastructure.db.sql_db import get_session
from infrastructure.exceptions.exceptions import NotEnoughRightsException
from config.constants import USER_AUTH_HEADER
from infrastructure.models.user import UserStatus


def require_position_authentication(position: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            request: Request,
            session: AsyncSession = Depends(get_session),
            redis: Redis = Depends(get_redis),
            team_id=None,
            new_team_data=None,
        ):
            user_authorization_header = request.headers.get(USER_AUTH_HEADER)

            if not user_authorization_header:
                raise NotEnoughRightsException

            current_user = await identificate_user(
                user_authorization_header, session, redis
            )

            if current_user.status != UserStatus.ACTIVE:
                raise NotEnoughRightsException
            if position and current_user.position not in position:
                raise NotEnoughRightsException

            args_list = [request, session, redis]
            if team_id:
                args_list.append(team_id)
            if new_team_data:
                args_list.append(new_team_data)

            return await func(*args_list)

        return wrapper

    return decorator


def require_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        params=None,
        task_id=None,
        role=None,
        current_user=None,
    ):
        user_authorization_header = request.headers.get(USER_AUTH_HEADER)

        if not user_authorization_header:
            raise NotEnoughRightsException
        current_user = await identificate_user(
            user_authorization_header, session, redis
        )

        args_list = [request, session, redis]
        if params:
            args_list.append(params)
        if task_id:
            args_list.append(task_id)
        args_list.append(role)
        if current_user:
            args_list.append(current_user)

        return await func(*args_list)

    return wrapper
