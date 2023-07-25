from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    hidden = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    tts = Column(Boolean, default=False)
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

    def format_for_prompt(self):
        if self.role == "assistant":
            return f"Glyph: {self.content}"
        elif self.role == "user":
            return f"User: {self.content}"
        else:
            return f"System: {self.content}"
