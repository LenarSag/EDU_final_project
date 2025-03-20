from typing import Optional, Sequence
from uuid import UUID

from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import or_
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from infrastructure.models.evaluation import TaskEvaluation
from infrastructure.models.task import Task
from infrastructure.models.user import User
from infrastructure.schemas.evaluation import TaskEvaluationCreate


async def get_user_by_id(session: AsyncSession, id: UUID) -> Optional[User]:
    query = select(User).filter_by(id=id)
    result = await session.execute(query)
    return result.scalar()


async def get_eval_by_task_id(
    session: AsyncSession, task_id: int
) -> Optional[TaskEvaluation]:
    query = select(TaskEvaluation).filter_by(task_id=task_id)
    result = await session.execute(query)
    return result.scalar()


async def get_employee_evaluations(
    session: AsyncSession, user_id: str, params: Params
) -> Sequence[TaskEvaluation]:
    query = (
        select(TaskEvaluation)
        .join(Task)
        .filter(or_(Task.employee_id == user_id, Task.manager_id == user_id))
        .options(selectinload(TaskEvaluation.task))
    )
    return await paginate(session, query, params)


async def create_new_task_evaluation(
    session: AsyncSession,
    new_task_eval_data: TaskEvaluationCreate,
    task_id: int,
) -> TaskEvaluation:
    new_evaluation = TaskEvaluation(
        score_quality=new_task_eval_data.score_quality, task_id=task_id
    )
    session.add(new_evaluation)
    await session.commit()
    return new_evaluation


async def update_evaluation(
    session: AsyncSession,
    eval_to_update: TaskEvaluation,
    new_task_eval_data: TaskEvaluationCreate,
) -> TaskEvaluation:
    eval_to_update.score_quality = new_task_eval_data.score_quality

    await session.commit()
    await session.refresh(eval_to_update)

    return eval_to_update


async def delete_eval_from_db(
    session: AsyncSession, eval_to_delete: TaskEvaluation
) -> None:
    await session.delete(eval_to_delete)
    await session.commit()
