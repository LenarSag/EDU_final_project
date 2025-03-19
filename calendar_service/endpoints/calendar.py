from typing import Annotated, Optional

from fastapi import Depends, APIRouter, Request
from fastapi_pagination import Page, Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from calendar_service.crud.sql_repository import (
    get_employee_events,
    get_event_full_info_by_id,
)
from calendar_service.permissions.rbac_calendar import require_authentication
from infrastructure.db.redis_db import get_redis
from infrastructure.exceptions.basic_exeptions import NotFoundException
from infrastructure.models.calendar import EventType
from infrastructure.models.user import UserPosition
from infrastructure.db.sql_db import get_session
from infrastructure.schemas.calendar import CalendarFull


calendar_router = APIRouter()


@calendar_router.get('/', response_model=Page[CalendarFull])
@require_authentication
async def get_my_calendar_events(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    params: Annotated[Params, Depends()],
    current_user=None,
    event_type: Optional[EventType] = None,
):
    events = await get_employee_events(session, current_user.id, params, event_type)
    print(events)

    return events


@calendar_router.get('/{calendar_id}', response_model=CalendarFull)
@require_authentication
async def get_calendar_event_info(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    calendar_id: int,
    current_user=None,
):
    if (
        current_user.position == UserPosition.ADMIN
        or current_user.position == UserPosition.CEO
    ):
        employee_id = None
    else:
        employee_id = current_user.id

    event = await get_event_full_info_by_id(session, employee_id, calendar_id)
    if not event:
        raise NotFoundException

    return event
