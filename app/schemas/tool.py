from pydantic import BaseModel


class ToolBase(BaseModel):
    id: int
    name: str
    description: str
    auth_provider: str | None = None
    is_authorized: bool


class Tool(ToolBase):
    class Config:
        orm_mode = True
