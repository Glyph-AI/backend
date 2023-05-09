from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property


from app.db.base_class import Base


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_upload_id = Column(Integer, ForeignKey(
        "user_uploads.id"), nullable=True)
    _name = Column(String)
    text_type = Column(String, default="file")  # file, note, chat_history
    content = Column(Text, nullable=False)
    deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", back_populates="texts")
    bots = association_proxy("bot_texts", "bots")
    embeddings = relationship("Embedding", back_populates="text")
    user_upload = relationship("UserUpload", back_populates="text")

    @hybrid_property
    def name(self):
        if self._name is not None:
            return self._name
        return self.user_upload.filename

    @name.setter
    def name(self, name_string):
        self._name = name_string
