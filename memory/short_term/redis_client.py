import json
import logging
from typing import List, Dict, Any
import redis.asyncio as aioredis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core import config
from database.models import MessageRecord

logger = logging.getLogger("Lisheshart.Redis")


class RedisMemoryManager:
    def __init__(self) -> None:
        self.redis: aioredis.Redis = aioredis.from_url(
            config.REDIS_URL, decode_responses=True, encoding="utf-8", protocol=2
        )
        self.ttl = 2592000  # 30 дней в секундах

    def _get_key(self, chat_id: int) -> str:
        return f"history:{chat_id}"

    async def get_user_history(
        self, chat_id: int, db_session: AsyncSession
    ) -> List[Dict[str, str]]:
        key = self._get_key(chat_id)
        limit = int(config.WINDOW_MEMORY_LIMIT)

        if await self.redis.exists(key):
            raw_history = await self.redis.lrange(key, -limit, -1)
            return [json.loads(msg) for msg in raw_history]

        lock_key = f"lock:warm:{chat_id}"

        async with self.redis.lock(lock_key, timeout=5, blocking_timeout=3):
            if await self.redis.exists(key):
                raw_history = await self.redis.lrange(key, -limit, -1)
                return [json.loads(msg) for msg in raw_history]

            logger.info(
                f"Кэш Redis пуст. Запускаем ПОЛНЫЙ прогрев истории из SQLite для chat_id: {chat_id}"
            )

            stmt = (
                select(MessageRecord)
                .where(MessageRecord.chat_id == chat_id)
                .order_by(MessageRecord.created_at.asc())
            )
            result = await db_session.execute(stmt)
            records = result.scalars().all()

            history_list = []
            for rec in records:
                history_list.append({"role": rec.role, "content": rec.content})

            if history_list:
                string_messages = [json.dumps(msg) for msg in history_list]
                await self.redis.rpush(key, *string_messages)
                await self.redis.expire(key, self.ttl)
                logger.info(
                    f"Кэш Redis для chat_id {chat_id} прогрет полностью ({len(history_list)} сообщений)."
                )

            return history_list[-limit:]

    async def append_message(self, chat_id: int, role: str, content: str) -> None:
        key = self._get_key(chat_id)

        payload = json.dumps({"role": role, "content": content}, ensure_ascii=False)

        # RPUSHX запишет сообщение только если ключ уже существует.
        # Если кэш холодный — запись проигнорируется, предотвращая рассинхронизацию.
        await self.redis.rpushx(key, payload)
        await self.redis.expire(key, self.ttl)

    async def invalidate_cache(self, chat_id: int) -> None:
        key = self._get_key(chat_id)
        await self.redis.delete(key)

    async def close(self) -> None:
        await self.redis.aclose()


short_term = RedisMemoryManager()
