from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
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
    bots = relationship(
        "Bot", secondary="bot_users", back_populates="users")
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

    def active_subscriptions(self):
        return [s for s in self.subscriptions if s.deleted_at == None]
