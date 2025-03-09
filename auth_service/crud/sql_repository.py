from typing import Optional, Union
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.team import Team
from infrastructure.models.user import User
from infrastructure.schemas.user import (
    UserCreate,
    UserEditManager,
    UserEditSelf,
    UserBase,
)


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
    return result.scalar()


async def update_user_data(
    session: AsyncSession,
    user_id: UUID,
    new_user_data: Union[UserEditSelf, UserEditManager],
) -> Optional[User]:
    update_data = {
        key: val for key, val in new_user_data.model_dump().items() if val is not None
    }
    stmt = update(User).where(User.id == user_id).values(**update_data)
    await session.execute(stmt)
    await session.commit()

    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar()


async def delete_user_from_db(session: AsyncSession, user_id: UUID) -> int:
    result = await session.execute(delete(User).where(User.id == user_id))
    deleted_rows = result.rowcount
    await session.commit()
    return deleted_rows


async def get_team(session: AsyncSession):
    query = select(Team).options(joinedload(Team.members))
    result = await session.execute(query)
    return result.scalars().first()
