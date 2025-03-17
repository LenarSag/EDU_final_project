from typing import Annotated

from fastapi import Depends, APIRouter, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.config import settings
from config.constants import SERVICE_SECRET_KEY_HEADER
from auth_service.crud.sql_repository import (
    create_new_user,
    get_user_by_email,
)
from infrastructure.db.sql_db import get_session
from infrastructure.exceptions.auth_exceptions import (
    EmailAlreadyExistsException,
    IncorrectEmailOrPasswordException,
    InvalidServiceSecretKeyException,
)
from infrastructure.schemas.token import Token
from infrastructure.schemas.user import (
    UserAuthentication,
    UserCreate,
    UserBase,
)
from auth_service.security.authentication import (
    authenticate_user,
    create_access_token_for_user,
    create_internal_access_token,
)
from auth_service.security.pwd_crypt import get_hashed_password


login_router = APIRouter()


@login_router.post(
    '/user', response_model=UserBase, status_code=status.HTTP_201_CREATED
)
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


@login_router.post('/token_user', response_model=Token)
async def user_login_for_access_token(
    form_data: UserAuthentication,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await authenticate_user(session, form_data.email, form_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    access_token = create_access_token_for_user(user)
    return Token(access_token=access_token, token_type='Bearer')


@login_router.post('/token_service', response_model=Token)
async def service_login_for_access_token(
    request: Request,
):
    authorization_header = request.headers.get(SERVICE_SECRET_KEY_HEADER)
    print(authorization_header)
    if (
        not authorization_header
        or authorization_header != settings.SERVICES_COMMON_SECRET_KEY
    ):
        raise InvalidServiceSecretKeyException

    access_token = create_internal_access_token()
    return Token(access_token=access_token, token_type='Bearer')
