from fastapi import FastAPI
from sqladmin import Admin, ModelView
import uvicorn

from infrastructure.db.sql_db import engine, init_models
from infrastructure.models.user import User


app = FastAPI()
admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email]


admin.add_view(UserAdmin)


async def startup_event():
    await init_models()


if __name__ == '__main__':
    uvicorn.run(
        'infra_main:app',
        host='127.0.0.1',
        port=8001,
        reload=True,
    )
