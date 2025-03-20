from typing import Optional, Sequence
from uuid import UUID

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, or_, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.calendar import CalendarEvent, EventType
from infrastructure.models.task import Task, TaskStatus
from infrastructure.models.user import User
from infrastructure.schemas.task import TaskCreate, TaskEdit


async def get_user_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_user_by_id_with_team(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id).options(joinedload(User.team))
    result = await session.execute(query)
    return result.scalar()


async def get_all_employee_tasks(
    session: AsyncSession, employee_id: UUID, params: Params
) -> Sequence[Task]:
    query = (
        select(Task)
        .where(Task.employee_id == employee_id)
        .options(selectinload(Task.task_manager))
    )
    return await paginate(session, query, params)


async def get_all_manager_tasks(
    session: AsyncSession, manager_id: UUID, params: Params
) -> Sequence[Task]:
    query = (
        select(Task)
        .where(Task.manager_id == manager_id)
        .options(selectinload(Task.task_employee))
    )
    return await paginate(session, query, params)


async def get_all_user_tasks(
    session: AsyncSession, user_id: UUID, params: Params
) -> Sequence[Task]:
    query = (
        select(Task)
        .where(or_(Task.employee_id == user_id, Task.manager_id == user_id))
        .options(selectinload(Task.task_manager), selectinload(Task.task_employee))
    )
    return await paginate(session, query, params)


async def get_task_full_info_by_id(
    session: AsyncSession, task_id: int
) -> Optional[Task]:
    query = (
        select(Task)
        .filter_by(id=task_id)
        .options(
            joinedload(Task.task_manager),
            joinedload(Task.task_employee),
            joinedload(Task.evaluation),
        )
    )
    result = await session.execute(query)
    return result.scalar()


async def get_task_by_id(session: AsyncSession, task_id: int) -> Optional[Task]:
    query = select(Task).filter_by(id=task_id)
    result = await session.execute(query)
    return result.scalar()


async def check_task_exist(
    session: AsyncSession, title: str, employee_id: UUID, manager_id: UUID
) -> Optional[Task]:
    query = select(Task).where(
        Task.title == title,
        Task.employee_id == employee_id,
        Task.manager_id == manager_id,
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_task_for_empoloyee(
    session: AsyncSession, new_task_data: TaskCreate, manager_id: UUID
):
    new_calendar_event = CalendarEvent(
        event_type=EventType.TASK,
        title=new_task_data.title,
        description=new_task_data.description,
        end_time=new_task_data.due_date,
        event_creator_id=manager_id,
    )

    session.add(new_calendar_event)
    await session.flush()

    new_task = Task(**new_task_data.model_dump())
    new_task.manager_id = manager_id
    new_task.calendar_event_id = new_calendar_event.id
    new_task.status = TaskStatus.IN_PROGRESS

    session.add(new_task)
    await session.commit()
    return new_task


async def update_task(
    session: AsyncSession, task_to_update: Task, new_task_data: TaskEdit
):
    for key, value in new_task_data.model_dump().items():
        if value:
            setattr(task_to_update, key, value)

    calendar_update_data = {
        'end_time': new_task_data.due_date,
        'title': new_task_data.title,
        'description': new_task_data.description,
    }
    calendar_update_data = {
        key: value for key, value in calendar_update_data.items() if value is not None
    }
    if calendar_update_data:
        await session.execute(
            update(CalendarEvent)
            .where(CalendarEvent.id == task_to_update.calendar_event_id)
            .values(**calendar_update_data)
        )

    await session.commit()
    await session.refresh(task_to_update)

    return task_to_update


async def delete_task_from_db(session: AsyncSession, task_to_delete: Task):
    await session.execute(
        delete(CalendarEvent).where(
            CalendarEvent.id == task_to_delete.calendar_event_id
        )
    )
    await session.delete(task_to_delete)
    await session.commit()
