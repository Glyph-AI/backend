from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from app.db.base_class import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    price_tier_id = Column(String, ForeignKey("price_tiers.id"))
    billed_price = Column(Float)
    stripe_subscription_id = Column(String)
    stripe_subscription_item_id = Column(String)
    current_window_start_date = Column(DateTime(timezone=True))
    current_window_end_date = Column(DateTime(timezone=True))
    google_token = Column(String)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())
    deleted_at = Column(DateTime)

    user = relationship("User", back_populates="subscriptions")
    price_tier = relationship("PriceTier", back_populates="subscriptions")

    @property
    def is_google(self):
        if self.google_token:
            return True
        return False
