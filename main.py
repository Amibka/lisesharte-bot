import asyncio
import logging
import sys

import uvicorn

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from alembic.config import Config

from alembic import command
from fastapi import FastAPI

from api import fastapi_hub_router
from core import config
from handlers import hub_router
from services import load_model

dp = Dispatcher()
app = FastAPI()
app.include_router(fastapi_hub_router)

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))


def run_migrations() -> None:
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def start_uvicorn_server() -> None:
    cfg = uvicorn.Config(app, host=config.IP, port=config.PORT, log_level="debug")
    server = uvicorn.Server(cfg)
    await server.serve()


async def start_bot() -> None:
    if config.LLM_PROVIDER == "lm_studio":
        model_ready = await load_model()
        if not model_ready:
            logging.critical(
                "Запуск бота отменен: локальная ИИ-машина не готова к работе."
            )
            sys.exit(1)
    else:
        logging.info("Используется облачный провайдер. Пропускаем прогрев VRAM.")

    dp.include_router(hub_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main() -> None:
    await asyncio.gather(start_uvicorn_server(), start_bot())


if __name__ == "__main__":
    print("Running database migrations...")
    run_migrations()
    if config.DEBUG:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        )

        asyncio.run(main())
    else:
        asyncio.run(main())
