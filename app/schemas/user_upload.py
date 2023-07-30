from pydantic import BaseModel
from datetime import datetime


class UserUpload(BaseModel):
    id: int
    filename: str | None = None
    processed: bool
    include_in_context: bool | None = True
    created_at: datetime

    class Config:
        orm_mode = True

class ArchiveUrl(BaseModel):
    url: str
