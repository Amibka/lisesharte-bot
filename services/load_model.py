import logging
import httpx
from core import config


async def load_model() -> bool:
    base_url = config.LM_STUDIO_BASE.rstrip("/")
    list_url = f"{base_url}/api/v1/models"
    load_url = f"{base_url}/api/v1/models/load"

    async with httpx.AsyncClient() as client:
        try:
            logging.info("Проверяем запущенные инстансы моделей в LM Studio...")
            list_response = await client.get(list_url, timeout=10.0)

            if list_response.status_code == 200:
                data = list_response.json()
                models = data.get("models", [])

                for model_info in models:
                    if model_info.get("key") == config.MODEL:
                        if model_info.get("loaded_instances"):
                            logging.info(
                                f"Локальная модель '{config.MODEL}' уже активна в памяти. Пропускаем шаг загрузки."
                            )
                            return True
                        break

            logging.info(
                f"Модель '{config.MODEL}' не активна в памяти. Отправляем команду на запуск..."
            )

            payload = {
                "model": config.MODEL,
                "context_length": int(config.CONTEXT_LENGTH),
                "flash_attention": bool(config.FLASH_ATTENTION),
                "offload_kv_cache_to_gpu": bool(config.OFFLOAD_KV_CACHE_TO_GPU),
            }

            response = await client.post(load_url, json=payload, timeout=60.0)
            response.raise_for_status()

            res_data = response.json()
            if res_data.get("status") == "loaded":
                logging.info(
                    f"Локальная модель '{config.MODEL}' успешно загружена в память!"
                )
                return True

            return False

        except httpx.HTTPStatusError as e:
            error_text = e.response.text.lower()
            if "already loaded" in error_text or "already" in error_text:
                logging.info(f"Локальная модель '{config.MODEL}' уже в памяти. Всё ок!")
                return True

            logging.error(
                f"HTTP ошибка при работе с LM Studio: {e.response.status_code} - {e.response.text}"
            )
            return False

        except httpx.ConnectError:
            logging.critical(
                "Не удалось подключиться к LM Studio. Программа вообще запущена?"
            )
            return False
        except Exception as e:
            logging.error(f"Непредвиденная ошибка при подготовке модели: {e}")
            return False
