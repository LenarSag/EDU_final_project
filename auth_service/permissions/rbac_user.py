from functools import wraps
from uuid import UUID

from fastapi import Depends, Request
from fastapi_pagination import Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.security.identification import identificate_service, identificate_user
from infrastructure.db.redis_db import get_redis
from infrastructure.db.sql_db import get_session
from infrastructure.exceptions.auth_exceptions import NotEnoughRightsException
from config.constants import SERVICE_AUTH_HEADER, USER_AUTH_HEADER
from infrastructure.models.user import UserStatus


def require_position_authentication(positions: list):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            user_id: UUID,
            request: Request,
            session: AsyncSession = Depends(get_session),
            redis: Redis = Depends(get_redis),
            new_user_data=None,
        ):
            user_authorization_header = request.headers.get(USER_AUTH_HEADER)
            service_authorization_header = request.headers.get(SERVICE_AUTH_HEADER)

            if user_authorization_header:
                current_user = await identificate_user(
                    user_authorization_header, session, redis
                )

                if current_user.status != UserStatus.ACTIVE:
                    raise NotEnoughRightsException
                if positions and current_user.position not in positions:
                    raise NotEnoughRightsException

            elif service_authorization_header:
                permission = identificate_service(service_authorization_header)
                if not permission:
                    raise NotEnoughRightsException
            else:
                raise NotEnoughRightsException

            args_list = [user_id, request, session, redis]
            if new_user_data:
                args_list.append(new_user_data)
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
        user_id=None,
    ):
        user_authorization_header = request.headers.get(USER_AUTH_HEADER)
        service_authorization_header = request.headers.get(SERVICE_AUTH_HEADER)

        if user_authorization_header:
            await identificate_user(user_authorization_header, session, redis)

        elif service_authorization_header:
            permission = identificate_service(service_authorization_header)
            if not permission:
                raise NotEnoughRightsException

        else:
            raise NotEnoughRightsException

        args_list = [request, session, redis]

        if params:
            args_list.append(params)
        if user_id:
            args_list.append(user_id)

        return await func(*args_list)

    return wrapper


def require_user_authentication(func):
    @wraps(func)
    async def wrapper(
        request: Request,
        session: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        new_user_data=None,
        current_user=None,
    ):
        user_authorization_header = request.headers.get(USER_AUTH_HEADER)
        if not user_authorization_header:
            raise NotEnoughRightsException

        current_user = await identificate_user(
            user_authorization_header, session, redis
        )

        args_list = [request, session, redis]

        if new_user_data:
            args_list.append(new_user_data)
        args_list.append(current_user)

        return await func(*args_list)

    return wrapper
