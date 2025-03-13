from datetime import datetime
from typing import Optional

from sqlalchemy import Column, ForeignKey, Table, func, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from config.constants import MEETING_NAME_LENGTH
from infrastructure.models.base import Base


user_meeting = Table(
    'user_meeting_table',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column(
        'meeting_id', ForeignKey('meetings.id', ondelete='CASCADE'), primary_key=True
    ),
)


class Meeting(Base):
    __tablename__ = 'meetings'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(MEETING_NAME_LENGTH))
    description: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    meeting_creator_id: Mapped[Optional[PG_UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL')
    )
    calendar_event_id: Mapped[int] = mapped_column(
        ForeignKey('calendar_events.id', ondelete='SET NULL')
    )

    meeting_creator = relationship('Users', back_populates='created_meetings')
    calendar_event = relationship('CalendarEvent', back_populates='meeting')
    participants = relationship(
        'User', secondary='user_meeting_table', back_populates='meetings'
    )

    def __repr__(self):
        return f'<Event {self.title} - {self.description} starts at {self.start_time}>'
