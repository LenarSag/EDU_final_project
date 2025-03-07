import asyncio
import logging

from fastapi import FastAPI
import uvicorn

from project_root.auth_service.db.sql_db import init_models
from project_root.auth_service.endpoints.login import login_router
from project_root.auth_service.endpoints.user import user_router
from project_root.config.config import settings


app = FastAPI()


app.include_router(login_router, prefix=f'{settings.API_URL}/auth')
app.include_router(user_router, prefix=f'{settings.API_URL}/users')


async def startup_event():
    await init_models()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    uvicorn.run(
        'project_root.auth_service.auth_main:app',
        host='127.0.0.1',
        port=8000,
        reload=True,
    )
