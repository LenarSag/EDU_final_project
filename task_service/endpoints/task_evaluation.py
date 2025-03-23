from typing import Annotated

from fastapi import Depends, APIRouter, Path, Request, status
from fastapi_pagination import Page, Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.redis_db import get_redis
from infrastructure.exceptions.basic_exeptions import NotFoundException
from infrastructure.exceptions.task_execeptions import (
    CantEvaluateException,
    EvalAlreadyExistsException,
    NotYourTaskException,
)
from infrastructure.models.user import UserPosition
from infrastructure.db.sql_db import get_session
from infrastructure.schemas.evaluation import (
    TaskEvaluationBase,
    TaskEvaluationCreate,
    TaskEvaluationFull,
)
from task_service.crud.sql_repository import get_task_by_id, get_task_full_info_by_id
from task_service.crud.sql_repository_eval import (
    create_new_task_evaluation,
    delete_eval_from_db,
    get_employee_evaluations,
    get_eval_by_task_id,
    update_evaluation,
)
from task_service.permissions.rbac_evaluation import (
    require_authentication,
    require_user_authentication,
)


task_eval_router = APIRouter()
all_evals_router = APIRouter()


@all_evals_router.get('/', response_model=Page[TaskEvaluationFull])
@require_authentication
async def get_employee_all_evaluations(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    params: Annotated[Params, Depends()],
    current_user=None,
):
    evaluations = await get_employee_evaluations(session, current_user.id, params)

    return evaluations


@task_eval_router.get('/', response_model=TaskEvaluationBase)
@require_user_authentication
async def get_evaluation(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    task_id: Annotated[int, Path(..., description='The id of the task')],
    current_user=None,
):
    task = await get_task_by_id(session, task_id)
    if not task:
        raise NotFoundException

    if current_user.position not in [UserPosition.ADMIN, UserPosition.CEO]:
        if current_user.position == UserPosition.MANAGER:
            if current_user.id != task.manager_id:
                raise NotYourTaskException
        else:
            if current_user.id != task.employee_id:
                raise NotYourTaskException

    evaluation = await get_eval_by_task_id(session, task_id)
    if not evaluation:
        raise NotFoundException
    return evaluation


@task_eval_router.post(
    '/', response_model=TaskEvaluationBase, status_code=status.HTTP_201_CREATED
)
@require_user_authentication
async def create_task_evaluation(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    task_id: Annotated[int, Path(..., description='The id of the task')],
    new_task_eval_data: TaskEvaluationCreate,
    current_user=None,
):
    task = await get_task_full_info_by_id(session, task_id)
    if not task:
        raise NotFoundException
    if task.evaluation:
        raise EvalAlreadyExistsException

    if current_user.position not in [UserPosition.ADMIN, UserPosition.CEO]:
        if current_user.position == UserPosition.MANAGER:
            if current_user.id != task.manager_id:
                raise CantEvaluateException
        else:
            raise CantEvaluateException

    new_evaluation = await create_new_task_evaluation(
        session, new_task_eval_data, task_id
    )

    return new_evaluation


@task_eval_router.patch('/', response_model=TaskEvaluationBase)
@require_user_authentication
async def edit_task_evaluation(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    task_id: Annotated[int, Path(..., description='The id of the task')],
    new_task_eval_data: TaskEvaluationCreate,
    current_user=None,
):
    task = await get_task_full_info_by_id(session, task_id)
    if not task:
        raise NotFoundException
    if not task.evaluation:
        raise NotFoundException

    if current_user.position not in [UserPosition.ADMIN, UserPosition.CEO]:
        if current_user.position == UserPosition.MANAGER:
            if current_user.id != task.manager_id:
                raise CantEvaluateException
        else:
            raise CantEvaluateException

    edited_task_eval = await update_evaluation(
        session, task.evaluation, new_task_eval_data
    )
    return edited_task_eval


@task_eval_router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
@require_user_authentication
async def delete_task_evaluation(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    task_id: Annotated[int, Path(..., description='The id of the task')],
    new_task_eval_data: TaskEvaluationCreate,
    current_user=None,
):
    task = await get_task_full_info_by_id(session, task_id)
    if not task:
        raise NotFoundException
    if not task.evaluation:
        raise NotFoundException

    if current_user.position not in [UserPosition.ADMIN, UserPosition.CEO]:
        if current_user.position == UserPosition.MANAGER:
            if current_user.id != task.manager_id:
                raise CantEvaluateException
        else:
            raise CantEvaluateException

    await delete_eval_from_db(session, task.evaluation)
