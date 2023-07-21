from pydantic import BaseModel
from datetime import datetime

class UserDeviceBase(BaseModel):
    device_token: str
    user_id: int

class UserDevice(UserDeviceBase):
    id: int
    user_id: int
    device_token: str

    class Config:
        orm_mode = True