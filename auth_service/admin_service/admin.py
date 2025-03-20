from fastapi import Request
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend

from auth_service.security.authentication import (
    authenticate_user,
    create_access_token_for_user,
)
from auth_service.security.identification import check_jwt
from config.config import settings
from infrastructure.models.calendar import CalendarEvent
from infrastructure.models.evaluation import TaskEvaluation
from infrastructure.models.meeting import Meeting
from infrastructure.models.task import Task
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


class CalendarAdmin(ModelView, model=CalendarEvent):
    column_list = [
        CalendarEvent.id,
        CalendarEvent.event_type,
        CalendarEvent.title,
        CalendarEvent.description,
        CalendarEvent.start_time,
        CalendarEvent.end_time,
        CalendarEvent.created_at,
        CalendarEvent.event_creator,
    ]

    page_size = 50
    page_size_options = [10, 25, 50]


class EvaluationAdmin(ModelView, model=TaskEvaluation):
    column_list = [
        TaskEvaluation.id,
        TaskEvaluation.score_quality,
        TaskEvaluation.task_id,
        TaskEvaluation.task,
    ]

    page_size = 50
    page_size_options = [10, 25, 50]


class MeetingAdmin(ModelView, model=Meeting):
    column_list = [
        Meeting.id,
        Meeting.title,
        Meeting.description,
        Meeting.start_time,
        Meeting.end_time,
        Meeting.created_at,
        Meeting.meeting_creator_id,
        Meeting.meeting_creator,
        Meeting.participants,
    ]

    page_size = 50
    page_size_options = [10, 25, 50]


class TaskAdmin(ModelView, model=Task):
    column_list = [
        Task.id,
        Task.title,
        Task.description,
        Task.due_date,
        Task.status,
        Task.created_at,
        Task.updated_at,
        Task.employee_id,
        Task.manager_id,
        Task.task_employee,
        Task.task_manager,
        Task.evaluation,
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
