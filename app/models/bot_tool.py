from sqlalchemy import Boolean, Column, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class BotTool(Base):
    __tablename__ = "bot_tools"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), index=True)
    tool_id = Column(Integer, ForeignKey("tools.id"), index=True)
    enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    bot = relationship("Bot", backref="bot_tools")
    tool = relationship("Tool", backref="bot_tools")
