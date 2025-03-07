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
