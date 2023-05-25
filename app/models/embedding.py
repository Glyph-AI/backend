from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.base_class import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    text_id = Column(Integer, ForeignKey("texts.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vector = Column(Vector(768))
    content = Column(String(4000), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    bot = relationship("Bot", back_populates="embeddings")
    text = relationship("Text", back_populates="embeddings")
    user = relationship("User", back_populates="embeddings")
