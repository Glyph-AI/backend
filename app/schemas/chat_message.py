from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    hidden: bool
    tts: bool | None = False

    class Config:
        orm_mode = True


class ChatMessageCreate(BaseModel):
    role: str
    content: str
    chat_id: int
    tts: bool | None = False

    class Config:
        orm_mode = True


class ApiChatMessageCreate(BaseModel):
    content: str


class ChatMessageCreateHidden(BaseModel):
    role: str
    content: str
    chat_id: int
    hidden: bool

    class Config:
        orm_mode = True
