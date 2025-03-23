from fastapi import FastAPI
import uvicorn

from config.config import settings
from calendar_service.endpoints.calendar import calendar_router


app = FastAPI()


app.include_router(calendar_router, prefix=f'{settings.API_URL}/calendar')
