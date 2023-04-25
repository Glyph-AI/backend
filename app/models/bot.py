from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sharing_enabled = Column(Boolean, default=False)
    sharing_code = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    users = relationship(
        "User", secondary="bot_users", back_populates="bots")
    embeddings = relationship("Embedding", back_populates="bot")
    chats = relationship("Chat", back_populates="bot")
    user_uploads = relationship("UserUpload", back_populates="bot")
