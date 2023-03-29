from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String, nullable=False)
    content = Column(String(12000), nullable=False)
    hidden = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    chat = relationship("Chat", back_populates="chat_messages")

    def format_gpt(self):
        return {
            "content": self.content,
            "role": self.role
        }

    def format_archive(self):
        return f"{self.role}: {self.content}"