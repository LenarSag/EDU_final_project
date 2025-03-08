from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.user import User
from infrastructure.schemas.user import UserCreate


async def get_user_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_user_by_email(session: AsyncSession, email: EmailStr) -> Optional[User]:
    query = select(User).filter_by(email=email)
    result = await session.execute(query)
    return result.scalar()


async def create_new_user(session: AsyncSession, user_data: UserCreate) -> User:
    new_user = User(**user_data.model_dump())
    session.add(new_user)
    await session.commit()
    return new_user


async def get_user_full_info_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = (
        select(User)
        .filter_by(id=id)
        .options(
            selectinload(User.team),
            selectinload(User.my_team_lead),
        )
    )
    result = await session.execute(query)
    return result.scalars().first()
