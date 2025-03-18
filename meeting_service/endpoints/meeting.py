from typing import Annotated, Optional, Union

from fastapi import Depends, APIRouter, Request, status
from fastapi_pagination import Page, Params
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.redis_db import get_redis
from infrastructure.exceptions.auth_exceptions import UserNotFoundException
from infrastructure.exceptions.basic_exeptions import NotFoundException
from infrastructure.exceptions.meeting_exceptions import (
    AtLeastTwoMeetingParticipantsException,
    CantEditMeetingException,
    MeetingMembersNotFoundException,
    MeetingMembersNotUniqueException,
    NotYourMeetingException,
)
from infrastructure.models.user import UserPosition
from infrastructure.db.sql_db import get_session
from infrastructure.schemas.meeting import MeetingCreate, MeetingEdit, MeetingFull
from meeting_service.crud.sql_repository import (
    create_new_meeting,
    delete_meeting_from_db,
    get_all_employee_meetings,
    get_meeting_full_info_by_id,
    get_users_by_ids,
    update_meeting,
)
from meeting_service.permissions.rbac_meeting import (
    require_authentication,
    require_position_authentication,
    require_user_authentication,
)


meeting_router = APIRouter()


@meeting_router.get('/', response_model=Page[MeetingFull])
@require_authentication
async def get_my_tasks(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    params: Annotated[Params, Depends()],
    current_user=None,
):
    meetings = await get_all_employee_meetings(session, current_user.id, params)
    return meetings


@meeting_router.post(
    '/', response_model=MeetingFull, status_code=status.HTTP_201_CREATED
)
@require_position_authentication(
    [UserPosition.MANAGER, UserPosition.CEO, UserPosition.ADMIN]
)
async def create_meeting(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    new_meeting_data: MeetingCreate,
    current_user=None,
):
    new_meeting_data.participants.append(current_user.id)

    if len(new_meeting_data.participants) != len(set(new_meeting_data.participants)):
        raise MeetingMembersNotUniqueException
    participants = await get_users_by_ids(session, new_meeting_data.participants)
    if len(new_meeting_data.participants) != len(participants):
        raise MeetingMembersNotFoundException

    if len(participants) < 2:
        raise AtLeastTwoMeetingParticipantsException

    new_team = await create_new_meeting(session, new_meeting_data, current_user.id)

    return new_team


@meeting_router.get('/{meeting_id}', response_model=MeetingFull)
@require_user_authentication
async def get_meeting_full_info(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    meeting_id: int,
    current_user=None,
):
    meeting = await get_meeting_full_info_by_id(session, meeting_id)
    if not meeting:
        raise NotFoundException

    if (
        current_user.position != UserPosition.ADMIN
        or current_user.position != UserPosition.CEO
    ):
        if current_user.id not in [
            participants.id for participants in meeting.participants
        ]:
            raise NotYourMeetingException

    return meeting


@meeting_router.patch('/{meeting_id}', response_model=MeetingFull)
@require_user_authentication
async def edit_meeting(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    meeting_id: int,
    new_meeting_data: MeetingEdit,
    current_user=None,
):
    meeting = await get_meeting_full_info_by_id(session, meeting_id)
    if not meeting:
        raise NotFoundException
    if (
        current_user.position != UserPosition.ADMIN
        or current_user.position != UserPosition.CEO
    ):
        if current_user.id != meeting.meeting_creator_id:
            raise CantEditMeetingException

    participants = None
    if new_meeting_data.participants:
        new_meeting_data.participants.append(current_user.id)

        if len(new_meeting_data.participants) != len(
            set(new_meeting_data.participants)
        ):
            raise MeetingMembersNotUniqueException

        participants = await get_users_by_ids(session, new_meeting_data.participants)
        if len(new_meeting_data.participants) != len(participants):
            raise MeetingMembersNotFoundException

        if len(participants) < 2:
            raise AtLeastTwoMeetingParticipantsException

    updated_task = await update_meeting(
        session, meeting, new_meeting_data, participants
    )
    return updated_task


@meeting_router.delete('/{meeting_id}', status_code=status.HTTP_204_NO_CONTENT)
@require_user_authentication
async def delete_meeting(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    meeting_id: int,
    current_user=None,
):
    meeting = await get_meeting_full_info_by_id(session, meeting_id)
    if not meeting:
        raise NotFoundException
    if (
        current_user.position != UserPosition.ADMIN
        or current_user.position != UserPosition.CEO
    ):
        if current_user.id != meeting.meeting_creator_id:
            raise CantEditMeetingException

    await delete_meeting_from_db(session, meeting)
