from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional


from sqlalchemy import Enum as SQLEnum, ForeignKey, UniqueConstraint, func, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from config.constants import TASK_NAME_LENGTH
from infrastructure.models.base import Base


class TaskStatus(PyEnum):
    IN_PROGRESS = 'In progress'
    COMPLETED = 'Completed'


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(TASK_NAME_LENGTH))
    description: Mapped[str]
    due_date: Mapped[datetime]
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.IN_PROGRESS
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        server_onupdate=func.now(), nullable=True
    )

    employee_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')
    )
    manager_id: Mapped[Optional[PG_UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True,
    )
    calendar_event_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey('calendar_events.id', ondelete='SET NULL'), nullable=True
    )

    task_employee = relationship(
        'User', back_populates='gotten_tasks', foreign_keys=[employee_id]
    )
    task_manager = relationship(
        'User', back_populates='assigned_tasks', foreign_keys=[manager_id]
    )
    calendar_event = relationship('CalendarEvent', back_populates='task', uselist=False)
    evaluation = relationship('TaskEvaluation', back_populates='task', uselist=False)

    __table_args__ = (
        UniqueConstraint(
            'title',
            'manager_id',
            'employee_id',
            'due_date',
            name='uq_task_title_mgr_emp_due',
        ),
    )

    def __repr__(self):
        return f'<Task {self.title} - {self.description} - {self.status}>'
