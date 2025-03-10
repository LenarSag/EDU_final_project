from fastapi import FastAPI
import uvicorn

from config.config import settings
from team_service.endpoints.team import team_router
from team_service.security.service_token import (
    fetch_service_token,
    refresh_service_token,
)


app = FastAPI()


app.include_router(team_router, prefix=f'{settings.API_URL}/teams')


# @app.on_event('startup')
# async def startup_event():
#     await fetch_service_token()
#     asyncio.create_task(refresh_service_token())


if __name__ == '__main__':
    uvicorn.run(
        'team_main:app',
        host='127.0.0.1',
        port=8002,
        reload=True,
    )
