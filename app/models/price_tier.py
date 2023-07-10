from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class PriceTier(Base):
    __tablename__ = "price_tiers"

    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"))
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True),
                    server_default=func.now())
    
    subscriptions = relationship("Subscription", back_populates="price_tier")
    product = relationship("Product", back_populates="price_tiers")

