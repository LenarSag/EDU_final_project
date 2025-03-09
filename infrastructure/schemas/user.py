from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from config.constants import (
    EMAIL_LENGTH,
    USERNAME_LENGTH,
    PASSWORD_REGEX,
)
from infrastructure.models.user import UserPosition, UserStatus


class UserAuthentication(BaseModel):
    email: EmailStr = Field(..., description='Email')
    password: str = Field(..., description='Password')


class UserCreate(BaseModel):
    email: EmailStr = Field(..., max_length=EMAIL_LENGTH, description='Email address')
    first_name: str = Field(
        ...,
        max_length=USERNAME_LENGTH,
        pattern=r'^[\w.@+-]+$',
        description='Username (alphanumeric + [@.+-] only, max length: 50 characters).',
    )
    last_name: str = Field(
        ...,
        max_length=USERNAME_LENGTH,
        pattern=r'^[\w.@+-]+$',
        description='Username (alphanumeric + [@.+-] only, max length: 50 characters).',
    )
    password: str = Field(
        ...,
        pattern=PASSWORD_REGEX,
        description='Password (8-50 characters, must include lower-case, upper-case, digits, and special symbols).',
    )
    team_id: Optional[int] = Field(None, description='Teamd id')


class UserEditSelf(BaseModel):
    first_name: Optional[str] = Field(None, description='Username')
    last_name: Optional[str] = Field(None, description='Username')


class UserEditManager(UserEditSelf):
    status: Optional[UserStatus] = Field(None, description='User status')
    position: Optional[UserPosition] = Field(
        None, description='User postiion in the company'
    )
    team_id: Optional[int] = Field(None, description='Teamd id')


class UserMinimal(BaseModel):
    id: UUID = Field(..., description='User id')
    email: EmailStr = Field(..., description='Email address')
    first_name: str = Field(..., description='Username')
    last_name: str = Field(..., description='Username')
    status: UserStatus = Field(..., description='User status')
    position: UserPosition = Field(..., description='User postiion in the company')
    team_id: Optional[int] = Field(None, description='Teamd id')

    model_config = ConfigDict(from_attributes=True)


class UserBase(UserMinimal):
    hired_at: date = Field(..., description='Hiring date')
    fired_at: Optional[date] = Field(..., description='Firing date')


class UserFull(UserBase):
    team: 'Optional[TeamBase]' = Field(None, description="User's team")
    my_team_lead: Optional[UserMinimal] = Field(None, description="User's team lead")


from infrastructure.schemas.team import TeamBase

UserFull.model_rebuild()
