from pydantic import BaseModel
from datetime import datetime
from .chat import Chat
from .user_upload import UserUpload


class BotBase(BaseModel):
    name: str


class BotCreate(BotBase):
    class Config:
        orm_mode = True


class Bot(BotBase):
    id: int
    user_id: int
    created_at: datetime
    chats: list[Chat]
    user_uploads: list[UserUpload]

    class Config:
        orm_mode = True
