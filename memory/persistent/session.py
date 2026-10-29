import asyncio
import json
import os
from datetime import datetime

from core import config

from sqlmodel.ext.asyncio.session import AsyncSession
from database import MessageRecord


class LISESHARTE_MEMORY:
    def __init__(self, file_path: str = "memory_storage.json") -> None:
        self.file_path = file_path
        self.storage = {}
        self._load_from_file()

    def _load_from_file(self) -> None:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    # В JSON ключи всегда строки, поэтому конвертируем их обратно в int (telegram_id)
                    data = json.load(f)
                    self.storage = {int(k): v for k, v in data.items()}
            except Exception as e:
                print(f"Ошибка при загрузке памяти из файла: {e}")
                self.storage = {}

    def _save_to_file_sync(self) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.storage, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении памяти на диск: {e}")

    def read_memory(self, telegram_id: int):
        limit = int(config.WINDOW_MEMORY_LIMIT)
        user_history = self.storage.get(telegram_id, [])
        return user_history[-limit:]

    async def save(
        self, session: AsyncSession, chat_session_id: int, message
    ) -> MessageRecord:

        meta_payload = {
            "username": message.from_user.username,
            "is_premium": getattr(message.from_user, "is_premium", False),
            "reply_to_id": message.reply_to_message.message_id
            if message.reply_to_message
            else None,
        }

        record = MessageRecord(
            chat_session_id=chat_session_id,
            telegram_message_id=message.message_id,
            role="user",
            raw_content=message.text,
            injected_content=f"[MSG_ID: {message.message_id}] {message.text}",
            telegram_meta=meta_payload,
            created_at=datetime.utcnow(),
        )

        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


memory = LISESHARTE_MEMORY()
