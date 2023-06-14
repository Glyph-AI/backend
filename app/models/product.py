from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True),
                server_default=func.now())
    
    price_tiers = relationship("PriceTier", back_populates="product")