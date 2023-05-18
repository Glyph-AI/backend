from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from datetime import datetime, timezone
from sqlalchemy.orm.session import object_session
from app.subscription_tiers import tiers
import bcrypt

from app.db.base_class import Base


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
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user_uploads = relationship("UserUpload", back_populates="user")
    bots = association_proxy("bot_users", "bots")
    texts = relationship("Text", back_populates="user")
    embeddings = relationship("Embedding", back_populates="user")
    chats = relationship("Chat", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")

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
    def message_count(self):
        from app.services import StripeService
        if len(self.chats) == 0:
            return 0

        if not self.subscription_in_good_standing:
            return sum([len(i.user_messages) for i in self.chats])

        active_subscription = self.active_subscriptions()[0]
        session = object_session(self)

        if active_subscription.current_window_end_date is None or datetime.now(timezone.utc) > active_subscription.current_window_end_date:
            print("NO VALUE SET, QUERYING STRIPE")
            period_start, period_end = StripeService.get_user_current_window(
                active_subscription.stripe_subscription_id)

            active_subscription.current_window_start_date = period_start
            active_subscription.current_window_end_date = period_end
            session.commit()

        user_messages_in_period = sum([i.messages_in_period(
            active_subscription.current_window_start_date, active_subscription.current_window_end_date) for i in self.chats])

        return user_messages_in_period

    @property
    def bot_count(self):
        return len(self.bots)

    @property
    def file_count(self):
        return len(self.texts)

    ### Subscription Limiting Functions BEGIN

    @property
    def messages_left(self):
        return self.allowed_messages - self.message_count

    @property
    def files_left(self):
        return self.allowed_files - self.file_count

    @property
    def bots_left(self):
        return self.allowed_bots - self.bot_count
    
    ### Subscription Limiting Functions END

    @property
    def allowed_files(self):
        tier, recurring = self.subscription_tier
        if recurring == "annually":
            return tiers[tier]["files"] * 12
        return tiers[tier]["files"]


    @property
    def allowed_bots(self):
        tier, recurring = self.subscription_tier
        if recurring == "annually":
            return tiers[tier]["bots"] * 12
        return tiers[tier]["bots"]

    @property
    def allowed_messages(self):
        tier, recurring = self.subscription_tier
        if recurring == "annually":
            return tiers[tier]["messages"] * 12
        return tiers[tier]["messages"]

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
    def subscription_canceled(self):
        if len(self.active_subscriptions()) == 0:
            return False

        if self.active_subscriptions()[0].deleted_at:
            return True

        return False

    @property
    def subscription_tier(self):
        actives = self.active_subscriptions()
        if len(actives) == 0:
            return "FREE", "monthly"
        
        if self.subscription_in_good_standing:
            return "FREE", "monthly"

        sub = actives[0]

        name, recurring = sub.name.split("_")

        return name, recurring

    def active_subscriptions(self):
        active = [
            s for s in self.subscriptions if s.deleted_at is None or s.deleted_at <= datetime.now()]
        active.sort(key=lambda x: x.created_at, reverse=True)
        return active
