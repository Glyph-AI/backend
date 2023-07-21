from sqlalchemy import String, Integer, DateTime, Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class UserDevice(Base):
    __tablename__ = "user_devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_token = Column(String, nullable=False)
    last_used = Column(DateTime)
    created_at = Column(DateTime(timezone=True),
                    server_default=func.now())

    user = relationship("User", back_populates="devices")