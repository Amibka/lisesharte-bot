from aiogram import Router
from .chat import ai_router

hub_router = Router()
hub_router.include_router(ai_router)
# hub_router.include_router(start_router)
