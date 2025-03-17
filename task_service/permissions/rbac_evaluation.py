from functools import wraps

from fastapi import Depends, Path, Request
from fastapi_pagination import Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from task_service.security.identification import identificate_user
from infrastructure.db.redis_db import get_redis
from infrastructure.db.sql_db import get_session
from infrastructure.exceptions.auth_exceptions import NotEnoughRightsException
from config.constants import USER_AUTH_HEADER
from infrastructure.models.user import UserStatus


def require_user_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        task_id: int = Path(..., review='The id of the task'),
        new_task_eval_data=None,
        current_user=None,
    ):
        user_authorization_header = request.headers.get(USER_AUTH_HEADER)

        if not user_authorization_header:
            raise NotEnoughRightsException
        current_user = await identificate_user(
            user_authorization_header, session, redis
        )
        if current_user.status != UserStatus.ACTIVE:
            raise NotEnoughRightsException

        args_list = [request, session, redis, task_id]
        if new_task_eval_data:
            args_list.append(new_task_eval_data)
        if current_user:
            args_list.append(current_user)

        return await func(*args_list)

    return wrapper


def require_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        params: Params = Depends(),
        current_user=None,
    ):
        user_authorization_header = request.headers.get(USER_AUTH_HEADER)

        if not user_authorization_header:
            raise NotEnoughRightsException
        current_user = await identificate_user(
            user_authorization_header, session, redis
        )
        if current_user.status != UserStatus.ACTIVE:
            raise NotEnoughRightsException

        args_list = [request, session, redis, params]

        if current_user:
            args_list.append(current_user)

        return await func(*args_list)

    return wrapper
