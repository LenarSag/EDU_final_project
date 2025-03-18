from typing import Annotated, Optional, Union

from fastapi import BackgroundTasks, Depends, APIRouter, Request, status
from fastapi_pagination import Page, Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.redis_db import get_redis
from infrastructure.exceptions.auth_exceptions import UserNotFoundException
from infrastructure.exceptions.basic_exeptions import NotFoundException
from infrastructure.exceptions.task_execeptions import (
    CantEditTaskException,
    NotYourTaskException,
    TaskAlreadyExistsException,
)
from infrastructure.exceptions.team_exceptions import (
    NotUserManagerException,
    UserNotInTeamException,
)
from infrastructure.models.user import UserPosition
from infrastructure.db.sql_db import get_session
from infrastructure.notification.notification import send_email
from infrastructure.schemas.task import (
    TaskBase,
    TaskCreate,
    TaskEdit,
    TaskEmployee,
    TaskEmployeeManager,
    TaskFull,
    TaskManager,
    TaskRoleEnum,
)
from task_service.crud.sql_repository import (
    check_task_exist,
    create_task_for_empoloyee,
    delete_task_from_db,
    get_all_employee_tasks,
    get_all_manager_tasks,
    get_all_user_tasks,
    get_task_full_info_by_id,
    get_user_by_id_with_team,
    update_task,
)
from task_service.endpoints.task_evaluation import task_eval_router
from task_service.permissions.rbac_task import (
    require_authentication,
    require_position_authentication,
    require_user_authentication,
)


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


@task_router.post('/', response_model=TaskBase, status_code=status.HTTP_201_CREATED)
@require_position_authentication(
    [UserPosition.MANAGER, UserPosition.CEO, UserPosition.ADMIN]
)
async def create_task(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    new_task_data: TaskCreate,
    current_user=None,
):
    user_to_execute_task = await get_user_by_id_with_team(
        session, new_task_data.employee_id
    )

    if not user_to_execute_task:
        raise UserNotFoundException
    if current_user.position == UserPosition.MANAGER:
        if not user_to_execute_task.team:
            raise UserNotInTeamException
        if user_to_execute_task.team.team_lead_id != current_user.id:
            raise NotUserManagerException

    task_exists = await check_task_exist(
        session, new_task_data.title, new_task_data.employee_id, current_user.id
    )
    if task_exists is not None:
        raise TaskAlreadyExistsException

    new_task = await create_task_for_empoloyee(session, new_task_data, current_user.id)

    email = [user_to_execute_task.email]
    background_tasks.add_task(send_email, email, 'Notification', 'Task added')

    return new_task


@task_router.get('/{task_id}', response_model=TaskFull)
@require_user_authentication
async def get_task_full_info(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    task_id: int,
    current_user=None,
):
    task = await get_task_full_info_by_id(session, task_id)
    if not task:
        raise NotFoundException
    if (
        current_user.position != UserPosition.ADMIN
        or current_user.position != UserPosition.CEO
    ):
        if current_user.id != task.employee_id and current_user.id != task.manager_id:
            raise NotYourTaskException

    return task


@task_router.patch('/{task_id}', response_model=TaskFull)
@require_user_authentication
async def edit_task(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    task_id: int,
    new_task_data: TaskEdit,
    current_user=None,
):
    task_to_update = await get_task_full_info_by_id(session, task_id)
    if not task_to_update:
        raise NotFoundException
    if (
        current_user.position != UserPosition.ADMIN
        or current_user.position != UserPosition.CEO
    ):
        if current_user.id != task_to_update.manager_id:
            raise CantEditTaskException

    if new_task_data.title:
        task_name_exists = await check_task_exist(
            session, new_task_data.title, task_to_update.employee_id, current_user.id
        )
        if task_name_exists is not None and task_name_exists.id != task_id:
            raise TaskAlreadyExistsException

    updated_task = await update_task(session, task_to_update, new_task_data)

    email = [task_to_update.task_employee.email]
    background_tasks.add_task(send_email, email, 'Notification', 'Task changed')

    return updated_task


@task_router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
@require_user_authentication
async def delete_task(
    request: Request,
    background_tasks: BackgroundTasks,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    task_id: int,
    current_user=None,
):
    task_to_delete = await get_task_full_info_by_id(session, task_id)
    if not task_to_delete:
        raise NotFoundException
    if (
        current_user.position != UserPosition.ADMIN
        or current_user.position != UserPosition.CEO
    ):
        if current_user.id != task_to_delete.manager_id:
            raise CantEditTaskException

    await delete_task_from_db(session, task_to_delete)

    email = [task_to_delete.task_employee.email]
    background_tasks.add_task(send_email, email, 'Notification', 'Task deleted')


task_router.include_router(task_eval_router, prefix='/{task_id}/evaluation')
