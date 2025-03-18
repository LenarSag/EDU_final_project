from typing import Optional, Sequence
from uuid import UUID

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import delete, or_, update
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.models.calendar import CalendarEvent, EventType
from infrastructure.models.meeting import Meeting, user_meeting
from infrastructure.models.user import User
from infrastructure.schemas.meeting import MeetingCreate, MeetingEdit


async def get_user_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_users_by_ids(session: AsyncSession, ids: list[UUID]) -> Sequence[User]:
    query = select(User).where(User.id.in_(ids))
    result = await session.execute(query)
    return result.scalars().all()


async def get_meeting_full_info_by_id(
    session: AsyncSession, meeting_id: int
) -> Optional[Meeting]:
    query = (
        select(Meeting)
        .filter_by(id=meeting_id)
        .options(
            joinedload(Meeting.meeting_creator),
            joinedload(Meeting.participants),
        )
    )
    result = await session.execute(query)
    return result.scalar()


async def get_all_employee_meetings(
    session: AsyncSession, employee_id: UUID, params: Params
) -> Sequence[Meeting]:
    query = (
        select(Meeting)
        .join(Meeting.participants)
        .where(Meeting.participants.any(User.id == employee_id))
        .options(
            selectinload(Meeting.participants), selectinload(Meeting.meeting_creator)
        )
    )

    return await paginate(session, query, params)


async def get_meeting_by_id(
    session: AsyncSession, meeting_id: int
) -> Optional[Meeting]:
    query = select(Meeting).filter_by(id=meeting_id)
    result = await session.execute(query)
    return result.scalar()


async def create_new_meeting(
    session: AsyncSession,
    new_meeting_data: MeetingCreate,
    organizer_id: UUID,
):
    new_calendar_event = CalendarEvent(
        event_type=EventType.MEETING,
        title=new_meeting_data.title,
        description=new_meeting_data.description,
        start_time=new_meeting_data.start_time,
        end_time=new_meeting_data.start_time,
        event_creator_id=organizer_id,
    )

    session.add(new_calendar_event)
    await session.flush()

    new_meeting = Meeting(
        title=new_meeting_data.title,
        description=new_meeting_data.description,
        start_time=new_meeting_data.start_time,
        end_time=new_meeting_data.end_time,
        meeting_creator_id=organizer_id,
        calendar_event_id=new_calendar_event.id,
    )

    session.add(new_meeting)
    await session.flush()

    await session.execute(
        user_meeting.insert(),
        [
            {'user_id': id, 'meeting_id': new_meeting.id}
            for id in new_meeting_data.participants
        ],
    )

    await session.commit()
    await session.refresh(
        new_meeting, attribute_names=['participants', 'meeting_creator']
    )

    return new_meeting


async def update_meeting(
    session: AsyncSession,
    meeting_to_update: Meeting,
    new_meeting_data: MeetingEdit,
    participants: Optional[Sequence[User]],
):
    update_data = {
        key: value
        for key, value in new_meeting_data.model_dump().items()
        if value is not None
    }
    update_data.pop('participants', None)

    for key, value in update_data.items():
        if value:
            setattr(meeting_to_update, key, value)

    if participants:
        meeting_to_update.participants = participants

    await session.execute(
        update(CalendarEvent)
        .where(CalendarEvent.id == meeting_to_update.calendar_event_id)
        .values(**update_data)
    )

    await session.commit()
    await session.refresh(meeting_to_update)

    return meeting_to_update


async def delete_meeting_from_db(session: AsyncSession, meeting_to_delete: Meeting):
    await session.execute(
        delete(CalendarEvent).where(
            CalendarEvent.id == meeting_to_delete.calendar_event_id
        )
    )
    await session.delete(meeting_to_delete)
    await session.commit()
