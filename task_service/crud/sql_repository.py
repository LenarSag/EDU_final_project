from typing import Optional, Sequence
from uuid import UUID

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate

from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.models.task import Task
from infrastructure.models.user import User
from infrastructure.schemas.team import TeamCreate, TeamEdit


async def get_user_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_all_employee_tasks(session: AsyncSession, user_id: UUID, params: Params):
    query = (
        select(Task)
        .where(Task.employee_id == user_id)
        .options(selectinload(Task.manager))
    )
    return await paginate(session, query, params)


async def get_all_manager_tasks(session: AsyncSession, user_id: UUID, params: Params):
    query = (
        select(Task)
        .where(Task.manager_id == user_id)
        .options(selectinload(Task.employee))
    )
    return await paginate(session, query, params)


async def get_all_user_tasks(session: AsyncSession, user_id: UUID, params: Params):
    query = (
        select(Task)
        .where(or_(Task.employee_id == user_id, Task.manager_id == user_id))
        .options(selectinload(Task.manager), selectinload(Task.employee))
    )
    return await paginate(session, query, params)
