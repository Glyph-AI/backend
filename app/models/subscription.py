from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    price_tier_id = Column(String, ForeignKey("price_tiers.id"))
    billed_price = Column(Float, nullable=False)
    stripe_subscription_id = Column(String, nullable=False)
    stripe_subscription_item_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())
    deleted_at = Column(DateTime)

    user = relationship("User", back_populates="subscriptions")
    price_tier = relationship("PriceTier", back_populates="subscriptions")
