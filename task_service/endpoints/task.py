from typing import Annotated, Optional, Union

from fastapi import Depends, APIRouter, Request, status
from fastapi_pagination import Page, Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession


from infrastructure.db.redis_db import get_redis

from infrastructure.models.user import UserPosition, UserStatus
from infrastructure.db.sql_db import get_session
from infrastructure.schemas.task import (
    TaskEmployee,
    TaskEmployeeManager,
    TaskManager,
    TaskRoleEnum,
)
from infrastructure.schemas.user import UserMinimal
from task_service.crud.sql_repository import (
    get_all_employee_tasks,
    get_all_manager_tasks,
    get_all_user_tasks,
)
from task_service.permissions.rbac_task import require_authentication


task_router = APIRouter()


@task_router.get(
    '/', response_model=Page[Union[TaskEmployeeManager, TaskEmployee, TaskManager]]
)
@require_authentication
async def get_my_tasks(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    params: Annotated[Params, Depends()],
    role: Optional[TaskRoleEnum] = None,
    current_user=None,
):
    if role == 'employee':
        tasks = await get_all_employee_tasks(session, current_user.id, params)
    elif role == 'manager':
        tasks = await get_all_manager_tasks(session, current_user.id, params)
    elif role is None:
        tasks = await get_all_user_tasks(session, current_user.id, params)

    return tasks


@task_router.post('/')
@require_authentication
async def create_task(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    params: Annotated[Params, Depends()],
    role: Optional[TaskRoleEnum] = None,
    current_user=None,
):
    if role == 'employee':
        tasks = await get_all_employee_tasks(session, current_user.id, params)
    elif role == 'manager':
        tasks = await get_all_manager_tasks(session, current_user.id, params)
    elif role is None:
        tasks = await get_all_user_tasks(session, current_user.id, params)

    return tasks


# @task_router.post('/', response_model=TeamFull, status_code=status.HTTP_201_CREATED)
# @require_position_authentication(
#     [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER]
# )
# async def create_new_task(
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
#     new_team_data: TeamCreate,
# ):
#     team = await get_team_by_name(session, new_team_data.name)
#     if team:
#         raise TeamAlreadyExistsException

#     team_lead_user = await get_user_by_id(session, new_team_data.team_lead_id)
#     if team_lead_user is None:
#         raise TeamLeadNotFoundException
#     if (
#         team_lead_user.position is not UserPosition.MANAGER
#         or team_lead_user.status is not UserStatus.ACTIVE
#     ):
#         raise NoManagerTeamLeadException

#     other_team = await get_team_by_team_lead_id(session, new_team_data.team_lead_id)
#     if other_team:
#         raise UserAlreadyTeamLeadException

#     if new_team_data.members:
#         if len(new_team_data.members) != len(set(new_team_data.members)):
#             raise TeamMembersNotUniqueException
#         members = await get_users_by_ids(session, new_team_data.members)
#         if len(new_team_data.members) != len(members):
#             raise TeamMembersNotFoundException
#         for user in members:
#             if user.team_id:
#                 raise UserAlreadyInTeamException

#     new_team = await create_team(session, new_team_data, members)
#     return new_team


# @team_router.get('/{team_id}', response_model=TeamFull)
# @require_authentication
# async def get_team_full_info(
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
#     team_id: int,
# ):
#     team = await get_team_full_info_by_id(session, team_id)
#     if team is None:
#         raise NotFoundException
#     return team


# @team_router.patch('/{team_id}', response_model=TeamFull)
# @require_position_authentication(
#     [UserPosition.ADMIN, UserPosition.CEO, UserPosition.MANAGER]
# )
# async def edit_team(
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
#     team_id: int,
#     new_team_data: TeamEdit,
# ):
#     team_to_update = await get_team_full_info_by_id(session, team_id)
#     if team_to_update is None:
#         raise NotFoundException

#     team_unique_name = await get_team_by_name(session, new_team_data.name)
#     if team_unique_name and team_unique_name.id != team_id:
#         raise TeamAlreadyExistsException

#     if new_team_data.team_lead_id:
#         team_lead_user = await get_user_by_id(session, new_team_data.team_lead_id)

#         if team_lead_user is None:
#             raise TeamLeadNotFoundException
#         if (
#             team_lead_user.position is not UserPosition.MANAGER
#             or team_lead_user.status is not UserStatus.ACTIVE
#         ):
#             raise NoManagerTeamLeadException

#         other_team = await get_team_by_team_lead_id(session, new_team_data.team_lead_id)
#         if other_team and other_team.id != team_id:
#             raise UserAlreadyTeamLeadException

#     if new_team_data.members:
#         if len(new_team_data.members) != len(set(new_team_data.members)):
#             raise TeamMembersNotUniqueException
#         members = await get_users_by_ids(session, new_team_data.members)
#         if len(new_team_data.members) != len(members):
#             raise TeamMembersNotFoundException
#         for user in members:
#             if user.team_id and user.team_id != team_id:
#                 raise UserAlreadyInTeamException

#     updated_team = await update_team(session, team_to_update, new_team_data, members)

#     return updated_team


# @team_router.delete('/{team_id}', status_code=status.HTTP_204_NO_CONTENT)
# @require_position_authentication([UserPosition.ADMIN, UserPosition.CEO])
# async def delete_team(
#     request: Request,
#     session: Annotated[AsyncSession, Depends(get_session)],
#     redis: Annotated[Redis, Depends(get_redis)],
#     team_id: int,
# ):
#     team_to_delete = await get_team_by_id(session, team_id)
#     if not team_to_delete:
#         raise NotFoundException

#     await delete_team_from_db(session, team_to_delete)
