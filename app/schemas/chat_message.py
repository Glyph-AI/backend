from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


class ChatMessageCreate(BaseModel):
    role: str
    content: str
    chat_id: int

    class Config:
        orm_mode = True
