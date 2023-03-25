from pydantic import BaseModel
from datetime import datetime

class UserUpload(BaseModel):
    id: int
    filename: str | None = None
    processed: bool
    created_at: datetime

    class Config:
        orm_mode = True