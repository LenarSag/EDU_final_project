from datetime import date, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Request, status
from fastapi_pagination import Page, Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.schemas.team import TeamBase, TeamCreate, TeamEdit, TeamFull

from team_service.crud.sql_repository import (
    create_team,
    get_all_teams_db,
    get_team_by_name,
    get_team_by_team_lead_id,
    get_team_full_info_by_id,
    get_user_by_id,
    get_users_by_ids,
)
from team_service.permissions.rbac_team import (
    require_position_authentication,
    require_authentication,
)
from infrastructure.db.redis_db import get_redis
from infrastructure.exceptions.exceptions import (
    AlreadyFiredException,
    EmailAlreadyExistsException,
    NoManagerTeamLeadException,
    NotAllowedToDeleteException,
    NotAllowedToFireException,
    NotAllowedToRehireException,
    NotFiredToRehireException,
    NotFoundException,
    TeamAlreadyExistsException,
    TeamLeadNotFoundException,
    TeamMembersNotFoundException,
    UserAlreadyInTeamException,
    UserAlreadyTeamLeadException,
    UserNotFoundException,
)
from config.constants import DAYS_TILL_DELETE, USER_REDIS_KEY
from infrastructure.models.user import UserPosition, UserStatus

from infrastructure.schemas.user import (
    UserEditManager,
    UserMinimal,
    UserEditSelf,
    UserFull,
)
from infrastructure.db.sql_db import get_session


team_router = APIRouter()


@team_router.get('/', response_model=Page[TeamBase])
@require_authentication
async def get_all_teams(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    params: Annotated[Params, Depends()],
):
    teams = await get_all_teams_db(session, params)
    return teams


@team_router.post('/', response_model=TeamFull)
@require_position_authentication(
    [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER]
)
async def create_new_team(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    new_team_data: TeamCreate,
):
    team = await get_team_by_name(session, new_team_data.name)
    if team:
        raise TeamAlreadyExistsException

    team_lead_user = await get_user_by_id(session, new_team_data.team_lead_id)
    if team_lead_user is None:
        raise TeamLeadNotFoundException
    if (
        team_lead_user.position is not UserPosition.MANAGER
        or team_lead_user.status is not UserStatus.ACTIVE
    ):
        raise NoManagerTeamLeadException

    other_team = await get_team_by_team_lead_id(session, new_team_data.team_lead_id)
    if other_team:
        raise UserAlreadyTeamLeadException

    if new_team_data.members:
        users = await get_users_by_ids(session, new_team_data.members)
        if len(new_team_data.members) != len(users):
            raise TeamMembersNotFoundException
        for user in users:
            if user.team_id:
                raise UserAlreadyInTeamException

    new_team = await create_team(session, new_team_data, users)
    return new_team


@team_router.get('/{team_id}', response_model=TeamFull)
@require_authentication
async def get_team_full_info(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    team_id: int,
):
    team = await get_team_full_info_by_id(session, team_id)
    if team is None:
        raise NotFoundException
    return team


@team_router.patch('/{team_id}', response_model=TeamBase)
@require_position_authentication(
    [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER]
)
async def edit_team(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    team_id: int,
    new_team_data: TeamEdit,
):
    team = await get_team_by_name(session, new_team_data.name)
    if team:
        raise TeamAlreadyExistsException
    new_team = await create_team(session, new_team_data)
    return new_team


# @user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
# @require_position_authentication([UserPosition.ADMIN, UserPosition.CEO], editing=True)
# async def delete_user(
#     user_id: UUID,
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
# ):
#     user_to_delete = await get_user_by_id(session, user_id)
#     if not user_to_delete:
#         raise NotFoundException
#     if user_to_delete.fired_at is None:
#         raise NotAllowedToDeleteException
#     if user_to_delete.fired_at + timedelta(days=DAYS_TILL_DELETE) > date.today():
#         raise NotAllowedToDeleteException

#     await delete_user_by_object(session, user_to_delete)
#     await delete_key_from_cache(USER_REDIS_KEY, str(user_id), redis)


# @user_router.patch('/{user_id}', response_model=UserMinimal)
# @require_position_authentication(
#     [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER], editing=True
# )
# async def edit_user_info(
#     user_id: UUID,
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
#     new_user_data: UserEditManager,
# ):
#     if new_user_data.email:
#         email_owner = await get_user_by_email(session, new_user_data.email)
#         if email_owner:
#             if email_owner.id != user_id:
#                 raise EmailAlreadyExistsException

#     edited_user = await update_user_data(session, user_id, new_user_data)
#     if edited_user is None:
#         raise UserNotFoundException

#     await set_key_to_cache(
#         USER_REDIS_KEY,
#         str(edited_user.id),
#         UserMinimal.model_validate(edited_user).model_dump_json(),
#         redis,
#     )

#     return edited_user


# @user_router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
# @require_position_authentication([UserPosition.ADMIN, UserPosition.CEO], editing=True)
# async def delete_user(
#     user_id: UUID,
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
# ):
#     user_to_delete = await get_user_by_id(session, user_id)
#     if not user_to_delete:
#         raise NotFoundException
#     if user_to_delete.fired_at is None:
#         raise NotAllowedToDeleteException
#     if user_to_delete.fired_at + timedelta(days=DAYS_TILL_DELETE) > date.today():
#         raise NotAllowedToDeleteException

#     await delete_user_by_object(session, user_to_delete)
#     await delete_key_from_cache(USER_REDIS_KEY, str(user_id), redis)
