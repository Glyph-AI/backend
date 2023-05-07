from pydantic import BaseModel
from typing import Any
from pydantic.utils import GetterDict
from datetime import datetime

class TextBase(BaseModel):
    name: str
    content: str
    text_type: str

class Text(TextBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TextInfo(BaseModel):
    id: int
    text_type: int
    created_at: datetime
    name: str

    class Config:
        orm_mode = True

class TextCreate(TextBase):
    class Config: 
        orm_mode = True

class BotTextStatusUpdate(BaseModel):
    bot_id: int
    text_id: int
    include_in_context: bool