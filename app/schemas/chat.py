from pydantic import BaseModel
from datetime import datetime
from .chat_message import ChatMessage


class ChatBase(BaseModel):
    name: str


class Chat(ChatBase):
    id: int
    user_id: int
    bot_id: int
    created_at: datetime | None = None
    chat_messages: list[ChatMessage]
    chat_token: str | None = None

    class Config:
        orm_mode = True
