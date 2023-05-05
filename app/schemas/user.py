from pydantic import BaseModel
from typing import List
from typing import Optional
from datetime import datetime

class GoogleAuth(BaseModel):
    token: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: str
    role: str


class User(UserBase):
    id: int
    created_at: datetime
    profile_picture_location: str | None = None
    subscribed: bool
    bots_left: int
    messages_left: int
    files_left: int
    allowed_bots: int
    allowed_messages: int
    allowed_files: int

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
