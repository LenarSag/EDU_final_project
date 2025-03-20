from fastapi import status, HTTPException


class NotFiredToRehireException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User was not fired',
        )


class NotAllowedToRehireException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User cannot be rehired because the maximum rehire period has expired.',
        )


class NotAllowedToFireException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='CEO and admins can"t be fired.',
        )


class AlreadyFiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User already fired.',
        )
