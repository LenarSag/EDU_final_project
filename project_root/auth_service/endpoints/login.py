from typing import Annotated

from fastapi import Depends, APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession

from project_root.auth_service.crud.user_repository import (
    create_new_user,
    get_user_by_email,
)
from project_root.auth_service.db.sql_db import get_session
from project_root.auth_service.exceptions.exceptions import (
    EmailAlreadyExistsException,
    IncorrectEmailOrPasswordException,
)
from project_root.infrastructure.schemas.token import Token
from project_root.infrastructure.schemas.user import (
    UserAuthentication,
    UserCreate,
    UserOut,
)
from project_root.auth_service.security.authentication import (
    authenticate_user,
    create_access_token,
)
from project_root.auth_service.security.pwd_crypt import get_hashed_password


login_router = APIRouter()


@login_router.post('/user', response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await get_user_by_email(session, user_data.email)
    if user:
        raise EmailAlreadyExistsException

    user_data.password = get_hashed_password(user_data.password)
    new_user = await create_new_user(session, user_data)
    return new_user


@login_router.post('/token', response_model=Token)
async def login_for_access_token(
    form_data: UserAuthentication,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await authenticate_user(session, form_data.email, form_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    access_token = create_access_token(user)
    return Token(access_token=access_token, token_type='Bearer')
