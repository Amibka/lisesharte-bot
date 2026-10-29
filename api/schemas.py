from typing import Literal, Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict
from typing_extensions import Annotated


class SendMessageParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(..., min_length=1, max_length=4096)


class ReplyMessageParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    reply_to_message_id: int = Field(..., ge=1)
    text: str = Field(..., min_length=1, max_length=4096)


class DeleteMessageParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message_id: int = Field(..., ge=1)


class MessageReactionParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_message_id: int = Field(..., ge=1)
    emoji: Literal[
        "👍",
        "👎",
        "❤️",
        "🔥",
        "🥰",
        "👏",
        "😁",
        "🤔",
        "🤯",
        "😱",
        "🤬",
        "😢",
        "🎉",
        "🤩",
        "🤮",
        "💩",
        "🙏",
        "👌",
        "🕊️",
        "🤡",
        "🥱",
        "🥴",
        "😍",
        "🐳",
        "❤️‍🔥",
        "💯",
        "🤣",
    ]
    is_big: bool = False


class SendChatActionParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["typing"] = "typing"


class SendMessageAction(BaseModel):
    sequence_id: int
    tool: Literal["send_message"] = "send_message"
    params: SendMessageParams


class ReplyMessageAction(BaseModel):
    sequence_id: int
    tool: Literal["reply_message"] = "reply_message"
    params: ReplyMessageParams


class DeleteMessageAction(BaseModel):
    sequence_id: int
    tool: Literal["delete_message"] = "delete_message"
    params: DeleteMessageParams


class MessageReactionAction(BaseModel):
    sequence_id: int
    tool: Literal["message_reaction"] = "message_reaction"
    params: MessageReactionParams


class SendChatActionAction(BaseModel):
    sequence_id: int
    tool: Literal["send_chat_action"] = "send_chat_action"
    params: SendChatActionParams


AiAction = Annotated[
    Union[
        SendMessageAction,
        ReplyMessageAction,
        DeleteMessageAction,
        MessageReactionAction,
        SendChatActionAction,
    ],
    Field(discriminator="tool"),
]


class ActionPackage(BaseModel):
    actions: List[AiAction]


class MessageMetadata(BaseModel):
    username: str | None = None
    premium: bool
    chat_id: int
    message_id: int
    reply_to_id: int | None = None
    content: str
