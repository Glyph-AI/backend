from pydantic import BaseModel
from typing import List
from typing import Optional
from datetime import datetime
from .user_device import UserDevice
from .price_tier import PriceTier


class GoogleAuth(BaseModel):
    token: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    id: int
    notifications: bool | None = None
    first_name: str | None = None
    last_name: str | None = None
    password: str | None = None

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str
    role: str


class User(UserBase):
    id: int
    created_at: datetime
    profile_picture_location: str | None = None
    subscribed: bool
    bot_count: int
    message_count: int
    file_count: int
    bots_left: int
    messages_left: int
    files_left: int
    allowed_bots: int
    allowed_messages: int
    allowed_files: int
    subscription_canceled: bool
    is_current: bool
    notifications: bool | None = None
    subscription_provider: str | None = None
    subscription_price_tier: PriceTier | None = None
    subscription_renewal_date: datetime | None = None
    last_used_device: UserDevice | None = None
    conversation_mode: bool

    class Config:
        orm_mode = True


class UserCreateSSO(UserBase):
    google_user_id: str
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class BotTokenData(BaseModel):
    id: int
    email: str
    chat_id: int | None = None
