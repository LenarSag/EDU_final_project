from pydantic import BaseModel, ConfigDict, Field


class TaskEvaluationCreate(BaseModel):
    score_quality: int = Field(..., ge=1, le=10, description='Score')


class TaskEvaluationBase(TaskEvaluationCreate):
    id: int = Field(..., description='Task id')
    task_id: int = Field(..., description='Task id')

    model_config = ConfigDict(from_attributes=True)


class TaskEvaluationFull(TaskEvaluationBase):
    task: 'TaskBase' = Field(..., description='Task')


from infrastructure.schemas.task import TaskBase

TaskEvaluationFull.model_rebuild()
