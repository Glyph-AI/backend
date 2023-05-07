from sqlalchemy import Column, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class BotText(Base):
    __tablename__ = "bot_texts"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    text_id = Column(Integer, ForeignKey("texts.id"))
    include_in_context = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())
    
    bot = relationship("Bot", backref="bot_texts")
    text = relationship("Text", backref="bot_texts")