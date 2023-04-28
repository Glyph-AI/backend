from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    initial_message = Column(String)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    bots = relationship("Bot", back_populates="persona")
