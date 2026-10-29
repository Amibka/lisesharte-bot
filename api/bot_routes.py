import json
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from api.schemas import MessageMetadata
from orchestrator import orchestrator

telegram_router = APIRouter()


import json


@telegram_router.post("/telegram/process")
async def process_message(data: MessageMetadata):
    clean_ai_json = await orchestrator.process_user_message(data)

    try:
        actions_list = json.loads(clean_ai_json)
    except Exception:
        actions_list = {"actions": []}

    return actions_list
