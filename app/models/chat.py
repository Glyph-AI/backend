from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import timedelta, datetime
from sqlalchemy.orm.session import object_session

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
    chat_messages = relationship(
        "ChatMessage", back_populates="chat")
    chatgpt_logs = relationship("ChatgptLog", back_populates="chat")
    texts = relationship("Text", back_populates="related_chat")

    @property
    def user_messages(self):
        return [i for i in self.chat_messages if i.role == "user"]

    @property
    def user_message_count(self):
        return len(self.user_messages)

    def messages_in_period(self, period_start, period_end):
        from .chat_message import ChatMessage
        session = object_session(self)
        query = session.query(ChatMessage).filter(ChatMessage.created_at < period_end, ChatMessage.created_at >
                                                  period_start, ChatMessage.role == "user", ChatMessage.chat_id == self.id)
        return query.count()

    @property
    def chat_token(self):
        to_encode = {"sub": f"{self.user.email}|{self.id}"}
        expires_delta = timedelta(minutes=100000)

        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
