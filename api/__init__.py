from .schemas import *


from fastapi import APIRouter

from api.bot_routes import telegram_router
from api.memory_routes import memory_router


fastapi_hub_router = APIRouter()
fastapi_hub_router.include_router(telegram_router, prefix="/v1")
fastapi_hub_router.include_router(memory_router, prefix="/v1")
