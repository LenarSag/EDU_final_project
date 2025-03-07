from datetime import datetime, timedelta
from typing import Optional

import jwt
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from infrastructure.models.user import User
from auth_service.crud.sql_repository import get_user_by_email
from security.pwd_crypt import verify_password


async def authenticate_user(
    session: AsyncSession, email: EmailStr, password: str
) -> Optional[User]:
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token_for_user(user: User) -> str:
    to_encode = {'sub': str(user.id)}
    expire = datetime.now() + timedelta(
        minutes=settings.USER_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.USER_JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_internal_access_token() -> str:
    to_encode = {'sub': settings.SERVICES_COMMON_SECRET_KEY}
    expire = datetime.now() + timedelta(
        minutes=settings.SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SERVICE_JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
