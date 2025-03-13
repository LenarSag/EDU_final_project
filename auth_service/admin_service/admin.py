from fastapi import Request
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend

from auth_service.security.authentication import (
    authenticate_user,
    create_access_token_for_user,
)
from auth_service.security.identification import check_jwt
from config.config import settings
from infrastructure.models.user import User, UserPosition
from infrastructure.models.team import Team
from infrastructure.db.sql_db import AsyncSessionLocal


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form['username'], form['password']
        async with AsyncSessionLocal() as session:
            user = await authenticate_user(session, email, password)
            if not user:
                return False
            if user.position != UserPosition.ADMIN:
                return False

            token = create_access_token_for_user(user)
            request.session.update({'Authorization': f'Bearer {token}'})

            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get('Authorization')
        if not token:
            return False

        check_jwt(token, settings.USER_JWT_SECRET_KEY)
        return True


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.first_name,
        User.last_name,
        User.status,
        User.position,
        User.hired_at,
        User.fired_at,
        User.team,
    ]
    page_size = 50
    page_size_options = [10, 25, 50]


class TeamAdmin(ModelView, model=Team):
    column_list = [
        Team.id,
        Team.name,
        Team.description,
        Team.team_lead,
        Team.members,
    ]
