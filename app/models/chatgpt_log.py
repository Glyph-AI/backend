from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ChatgptLog(Base):
    __tablename__ = "chatgpt_logs"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    text_id = Column(Integer, ForeignKey("texts.id"))
    message = Column(Text)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    chat = relationship("Chat", back_populates="chatgpt_logs")
    text = relationship("Text", back_populates="chatgpt_logs")
