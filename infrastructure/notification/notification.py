async def send_email(
    email: list[str], subject: str = 'Notification', message: str = 'Empty message'
):
    """Fake email sender: just prints the email content instead of sending it."""
    print('--- FAKE EMAIL SENT ---')
    print(f'To: {", ".join(email)}')
    print(f'Subject: {subject}')
    print(f'Message:\n{message}')
    print('------------------------')
