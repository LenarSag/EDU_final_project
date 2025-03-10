from fastapi import FastAPI
import uvicorn

from auth_service.endpoints.login import login_router
from auth_service.endpoints.user import user_router
from config.config import settings


app = FastAPI()


app.include_router(login_router, prefix=f'{settings.API_URL}/auth')
app.include_router(user_router, prefix=f'{settings.API_URL}/users')


if __name__ == '__main__':
    uvicorn.run(
        'auth_main:app',
        host='127.0.0.1',
        port=8000,
        reload=True,
    )
