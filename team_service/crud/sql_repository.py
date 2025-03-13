from typing import Optional, Sequence
from uuid import UUID

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.models.team import Team
from infrastructure.models.user import User
from infrastructure.schemas.team import TeamCreate, TeamEdit


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


async def update_team(
    session: AsyncSession,
    team_to_update: Team,
    new_team_data: TeamEdit,
    members: Sequence[User],
):
    new_team_data_dict = new_team_data.model_dump()
    new_team_data_dict.pop('members')
    for key, value in new_team_data_dict.items():
        if value:
            setattr(team_to_update, key, value)
    if members:
        team_to_update.members = members

    await session.commit()
    await session.refresh(team_to_update)

    return team_to_update


async def delete_team_from_db(session: AsyncSession, team_to_delete: Team):
    await session.delete(team_to_delete)
    await session.commit()


async def get_all_teams_db(session: AsyncSession, params: Params) -> Sequence[Team]:
    query = select(Team)
    return await paginate(session, query, params)


async def get_team_by_id(session: AsyncSession, id: int):
    query = select(Team).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_team_full_info_by_id(session: AsyncSession, id: int):
    query = (
        select(Team)
        .filter_by(id=id)
        .options(joinedload(Team.members), joinedload(Team.team_lead))
    )
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
