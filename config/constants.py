import re

USERNAME_LENGTH = 50
EMAIL_LENGTH = 150

MAX_DAYS_INACTIVE = 30

TEAM_NAME_LENGTH = 50

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


USERMINIMAL_REDIS_KEY = 'user_min'
USERFULL_REDIS_KEY = 'user_full'
