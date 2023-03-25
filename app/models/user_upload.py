from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class UserUpload(Base):
    __tablename__ = "user_uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    s3_link = Column(String, nullable=False)
    filename = Column(String)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", back_populates="user_uploads")
    texts = relationship("Text", back_populates="user_upload")
    bot = relationship("Bot", back_populates="user_uploads")
