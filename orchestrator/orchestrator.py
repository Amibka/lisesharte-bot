from api.schemas import MessageMetadata
from memory import unified_memory_manager
from services import llm_service


class Orchestrator:
    def __init__(self) -> None:
        pass

    async def process_user_message(self, data: MessageMetadata) -> str:
        await unified_memory_manager.save_user_message(data)

        messages_history = await unified_memory_manager.get_cognitive_history(
            chat_id=data.chat_id
        )
        raw_ai_response = await llm_service(messages_history=messages_history)

        await unified_memory_manager.save_assistant_message(data, raw_ai_response)

        return raw_ai_response


orchestrator = Orchestrator()
