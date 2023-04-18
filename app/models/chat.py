from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import timedelta, datetime
import os
from jose import jwt

from app.db.base_class import Base

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
ALGORITHM = "HS256"


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    bot_id = Column(Integer, ForeignKey("bots.id"))
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", back_populates="chats")
    bot = relationship("Bot", back_populates="chats")
    chat_messages = relationship("ChatMessage", back_populates="chat")
    chatgpt_logs = relationship("ChatgptLog", back_populates="chat")

    @property
    def chat_token(self):
        to_encode = {"sub": f"{self.user.email}|{self.id}"}
        expires_delta = timedelta(minutes=100000)

        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
