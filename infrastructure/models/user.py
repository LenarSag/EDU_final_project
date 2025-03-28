from datetime import date, timedelta
from enum import Enum as PyEnum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Enum as SQLEnum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from infrastructure.models.base import Base
from config.constants import (
    EMAIL_LENGTH,
    MAX_DAYS_INACTIVE,
    USERNAME_LENGTH,
)


class UserStatus(PyEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    FIRED = 'fired'


class UserPosition(PyEnum):
    NONE = 'None'
    ADMIN = 'Admin'
    JUNIOR = 'Junior'
    DEVELOPER = 'Developer'
    MANAGER = 'Manager'
    CEO = 'CEO'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(
        String(EMAIL_LENGTH), unique=True, nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(USERNAME_LENGTH), nullable=False)
    last_name: Mapped[str] = mapped_column(String(USERNAME_LENGTH), nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus), default=UserStatus.ACTIVE
    )
    position: Mapped[UserPosition] = mapped_column(
        SQLEnum(UserPosition), default=UserPosition.JUNIOR
    )
    hired_at: Mapped[date] = mapped_column(server_default=func.current_date())
    fired_at: Mapped[Optional[date]] = mapped_column(nullable=True)

    team_id: Mapped[int] = mapped_column(
        ForeignKey('teams.id', ondelete='SET NULL'),
        nullable=True,
    )

    team = relationship('Team', back_populates='members', foreign_keys=[team_id])
    team_lead = relationship(
        'Team', back_populates='team_lead', foreign_keys='Team.team_lead_id'
    )
    gotten_tasks = relationship(
        'Task', back_populates='task_employee', foreign_keys='Task.employee_id'
    )
    assigned_tasks = relationship(
        'Task', back_populates='task_manager', foreign_keys='Task.manager_id'
    )

    meetings = relationship(
        'Meeting', secondary='user_meeting_table', back_populates='participants'
    )
    created_events = relationship('CalendarEvent', back_populates='event_creator')
    created_meetings = relationship('Meeting', back_populates='meeting_creator')

    def __repr__(self):
        return f'<User {self.id} - {self.email}, {self.first_name} {self.last_name}>'

    @property
    def is_rehirable(self):
        if self.fired_at is None:
            return False
        return date.today() <= self.fired_at + timedelta(days=MAX_DAYS_INACTIVE)
