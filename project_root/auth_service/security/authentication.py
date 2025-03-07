from datetime import datetime, timedelta
from typing import Optional

import jwt
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession


from project_root.config.config import settings
from project_root.infrastructure.models.user import User
from project_root.auth_service.crud.user_repository import get_user_by_email


from project_root.auth_service.security.pwd_crypt import verify_password


async def authenticate_user(
    session: AsyncSession, email: EmailStr, password: str
) -> Optional[User]:
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(user: User) -> str:
    to_encode = {'sub': str(user.id)}
    expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
