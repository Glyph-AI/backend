from .bot import BotBase
from pydantic import BaseModel
from typing import Any
from pydantic.utils import GetterDict
from datetime import datetime
from .chat_message import ChatMessage


class ChatBase(BaseModel):
    name: str
    bot_id: int
    bot: "BotBase"


class ChatCreate(BaseModel):
    name: str
    bot_id: int

    class Config:
        orm_mode = True


class Chat(ChatBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    chat_messages: list[ChatMessage] | None = None

    class Config:
        orm_mode = True


class ChatListItem(ChatBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    last_message: ChatMessage | None = None

    class Config:
        orm_mode = True


class ChatApiAccess(ChatBase):
    chat_token: str

    class Config:
        orm_mode = True


from .bot import BotBase  # noqa
ChatBase.update_forward_refs()
Chat.update_forward_refs()
