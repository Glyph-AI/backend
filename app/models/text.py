from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm.session import object_session
from sqlalchemy.ext.associationproxy import association_proxy

from app.db.base_class import Base


class Text(Base):
    __tablename__ = "texts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_upload_id = Column(Integer, ForeignKey(
        "user_uploads.id"), nullable=True)
    content = Column(Text, nullable=False)
    text_type = Column(String, default="file") # file, note, chat_history
    history_chat_id = Column(Integer, ForeignKey("chats.id"))
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    user = relationship("User", back_populates="texts")
    user_upload = relationship("UserUpload", back_populates="texts")
    bots = association_proxy("bot_texts", "bots")
    related_chat = relationship("Chat", back_populates="texts", foreign_keys=[history_chat_id])
    embeddings = relationship("Embedding", back_populates="text")

    def refresh_embeddings(self):
        self.embeddings.delete()
        self.generate_embeddings()

    def generate_embeddings(self, chunk_size=2000, overlap=500):
        from app.services import OpenaiService
        from .embedding import Embedding
        openai = OpenaiService()
        session = object_session(self)
        # find existing embeddings and delete them

        chunks = [self.content[i:i + chunk_size] for i in range(0, len(self.content), chunk_size-overlap)]

        for chunk in chunks:
            vector = openai.get_embedding(chunk)
            new_e = Embedding(
                user_id=self.user_id,
                vector=vector,
                content=chunk
            )

            session.add(new_e)

        session.commit()

        return True