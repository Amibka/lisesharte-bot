from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Relationship, JSON
from sqlalchemy import Column, TIMESTAMP


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    telegram_chat_id: int = Field(
        primary_key=True, sa_column_kwargs={"autoincrement": False}
    )
    corrections_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    memory_text: str = Field(default="## Память пуста", max_length=10000)
    last_consolidated_at: datetime = Field(default_factory=datetime.utcnow)
    is_sleeping: bool = Field(default=False, index=True)

    messages: List["MessageRecord"] = Relationship(
        back_populates="chat_session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class MessageRecord(SQLModel, table=True):
    __tablename__ = "message_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chat_sessions.telegram_chat_id", index=True)
    telegram_message_id: int = Field(index=True)

    role: str = Field(max_length=20, index=True)
    content: str = Field(max_length=5000)

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    )

    year: int = Field(index=True)
    month: int = Field(index=True)
    day: int = Field(index=True)
    day_of_week: int = Field(index=True)  # Будет от 1 (Пн) до 7 (Вс)
    hour: int = Field(index=True)
    minute: int = Field(index=True)

    telegram_meta: Dict[str, Any] = Field(
        default_factory=dict, sa_column=Column(JSON, nullable=False)
    )

    chat_session: ChatSession = Relationship(back_populates="messages")
    is_consolidated: bool = Field(default=False, index=True)
