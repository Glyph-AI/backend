from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm.session import object_session
from dateutil.relativedelta import relativedelta
import bcrypt

from app.db.base_class import Base

FREEMIUM_BOTS = 3
FREEMIUM_MESSAGES = 50
FREEMIUM_FILES = 3
SUBSCRIPTION_MESSAGES = 750
ANNUAL_SUBSCRIPTION_MESSAGES = SUBSCRIPTION_MESSAGES * 12


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    _password = Column(String)
    google_user_id = Column(String)
    s3_id_link = Column(String)
    profile_picture_location = Column(String)
    allow_public_profile_picture = Column(Boolean, default=False)
    stripe_customer_id = Column(String)
    is_current = Column(Boolean, default=False)
    notifications = Column(Boolean)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user_uploads = relationship("UserUpload", back_populates="user")
    bots = association_proxy("bot_users", "bots")
    texts = relationship("Text", back_populates="user")
    embeddings = relationship("Embedding", back_populates="user")
    chats = relationship("Chat", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    devices = relationship("UserDevice", back_populates="user")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        # max password length of 72. Make sure we acknowledge this
        self._password = bcrypt.hashpw(plaintext.encode(
            "utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, plaintext):
        return bcrypt.checkpw(plaintext.encode("utf-8"), self._password.encode("utf-8"))

    @property
    def subscribed(self):
        return len(self.active_subscriptions()) > 0

    @property
    def subscription_in_good_standing(self):
        return self.subscribed and self.is_current

    @property
    def bots_left(self):
        if self.subscription_in_good_standing:
            active_subscription = self.active_subscriptions()[0]
            bots_limit = active_subscription.price_tier.product.bot_limit
            if bots_limit > 0:
                return bots_limit - len(self.bots)
            return -1

        return FREEMIUM_BOTS - len(self.bots)

    @property
    def message_count(self):
        from app.services import StripeService
        if len(self.chats) == 0:
            return 0

        if not self.subscription_in_good_standing:
            period_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            period_end = period_start + \
                relativedelta(months=1) - timedelta(days=1)
            return sum([i.messages_in_period(
                period_start, period_end) for i in self.chats])

        active_subscription = self.active_subscriptions()[0]
        session = object_session(self)

        if active_subscription.current_window_end_date is None or datetime.now(timezone.utc) > active_subscription.current_window_end_date:

            # if our subscription is from Stripe query Stripe
            if not active_subscription.is_google:
                print("NO VALUE SET, QUERYING STRIPE")
                period_start, period_end = StripeService.get_user_current_window(
                    active_subscription.stripe_subscription_id)

                active_subscription.current_window_start_date = period_start
                active_subscription.current_window_end_date = period_end
                session.commit()
            # query Google Play
            else:
                pass

        user_messages_in_period = sum([i.messages_in_period(
            active_subscription.current_window_start_date, active_subscription.current_window_end_date) for i in self.chats])

        return user_messages_in_period

    @property
    def bot_count(self):
        return len(self.bots)

    @property
    def file_count(self):
        return len(self.texts)

    @property
    def messages_left(self):
        message_count = self.message_count
        if self.subscription_in_good_standing:
            active_subscription = self.active_subscriptions()[0]
            message_limit = active_subscription.price_tier.product.message_limit
            if active_subscription.price_tier.name == "Annual":
                return (message_limit * 12) - message_count

            return message_limit - message_count

        return FREEMIUM_MESSAGES - self.message_count

    @property
    def files_left(self):
        if not self.subscription_in_good_standing:
            return FREEMIUM_FILES - len(self.texts)

        active_subscription = self.active_subscriptions()[0]
        files_limit = active_subscription.price_tier.product.text_limit
        if files_limit > 0:
            return files_limit - len(self.texts)

        return -1

    @property
    def allowed_files(self):
        if self.subscription_in_good_standing:
            active_subscription = self.active_subscriptions()[0]
            files_limit = active_subscription.price_tier.product.text_limit
            return files_limit

        return FREEMIUM_FILES

    @property
    def allowed_bots(self):
        if self.subscription_in_good_standing:
            active_subscription = self.active_subscriptions()[0]
            bots_limit = active_subscription.price_tier.product.bot_limit
            return bots_limit


        return FREEMIUM_BOTS

    @property
    def allowed_messages(self):
        if self.subscription_in_good_standing:
            active_subscription = self.active_subscriptions()[0]
            message_limit = active_subscription.price_tier.product.message_limit
            if active_subscription.price_tier.name == "Annual":
                return message_limit * 12

            return message_limit

        return FREEMIUM_MESSAGES

    @property
    def can_create_messages(self):
        return self.messages_left > 0

    @property
    def can_create_bots(self):
        return self.subscription_in_good_standing or self.bots_left > 0

    @property
    def can_create_files(self):
        return self.subscription_in_good_standing or self.files_left > 0
    
    @property
    def subscription_provider(self):
        if len(self.active_subscriptions()) == 0:
            return None
        
        if self.active_subscriptions()[0].is_google:
            return "Google"

        return "Stripe"

    @property
    def subscription_canceled(self):
        if len(self.active_subscriptions()) == 0:
            return False

        if self.active_subscriptions()[0].deleted_at:
            return True

        return False

    @property
    def monthly_cost(self):
        if self.subscription_in_good_standing:
            active_subscription = self.active_subscriptions()[0]
            if active_subscription.price_tier.name == "Annual":
                return active_subscription.billed_price // 12

            return active_subscription.billed_price

        return 0

    def active_subscriptions(self):
        active = [
            s for s in self.subscriptions if s.deleted_at is None or s.deleted_at >= datetime.now()]
        active.sort(key=lambda x: x.created_at, reverse=True)
        return active
