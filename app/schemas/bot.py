from pydantic import BaseModel
from datetime import datetime
from .chat import Chat
from .user import User
from .user_upload import UserUpload
from .persona import Persona
from .tool import Tool


class BotBase(BaseModel):
    name: str
    sharing_enabled: bool | None = False
    sharing_code: str | None = None


class BotCreate(BaseModel):
    name: str
    sharing_enabled: bool | None = False
    sharing_code: str | None = None
    persona_id: int

    class Config:
        orm_mode = True


class Bot(BotBase):
    id: int
    created_at: datetime
    users: list[User]
    chats: list[Chat]
    enabled_tools: list[Tool]
    persona: Persona
    user_uploads: list[UserUpload]
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
