from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from database import ChatSession


async def get_or_create_session(session: AsyncSession, telegram_chat_id: int) -> int:
    stmt = select(ChatSession).where(ChatSession.telegram_chat_id == telegram_chat_id)
    result = await session.execute(stmt)
    chat_session = result.scalars().first()

    if not chat_session:
        chat_session = ChatSession(
            telegram_chat_id=telegram_chat_id, corrections_count=0
        )
        session.add(chat_session)
        try:
            await session.commit()
            await session.refresh(chat_session)
        except IntegrityError:
            # Защита от параллельных запросов
            await session.rollback()
            result = await session.execute(stmt)
            chat_session = result.scalars().first()

    return chat_session.id
