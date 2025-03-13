from pydantic import BaseModel, ConfigDict, Field


class TaskEvaluationCreate(BaseModel):
    id: int = Field(..., description='Task id')
    score_quality: int = Field(..., ge=1, le=10, description='Score')
    task_id: int = Field(..., description='Task id')


class TaskEvaluationBase(TaskEvaluationCreate):
    model_config = ConfigDict(from_attributes=True)
