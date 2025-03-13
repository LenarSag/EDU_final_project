from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Enum as SQLEnum, ForeignKey, func, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from config.constants import EVENT_NAME_LENGTH
from infrastructure.models.base import Base


class EventType(PyEnum):
    MEETING = 'Meeting'
    TASK = 'Task'


class CalendarEvent(Base):
    __tablename__ = 'calendar_events'

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType))
    title: Mapped[str] = mapped_column(String(EVENT_NAME_LENGTH))
    description: Mapped[str]
    start_time: Mapped[datetime]
    end_time: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    event_creator_id: Optional[Mapped[PG_UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )

    task = relationship('Task', back_populates='calendar_event')
    meeting = relationship('Meeting', back_populates='calendar_event')
    event_creator = relationship('User', back_populates='created_events')

    def __repr__(self):
        return f'<Event {self.title} - {self.event_type}>'
