from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
import bcrypt

from app.db.base_class import Base

FREEMIUM_BOTS = 2
FREEMIUM_MESSAGES = 50
FREEMIUM_FILES = 2
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
    def bots_left(self):
        if self.subscribed:
            return -1

        return FREEMIUM_BOTS - len(self.bots)

    @property
    def messages_left(self):
        from app.services import StripeService
        if not self.subscribed:
            return FREEMIUM_MESSAGES - sum([len(i.user_messages) for i in self.chats])

        active_subscription = self.active_subscriptions[0]
        active_subscription_id = self.active_subscriptions()[
            0].stripe_subscription_id
        period_start, period_end = StripeService.get_user_current_window(
            active_subscription_id)
        user_messages_in_period = len([i.messages_in_period(
            period_start, period_end) for i in self.chats])

        if active_subscription.price_tier.name == "Annual":
            return ANNUAL_SUBSCRIPTION_MESSAGES - user_messages_in_period

        return SUBSCRIPTION_MESSAGES - user_messages_in_period

    @property
    def files_left(self):
        if not self.subscribed:
            return FREEMIUM_FILES - len(self.user_uploads)

        return -1

    @property
    def allowed_files(self):
        if self.subscribed:
            return -1

        return FREEMIUM_FILES

    @property
    def allowed_bots(self):
        if self.subscribed:
            return -1

        return FREEMIUM_BOTS

    @property
    def allowed_messages(self):
        if self.subscribed:
            return SUBSCRIPTION_MESSAGES

        return FREEMIUM_MESSAGES

    @property
    def can_create_messages(self):
        return self.messages_left > 0

    @property
    def can_create_bots(self):
        return self.subscribed or self.bots_left > 0

    @property
    def can_create_files(self):
        return self.subscribed or self.files_left > 0

    def active_subscriptions(self):
        return [s for s in self.subscriptions if s.deleted_at == None]
