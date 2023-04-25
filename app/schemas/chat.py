from pydantic import BaseModel
from typing import Any
from pydantic.utils import GetterDict
from datetime import datetime
from .chat_message import ChatMessage


class ChatBase(BaseModel):
    name: str
    bot_id: int


class Chat(ChatBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    chat_messages: list[ChatMessage] | None = None
    chat_token: str | None = None

    class Config:
        orm_mode = True
