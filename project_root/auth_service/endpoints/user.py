from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from project_root.auth_service.security.identification import identificate_user
from project_root.infrastructure.schemas.user import UserOut
from project_root.auth_service.db.sql_db import get_session


user_router = APIRouter()


@user_router.get('/me', response_model=UserOut)
async def create_user(
    current_user: Annotated[UserOut, Depends(identificate_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    return current_user
