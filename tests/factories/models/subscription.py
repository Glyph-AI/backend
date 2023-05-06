from app.models import Subscription
from .base import BaseFactory
from .user import UserFactory
from .price_tier import PriceTierFactory

class SubscriptionFactory(BaseFactory):
    def create(self, user=None, price_tier=None):
        if user is None:
            user = UserFactory(self.db_session).create()

        if price_tier is None:
            price_tier = PriceTierFactory(self.db_session).create()

        new_sub = Subscription(
            user_id=user.id,
            price_tier_id=price_tier.id,
            billed_price=price_tier.price,
            stripe_subscription_id="test_stripe_sub_id",
            stripe_subscription_item_id="test_stripe_subscription_item_id"
        )

        self.db_session.add(new_sub)
        self.db_session.commit()
        self.db_session.refresh(new_sub)

        return new_sub
