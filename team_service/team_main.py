from fastapi import FastAPI
import uvicorn

from config.config import settings
from team_service.endpoints.team import team_router


app = FastAPI()


app.include_router(team_router, prefix=f'{settings.API_URL}/teams')
