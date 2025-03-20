import re

USERNAME_LENGTH = 50
EMAIL_LENGTH = 150

MAX_DAYS_INACTIVE = 30

TEAM_NAME_LENGTH = 50
TASK_NAME_LENGTH = 50
EVENT_NAME_LENGTH = 50
MEETING_NAME_LENGTH = 50

PASSWORD_REGEX = re.compile(
    r'^'
    r'(?=.*[a-z])'
    r'(?=.*[A-Z])'
    r'(?=.*\d)'
    r'(?=.*[@$!%*?&])'
    r'[A-Za-z\d@$!%*?&]'
    r'{8,50}$'
)

SERVICE_SECRET_KEY_HEADER = 'X-Service-Secret-Key'
SERVICE_AUTH_HEADER = 'X-Service-Auth'
USER_AUTH_HEADER = 'Authorization'


USER_REDIS_KEY = 'user'

DAYS_TILL_DELETE = 30
