from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    message_limit = Column(Integer, nullable=False)
    bot_limit = Column(Integer, nullable=False)
    text_limit = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True),
                server_default=func.now())
    
    price_tiers = relationship("PriceTier", back_populates="price_tiers")