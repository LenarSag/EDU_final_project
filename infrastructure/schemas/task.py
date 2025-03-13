from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

from config.constants import TASK_NAME_LENGTH
from infrastructure.models.task import TaskStatus
from infrastructure.schemas.evaluation import TaskEvaluationBase
from infrastructure.schemas.user import UserMinimal


class TaskRoleEnum(str, Enum):
    EMPLOYEE = 'employee'
    MANAGER = 'manager'


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=TASK_NAME_LENGTH, description='Task name')
    description: str = Field(..., description='Task description')
    due_date: datetime = Field(..., description='Due date')
    employee_id: UUID = Field(..., description='Empleyee to execute task')


class TaskEdit(BaseModel):
    title: Optional[str] = Field(
        None, max_length=TASK_NAME_LENGTH, description='Task name'
    )
    description: Optional[str] = Field(None, description='Task description')
    due_date: Optional[datetime] = Field(None, description='Task due date')
    employee_id: Optional[UUID] = Field(None, description='Empleyee to execute task')


class TaskBase(BaseModel):
    id: int = Field(..., description='Task id')
    title: str = Field(..., description='Task name')
    description: str = Field(..., description='Task description')
    due_date: datetime = Field(..., description='Due date')
    status: TaskStatus = Field(..., description='Task status')
    created_at: datetime = Field(..., description='Task creation time')
    updated_at: datetime = Field(..., description='Task update time')
    calendar_event_id: int = Field(..., description='Calendar event id')

    model_config = ConfigDict(from_attributes=True)


class TaskEmployee(TaskBase):
    task_manager: Optional[UserMinimal] = Field(
        ..., description='Manager who set the task'
    )


class TaskManager(TaskBase):
    task_employee: UserMinimal = Field(..., description='User to execute task')


class TaskEmployeeManager(TaskEmployee, TaskManager):
    pass


class TaskFull(TaskEmployeeManager):
    evaluation: TaskEvaluationBase = Field(..., description='Task evaluation')
