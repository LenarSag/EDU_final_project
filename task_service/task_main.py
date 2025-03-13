from fastapi import FastAPI
import uvicorn

from config.config import settings
from task_service.endpoints.task import task_router


app = FastAPI()


app.include_router(task_router, prefix=f'{settings.API_URL}/tasks')


if __name__ == '__main__':
    uvicorn.run(
        'task_main:app',
        host='127.0.0.1',
        port=8002,
        reload=True,
    )
