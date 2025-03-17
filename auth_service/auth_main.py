import asyncio
from fastapi import FastAPI, Request
from sqladmin import Admin
import uvicorn

from auth_service.admin_service.admin import AdminAuth, TeamAdmin, UserAdmin
from auth_service.endpoints.login import login_router
from auth_service.endpoints.user import user_router
from config.config import settings
from infrastructure.db.sql_db import engine, init_models


app = FastAPI()


authentication_backend = AdminAuth(secret_key='...')
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)


app.include_router(login_router, prefix=f'{settings.API_URL}/auth')
app.include_router(user_router, prefix=f'{settings.API_URL}/users')


admin.add_view(UserAdmin)
admin.add_view(TeamAdmin)

if __name__ == '__main__':
    asyncio.run(init_models())
    uvicorn.run(
        'auth_main:app',
        host='127.0.0.1',
        port=8000,
        reload=True,
    )
