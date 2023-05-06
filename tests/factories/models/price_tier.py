from app.models import PriceTier
from .base import BaseFactory

class PriceTierFactory(BaseFactory):
    def create(self, id="test_id", name="Monthly", price=1499):
        new_price_tier = PriceTier(
            id=id,
            name=name,
            price=price,
        )

        self.db_session.add(new_price_tier)
        self.db_session.commit()
        self.db_session.refresh(new_price_tier)

        return new_price_tier
