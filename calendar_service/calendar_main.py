from fastapi import FastAPI
import uvicorn

from config.config import settings
from calendar_service.endpoints.meeting import meeting_router


app = FastAPI()


app.include_router(meeting_router, prefix=f'{settings.API_URL}/calendar')


if __name__ == '__main__':
    uvicorn.run(
        'calendar_main:app',
        host='127.0.0.1',
        port=8004,
        reload=True,
    )
