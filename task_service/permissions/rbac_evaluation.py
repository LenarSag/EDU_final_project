from functools import wraps
from typing import Optional

from fastapi import Depends, Path, Request
from fastapi_pagination import Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.schemas.evaluation import TaskEvaluationCreate
from task_service.security.identification import identify_user
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


def require_user_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        task_id: int = Path(..., description='The id of the task'),
        new_task_eval_data: Optional[TaskEvaluationCreate] = None,
        current_user: Optional[Params] = None,
    ):
        current_user = await get_current_user(request, session, redis)

        args_list = [request, session, redis, task_id]
        if new_task_eval_data is not None:
            args_list.append(new_task_eval_data)
        if current_user is not None:
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
        current_user: Optional[Params] = None,
    ):
        current_user = await get_current_user(request, session, redis)

        args_list = [request, session, redis, params]

        if current_user is not None:
            args_list.append(current_user)

        return await func(*args_list)

    return wrapper
