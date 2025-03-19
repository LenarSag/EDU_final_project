from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from config.constants import EVENT_NAME_LENGTH
from infrastructure.models.calendar import EventType
from infrastructure.schemas.meeting import MeetingBase
from infrastructure.schemas.task import TaskBase
from infrastructure.schemas.user import UserMinimal


class CalendarBase(BaseModel):
    id: int = Field(..., description='Calendar id')
    event_type: EventType = Field(..., description='Event_type')
    title: str = Field(..., description='Event title')
    description: str = Field(
        ..., max_length=EVENT_NAME_LENGTH, description='Event title'
    )
    start_time: datetime = Field(..., description='Event start time')
    end_time: datetime = Field(..., description='Event end time')
    created_at: datetime = Field(..., description='Event creation time')
    event_creator_id: Optional[UUID] = Field(None, description='Event creator id')

    model_config = ConfigDict(from_attributes=True)


class CalendarFull(CalendarBase):
    task: Optional[TaskBase] = Field(None, description='Event title')
    meeting: Optional[MeetingBase] = Field(None, description='Event title')
    event_creator: Optional[UserMinimal] = Field(None, description='Event creator')
