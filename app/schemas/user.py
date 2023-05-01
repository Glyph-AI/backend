from pydantic import BaseModel
from typing import List
from typing import Optional
from datetime import datetime


class GoogleAuth(BaseModel):
    token: str


class GoogleAuthorizationCode(BaseModel):
    code: str
    bot_id: str
    tool_id: str


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str


class User(UserBase):
    id: int
    created_at: datetime
    profile_picture_location: str | None = None
    subscribed: bool

    class Config:
        orm_mode = True


class UserCreateSSO(UserBase):
    google_user_id: str
    role: str

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
