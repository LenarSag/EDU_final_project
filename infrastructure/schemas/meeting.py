from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from config.constants import MEETING_NAME_LENGTH
from infrastructure.schemas.user import UserMinimal


class MeetingCreate(BaseModel):
    title: str = Field(..., max_length=MEETING_NAME_LENGTH, description='Task name')
    description: str = Field(..., description='Meeting description')
    start_time: datetime = Field(..., description='Meeting start time')
    end_time: datetime = Field(..., description='Meeting end time')


class MeetingEdit(BaseModel):
    title: Optional[str] = Field(
        None, max_length=MEETING_NAME_LENGTH, description='Meeting name'
    )
    description: Optional[str] = Field(None, description='Meeting description')
    start_time: Optional[datetime] = Field(None, description='Meeting start time')
    end_time: Optional[datetime] = Field(None, description='Meeting end time')


class MeetingBase(BaseModel):
    id: int = Field(..., description='Meeting id')
    title: str = Field(..., description='Meeting name')
    description: str = Field(..., description='Meeting description')
    start_time: datetime = Field(..., description='Start time')
    end_time: datetime = Field(..., description='End time')
    created_at: datetime = Field(..., description='Meeting creation time')
    meeting_creator_id: Optional[UUID] = Field(None, description='Meeting creator id')
    calendar_event_id: Optional[int] = Field(None, description='Meeting calendar id')

    model_config = ConfigDict(from_attributes=True)


class MeetingFull(MeetingBase):
    meeting_creator: UserMinimal = Field(..., description='Meeting creator')
    participants: list[UserMinimal] = Field(..., description='Meeting participants')
