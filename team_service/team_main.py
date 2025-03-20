from fastapi import FastAPI
import uvicorn

from config.config import settings
from team_service.endpoints.team import team_router


app = FastAPI()


app.include_router(team_router, prefix=f'{settings.API_URL}/teams')


# if __name__ == '__main__':
#     uvicorn.run(
#         'team_main:app',
#         host='127.0.0.1',
#         port=8001,
#         reload=True,
#     )
