from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from config.constants import MEETING_NAME_LENGTH
from infrastructure.schemas.user import UserMinimal


class MeetingCreate(BaseModel):
    title: str = Field(..., max_length=MEETING_NAME_LENGTH, description='Task name')
    description: str = Field(..., description='Meeting description')
    start_time: datetime = Field(..., description='Meeting start time')
    end_time: datetime = Field(..., description='Meeting end time')

    participants: list[UUID] = Field(..., description='Meeting participants')

    @model_validator(mode='after')
    def check_times(self):
        self.start_time = self.start_time.replace(tzinfo=None)
        self.end_time = self.end_time.replace(tzinfo=None)

        if self.start_time < datetime.now():
            raise ValueError(f'{self.start_time} cannot be earlier than now.')

        if self.end_time < self.start_time:
            raise ValueError(
                f'{self.end_time} cannot be earlier than {self.start_time}.'
            )

        return self


class MeetingEdit(BaseModel):
    title: Optional[str] = Field(
        None, max_length=MEETING_NAME_LENGTH, description='Meeting name'
    )
    description: Optional[str] = Field(None, description='Meeting description')
    start_time: datetime = Field(..., description='Meeting start time')
    end_time: datetime = Field(..., description='Meeting end time')

    participants: Optional[list[UUID]] = Field(None, description='Meeting participants')

    @model_validator(mode='after')
    def check_times(self):
        # Remove timezone info by making the datetime naive
        self.start_time = self.start_time.replace(tzinfo=None)
        self.end_time = self.end_time.replace(tzinfo=None)

        if self.start_time < datetime.now():
            raise ValueError(f'{self.start_time} cannot be earlier than now.')

        if self.end_time < self.start_time:
            raise ValueError(
                f'{self.end_time} cannot be earlier than {self.start_time}.'
            )

        return self


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
