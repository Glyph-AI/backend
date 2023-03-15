from pydantic import BaseModel
from datetime import datetime


class ChatBase(BaseModel):
    name: str
    created_at: datetime | None = None


class Chat(ChatBase):
    id: int
    user_id: int
    bot_id: int

    class Config:
        orm_mode = True
