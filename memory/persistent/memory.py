from datetime import datetime, timezone, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from database.models import ChatSession, MessageRecord
from api.schemas import MessageMetadata


class LisesharteMemoryManager:
    async def save_user_message(
        self, session: AsyncSession, data: MessageMetadata
    ) -> MessageRecord:
        tz_moscow = timezone(timedelta(hours=3))
        now = datetime.now(tz_moscow)

        timestamp = now.strftime("%a %d.%m.%Y | %I:%M:%S %p")

        await session.merge(ChatSession(telegram_chat_id=data.chat_id))
        await session.flush()

        injected_text = (
            f"[MSG_ID: {data.message_id} | "
            f"TIME: {timestamp} | "
            f"USER: @{data.username or 'unknown'} | "
            f"PREMIUM: {data.premium}] "
            f"{data.content}"
        )

        telegram_meta = {"username": data.username, "is_premium": data.premium}

        hour_12 = now.hour % 12
        if hour_12 == 0:
            hour_12 = 12

        record = MessageRecord(
            chat_id=data.chat_id,
            telegram_message_id=data.message_id,
            role="user",
            content=injected_text,
            telegram_meta=telegram_meta,
            created_at=now,
            year=now.year,
            month=now.month,
            day=now.day,
            day_of_week=now.weekday() + 1,
            hour=hour_12,
            minute=now.minute,
        )

        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


persistent_memory = LisesharteMemoryManager()
