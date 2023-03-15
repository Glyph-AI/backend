from pydantic import BaseModel
from datetime import datetime


class BotBase(BaseModel):
    name: str
    created_at: datetime


class BotCreate(BotBase):
    user_id: int

    class Config:
        orm_mode = True


class Bot(BotBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
