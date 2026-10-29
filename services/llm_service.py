import httpx

from core import config, LISESHARTE_PROMPT
from tools import jsonexcrator


async def llm_service(messages_history: list[dict[str, str]]) -> str:
    try:
        api_messages = [
            {"role": "system", "content": LISESHARTE_PROMPT}
        ] + messages_history

        payload = {
            "model": config.MODEL,
            "messages": api_messages,
            "temperature": float(config.TEMPERATURE),
            "top_p": float(config.TOP_P),
            "frequency_penalty": float(config.FREQUENCY_PENALTY),
            "presence_penalty": float(config.PRESENCE_PENALTY),
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                config.LM_STUDIO_URL, json=payload, timeout=120.0
            )
        response.raise_for_status()

        res_data = response.json()
        raw_ai_json = res_data["choices"][0]["message"].get("content") or "[]"

        clean_ai_json = jsonexcrator(raw_ai_json)

        return clean_ai_json

    except Exception as e:
        print(f"Ошибка при работе с LM Studio: {e}")
        return "[]"
