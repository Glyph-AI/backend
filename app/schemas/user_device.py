from pydantic import BaseModel
from datetime import datetime

class UserDeviceBase(BaseModel):
    device_token: str
    user_id: int
    last_used: datetime | None = None

class UserDevice(UserDeviceBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True