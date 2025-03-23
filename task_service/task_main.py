from fastapi import FastAPI
import uvicorn

from config.config import settings
from task_service.endpoints.task import task_router
from task_service.endpoints.task_evaluation import all_evals_router


app = FastAPI()


app.include_router(task_router, prefix=f'{settings.API_URL}/tasks')
app.include_router(all_evals_router, prefix=f'{settings.API_URL}/evaluations')
