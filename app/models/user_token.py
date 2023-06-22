from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import timedelta, datetime
from sqlalchemy.orm.session import object_session
import bcrypt

from app.db.base_class import Base


class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    _token = Column(String, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", back_populates="user_tokens")

    @hybrid_property
    def token(self):
        self._token

    @token.setter
    def token(self, plaintext):
        self._token = bcrypt.hashpw(plaintext.encode(
            "utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_token(self, plaintext):
        return bcrypt.checkpw(plaintext.encode("utf-8"), self._token.encode("utf-8"))
