from typing import Optional
from uuid import UUID

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.calendar import CalendarEvent, EventType
from infrastructure.models.meeting import Meeting
from infrastructure.models.task import Task
from infrastructure.models.user import User


async def get_user_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_employee_events(
    session: AsyncSession,
    employee_id: UUID,
    params: Params,
    event_type: Optional[EventType] = None,
):
    query = (
        select(CalendarEvent)
        .outerjoin(Meeting)
        .outerjoin(Task)
        .filter(
            or_(
                Meeting.participants.any(id=employee_id),
                Task.employee_id == employee_id,
                CalendarEvent.event_creator_id == employee_id,
            )
        )
        .options(
            selectinload(CalendarEvent.meeting),
            selectinload(CalendarEvent.task),
            selectinload(CalendarEvent.event_creator),
        )
    )

    if event_type:
        query = query.filter(CalendarEvent.event_type == event_type)

    return await paginate(session, query, params)


async def get_event_full_info_by_id(
    session: AsyncSession, employee_id: UUID, event_id: int
):
    if employee_id:
        query = (
            select(CalendarEvent)
            .outerjoin(Meeting)
            .outerjoin(Task)
            .filter(
                or_(
                    Meeting.participants.any(id=employee_id),
                    Task.employee_id == employee_id,
                    CalendarEvent.event_creator_id == employee_id,
                )
            )
            .options(
                selectinload(CalendarEvent.meeting),
                selectinload(CalendarEvent.task),
                selectinload(CalendarEvent.event_creator),
            )
        )
    else:
        query = select(CalendarEvent).options(
            selectinload(CalendarEvent.meeting),
            selectinload(CalendarEvent.task),
            selectinload(CalendarEvent.event_creator),
        )

    query = query.filter(CalendarEvent.id == event_id)
    result = await session.execute(query)

    return result.scalar()
