from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from project_root.config.constants import (
    EMAIL_LENGTH,
    USERNAME_LENGTH,
    PASSWORD_REGEX,
)
from project_root.infrastructure.models.user import UserPosition, UserStatus


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
    team_id: Optional[UUID] = Field(None, description='Teamd id')


class UserOut(BaseModel):
    id: UUID = Field(..., description='User id')
    email: EmailStr = Field(..., description='Email address')
    first_name: str = Field(..., description='Username')
    last_name: str = Field(..., description='Username')
    status: UserStatus = Field(..., description='User status')
    position: UserPosition = Field(..., description='User postiion in the company')
    hired_at: date = Field(..., description='Hiring date')
    team_id: Optional[UUID] = Field(None, description='Teamd id')

    model_config = ConfigDict(from_attributes=True)
