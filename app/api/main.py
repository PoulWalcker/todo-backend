from fastapi import APIRouter

from app.api.routes import users
from app.api.routes import auth
from app.api.routes import categories
from app.api.routes import statuses
from app.api.routes import items

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(categories.router)
api_router.include_router(statuses.router)
api_router.include_router(items.router)
