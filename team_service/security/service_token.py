import asyncio
import httpx
from time import time

import jwt

from config.config import settings
from config.constants import SERVICE_SECRET_KEY_HEADER

SERVICE_JWT = None


async def fetch_service_token():
    global SERVICE_JWT
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f'{settings.AUTH_SERVICE}{settings.API_URL}/token_service',
                headers={
                    SERVICE_SECRET_KEY_HEADER: settings.SERVICES_COMMON_SECRET_KEY
                },
            )
            response.raise_for_status()
            data = response.json()
            SERVICE_JWT = data['access_token']
            print('Service JWT obtained:', SERVICE_JWT)
        except Exception as e:
            print('Failed to obtain service JWT:', e)


async def refresh_service_token():
    global SERVICE_JWT
    while True:
        if SERVICE_JWT:
            try:
                payload = jwt.decode(SERVICE_JWT, options={'verify_signature': False})
                exp_time = payload.get('exp')
                if exp_time:
                    remaining_time = exp_time - int(time())
                    if (
                        remaining_time < 60
                    ):  # Refresh if it expires in less than 1 minute
                        await fetch_service_token()
            except jwt.ExpiredSignatureError:
                print('Service JWT expired, fetching new token...')
                await fetch_service_token()
            except Exception as e:
                print('Error decoding JWT:', e)

        await asyncio.sleep(60)  # Check every 30 seconds
