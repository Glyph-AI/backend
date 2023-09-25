from pydantic import BaseModel
from datetime import datetime
from .user import User
from .persona import Persona
from .tool import Tool
from .text import TextInfo
from typing import List


class BotBase(BaseModel):
    name: str
    description: str | None = None
    sharing_enabled: bool | None = False
    sharing_code: str | None = None
    avatar_location: str | None = None
    share_count: int | None = None
    available_in_store: bool | None = None

    class Config:
        orm_mode = True


class BotCreate(BaseModel):
    name: str
    sharing_enabled: bool | None = False
    sharing_code: str | None = None
    persona_id: int
    enabled_texts: list[TextInfo] | None = []
    enabled_tools: list[Tool] | None = []

    class Config:
        orm_mode = True


class Bot(BotBase):
    id: int
    created_at: datetime
    users: list[User]
    chats: "List[ChatListItem]"
    enabled_tools: list[Tool]
    enabled_texts: list[TextInfo]
    persona: Persona
    creator_id: int | None = None

    class Config:
        orm_mode = True


class BotUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    sharing_enabled: bool | None = None
    available_in_store: bool | None = None

    class Config:
        orm_mode = True


class BotSharingAdd(BaseModel):
    sharing_code: str


class BotApiInfo(BaseModel):
    user: "User"
    chat_id: int | None = None
    bot: Bot


class BotToken(BaseModel):
    token: str


from .chat import ChatListItem  # noqa
from .user import User  # noqa
Bot.update_forward_refs()
BotApiInfo.update_forward_refs()
