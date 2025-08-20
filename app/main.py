from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings
from app.core.init_db import init_db


app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f'{settings.API_V1_STR}/openapi.json'
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(api_router, prefix=settings.API_V1_STR)
