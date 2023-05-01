from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import importlib


class ToolAuthentication(Base):
    __tablename__ = "tool_authentications"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    tool_id = Column(Integer, ForeignKey("tools.id"))
    authorization_code = Column(String)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", back_populates="tool_authentications")
    tool = relationship("Tool", back_populates="tool_authentications")
    bot = relationship("Bot", back_populates='tool_authentications')
