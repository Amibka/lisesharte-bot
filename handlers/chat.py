import json
import logging

import httpx
from aiogram import Router, F
from aiogram.types import Message
from pydantic import ValidationError

from core import config
from api.schemas import ActionPackage, ReplyMessageAction, ReplyMessageParams
from handlers.execute_ai_actions import execute_ai_actions

ai_router = Router()


@ai_router.message(F.text)
async def handle_ai_chat(message: Message) -> None:
    payload = {
        "username": message.from_user.username,
        "premium": bool(message.from_user.is_premium),
        "chat_id": message.chat.id,
        "message_id": message.message_id,
        "reply_to_id": message.reply_to_message.message_id
        if message.reply_to_message
        else None,
        "content": message.text or "",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{config.FASTAPI_URL}/v1/telegram/process", json=payload, timeout=120.0
        )

    if response.status_code != 200:
        await message.answer(
            "<i>*Лишешарт ушла перебирать шестеренки... Бэкэнд недоступен.*</i>",
            parse_mode="HTML",
        )
        return

    response_data = response.json()

    try:
        raw_content = None
        ai_actions = None

        if "choices" in response_data:
            raw_content = response_data["choices"][0]["message"]["content"]

        elif "message" in response_data:
            raw_content = response_data["message"]["content"]

        elif "content" in response_data:
            raw_content = response_data["content"]

        elif "actions" in response_data:
            ai_actions = ActionPackage.model_validate(response_data)

        else:
            raise KeyError(
                f"Неизвестная структура ответа. Ключи: {list(response_data.keys())}"
            )

        if raw_content is not None:
            ai_actions = ActionPackage.model_validate_json(raw_content)

    except (ValidationError, KeyError, ValueError, TypeError) as e:
        dict_keys = (
            list(response_data.keys())
            if isinstance(response_data, dict)
            else "Это вообще не словарь!"
        )
        logging.error(
            f"Сбой парсинга. Ошибка: {e} | Реальные ключи в response_data: {dict_keys}"
        )

        ai_actions = ActionPackage(
            actions=[
                ReplyMessageAction(
                    sequence_id=1,
                    tool="reply_message",
                    params=ReplyMessageParams(
                        reply_to_message_id=message.message_id,
                        text="Ой, всё! Ты меня утомил своими расспросами, я спать хочу! 🙄",
                    ),
                )
            ]
        )

    await execute_ai_actions(message, ai_actions)
