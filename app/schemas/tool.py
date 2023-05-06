from pydantic import BaseModel


class ToolBase(BaseModel):
    id: int
    name: str
    description: str
    user_configurable: bool


class Tool(ToolBase):
    class Config:
        orm_mode = True
