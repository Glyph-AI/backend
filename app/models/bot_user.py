from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class BotUser(Base):
    __tablename__ = "bot_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    bot_id = Column(Integer, ForeignKey("bots.id"))
    creator = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", backref="bot_users")
    bot = relationship("Bot", backref="bot_users")

    __table_args__ = (
        Index('index_bot_users_on_user_id', user_id),
        Index('index_bot_users_on_bot_id', bot_id)
    )
