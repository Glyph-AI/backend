from pydantic import BaseModel
from datetime import datetime
from .chat import Chat
from .user import User
from .user_upload import UserUpload
from .persona import Persona
from .tool import Tool
from .text import TextInfo


class BotBase(BaseModel):
    name: str
    sharing_enabled: bool | None = False
    sharing_code: str | None = None


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
    chats: list[Chat]
    enabled_tools: list[Tool]
    enabled_texts: list[TextInfo]
    persona: Persona
    creator_id: int | None = None

    class Config:
        orm_mode = True


class BotUpdate(BaseModel):
    name: str | None = None
    sharing_enabled: bool | None = None

    class Config:
        orm_mode = True


class BotSharingAdd(BaseModel):
    sharing_code: str
