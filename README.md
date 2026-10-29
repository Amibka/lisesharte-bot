# Lisesharte Bot

Учебный Telegram-бот для общения с локальной языковой моделью через LM Studio.
Сохраняет историю диалога и выполняет действия из JSON-ответа модели: сообщения, реакции и другие команды Telegram.

Технологии: Python 3.14, aiogram, FastAPI, Pydantic, SQLAlchemy/SQLModel, SQLite, Redis, Alembic, httpx.

Структура проекта:
- `main.py` — запуск бота, API и миграций.
- `handlers/` — обработка сообщений и выполнение действий Telegram.
- `api/` — HTTP-маршруты и схемы данных.
- `orchestrator/`, `services/` — обработка диалога и запросы к модели.
- `memory/`, `database/`, `alembic/` — история, кэш, модели БД и миграции.
- `core/`, `tools/`, `static/` — настройки, промпт, вспомогательные функции и изображения.
