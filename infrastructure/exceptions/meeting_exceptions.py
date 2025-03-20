from fastapi import status, HTTPException


class MeetingMembersNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Meating members not found',
        )


class MeetingMembersNotUniqueException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Meeting members should be unique',
        )


class AtLeastTwoMeetingParticipantsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='At least two participants should be in the meeting',
        )


class NotYourMeetingException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not participant of this meeting',
        )


class CantEditMeetingException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have no rights to edit this meeting',
        )
