from datetime import timezone, datetime, timedelta

from api.schemas import MessageMetadata
from database import MessageRecord
from database import async_session_maker
from memory import persistent_memory, short_term


class UnifiedMemoryManager:
    def __init__(self) -> None:
        self.session_maker = async_session_maker
        self.short_term = short_term

    def _prepay(
        self, data: MessageMetadata, assistant_message: str
    ) -> tuple[str, datetime, int]:
        virtual_id = data.message_id + 1

        tz_moscow = timezone(timedelta(hours=3))
        now = datetime.now(tz_moscow)

        timestamp = now.strftime("%a %d.%m.%Y | %I:%M:%S %p")

        injected_assistant_text = f"[MSG_ID: {virtual_id} | TIME: {timestamp} | ACTIONS_TAKEN: True] {assistant_message}"

        hour_12 = now.hour % 12
        if hour_12 == 0:
            hour_12 = 12

        return injected_assistant_text, now, hour_12

    async def save_user_message(self, data: MessageMetadata) -> MessageRecord:
        async with self.session_maker() as session:
            user_record = await persistent_memory.save_user_message(session, data)
            await session.commit()
            await session.refresh(user_record)

        await self.short_term.append_message(
            chat_id=data.chat_id, role="user", content=user_record.content
        )
        return user_record

    async def save_assistant_message(
        self, data: MessageMetadata, clean_json: str
    ) -> MessageRecord:
        injected_text, now, hour_12 = self._prepay(data, clean_json)

        async with self.session_maker() as session:
            record = MessageRecord(
                chat_id=data.chat_id,
                telegram_message_id=data.message_id + 1,
                role="assistant",
                content=injected_text,
                telegram_meta={},
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

        await self.short_term.append_message(
            chat_id=data.chat_id, role="assistant", content=injected_text
        )
        return record

    async def get_cognitive_history(self, chat_id: int) -> list[dict[str, str]]:
        async with self.session_maker() as session:
            return await self.short_term.get_user_history(chat_id, session)


unified_memory_manager = UnifiedMemoryManager()
