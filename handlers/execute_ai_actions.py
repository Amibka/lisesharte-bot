import asyncio
import logging
import random
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message, ReactionTypeEmoji

from api import ActionPackage

logger = logging.getLogger("Lisheshart.ActionExecutor")


# todo Нужно добавить класс Ai и вызывать не aiogram, Ai.send_message()
async def execute_ai_actions(message: Message, ai_response: ActionPackage) -> None:
    bot: Bot = message.bot
    chat_id = message.chat.id

    sorted_actions = sorted(ai_response.actions, key=lambda a: a.sequence_id)

    for action in sorted_actions:
        tool = action.tool
        params = action.params

        logger.info(f"Выполнение команды ИИ: {tool} (Seq: {action.sequence_id})")

        try:
            if tool == "send_message":
                delay = min(len(params.text) * 0.04 + random.uniform(0.5, 1.5), 5.0)
                await bot.send_chat_action(chat_id=chat_id, action="typing")
                await asyncio.sleep(delay)

                await bot.send_message(
                    chat_id=chat_id, text=params.text, parse_mode="HTML"
                )

            elif tool == "reply_message":
                delay = min(len(params.text) * 0.04 + random.uniform(0.5, 1.5), 5.0)
                await bot.send_chat_action(chat_id=chat_id, action="typing")
                await asyncio.sleep(delay)

                await bot.send_message(
                    chat_id=chat_id,
                    text=params.text,
                    reply_to_message_id=params.reply_to_message_id,
                    parse_mode="HTML",
                )

            elif tool == "delete_message":
                if params.message_id == message.message_id:
                    logger.warning(
                        f"Заблокирована попытка ИИ удалить входящее сообщение пользователя (ID {params.message_id})!"
                    )
                    continue

                await bot.delete_message(chat_id=chat_id, message_id=params.message_id)

            elif tool == "message_reaction":
                reaction = [ReactionTypeEmoji(emoji=params.emoji)]
                await bot.set_message_reaction(
                    chat_id=chat_id,
                    message_id=params.target_message_id,
                    reaction=reaction,
                    is_big=params.is_big,
                )

            elif tool == "send_chat_action":
                await bot.send_chat_action(chat_id=chat_id, action=params.action)

        except TelegramAPIError as e:
            logger.error(f"Сбой отправки команды в Telegram API ({tool}): {e}")
            break

        except Exception as e:
            logger.error(f"Непредвиденная системная ошибка при обработке {tool}: {e}")
            break
