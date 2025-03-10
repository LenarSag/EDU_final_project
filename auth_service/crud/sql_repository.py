from datetime import date
from typing import Optional, Union
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.team import Team
from infrastructure.models.user import User, UserStatus
from infrastructure.schemas.user import (
    UserCreate,
    UserEditManager,
    UserEditSelf,
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
            selectinload(User.user_team_lead),
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
    if update_data.get('position') == UserStatus.FIRED:
        update_data['fired_at'] = date.today()

    stmt = update(User).where(User.id == user_id).values(**update_data)
    await session.execute(stmt)
    await session.commit()

    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar()


async def rehire_user_db(session: AsyncSession, user_to_rehire: User) -> User:
    user_to_rehire.fired_at = None
    user_to_rehire.status = UserStatus.ACTIVE
    await session.commit()
    await session.refresh(user_to_rehire)
    return user_to_rehire


async def fire_user_db(session: AsyncSession, user_to_fire: User) -> User:
    user_to_fire.status = UserStatus.FIRED
    user_to_fire.fired_at = date.today()
    await session.commit()
    await session.refresh(user_to_fire)
    return user_to_fire


async def delete_user_by_id(session: AsyncSession, user_id: UUID) -> int:
    result = await session.execute(delete(User).where((User.id == user_id)))
    deleted_rows = result.rowcount
    await session.commit()
    return deleted_rows


async def get_team(session: AsyncSession):
    query = select(Team).options(joinedload(Team.members))
    result = await session.execute(query)
    return result.scalars().first()


async def delete_user_by_object(session: AsyncSession, user_to_delete: User) -> None:
    await session.delete(user_to_delete)
    await session.commit()
