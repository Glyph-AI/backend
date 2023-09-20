from pydantic import BaseModel
from datetime import datetime


class PriceTier(BaseModel):
    id: int
    product_id: str
    name: str
    price: float
    created_at: datetime

    class Config:
        orm_mode = True
