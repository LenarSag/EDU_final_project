from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from config.constants import TEAM_NAME_LENGTH


class TeamCreate(BaseModel):
    name: str = Field(..., max_length=TEAM_NAME_LENGTH, description='Team name')
    description: Optional[str] = Field(None, description='Team description')
    team_lead_id: UUID = Field(..., description='Team lead id')

    members: Optional[list[UUID]] = Field(None, description='Team members')


class TeamEdit(BaseModel):
    name: Optional[str] = Field(
        ..., max_length=TEAM_NAME_LENGTH, description='Team name'
    )
    description: Optional[str] = Field(None, description='Team description')
    team_lead_id: Optional[UUID] = Field(None, description='Team lead id')

    members: Optional[list[UUID]] = Field(None, description='Team members')


class TeamBase(BaseModel):
    id: int = Field(..., description='Team id')
    name: str = Field(..., description='Team name')
    description: str = Field(..., description='Team description')
    team_lead_id: Optional[UUID] = Field(None, description='Team lead id')

    model_config = ConfigDict(from_attributes=True)


class TeamFull(TeamBase):
    members: 'Optional[list[UserMinimal]]' = Field(None, description='Team members')
    team_lead: 'Optional[UserMinimal]' = Field(None, description='Team lead')


from infrastructure.schemas.user import UserMinimal

TeamFull.model_rebuild()
