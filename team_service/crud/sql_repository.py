from datetime import date
from typing import Optional, Sequence, Union
from uuid import UUID

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import EmailStr
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.team import Team
from infrastructure.models.user import User
from infrastructure.schemas.team import TeamCreate


async def get_user_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_users_by_ids(session: AsyncSession, ids: list[UUID]) -> Sequence[User]:
    query = select(User).where(User.id.in_(ids))
    result = await session.execute(query)
    return result.scalars().all()


async def create_team(
    session: AsyncSession, team_data: TeamCreate, users: Sequence[User]
):
    new_team = Team(
        name=team_data.name,
        description=team_data.description,
        team_lead_id=team_data.team_lead_id,
    )
    session.add(new_team)
    await session.flush()
    await session.refresh(new_team, attribute_names=['members', 'team_lead'])

    new_team.members.extend(users)

    await session.commit()
    return new_team


async def get_all_teams_db(session: AsyncSession, params: Params) -> Sequence[Team]:
    query = select(Team)
    return await paginate(session, query, params)


async def get_team_full_info_by_id(session: AsyncSession, id: int):
    query = select(Team).filter_by(id=id).options(joinedload(Team.members))
    result = await session.execute(query)
    return result.scalar()


async def get_team_by_name(session: AsyncSession, name: str):
    query = select(Team).filter_by(name=name)
    result = await session.execute(query)
    return result.scalar()


async def get_team_by_team_lead_id(session: AsyncSession, team_lead_id: UUID):
    query = select(Team).filter_by(team_lead_id=team_lead_id)
    result = await session.execute(query)
    return result.scalar()
