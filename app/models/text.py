from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.session import object_session


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
    chatgpt_logs = relationship("ChatgptLog", back_populates="text")

    @hybrid_property
    def name(self):
        if self._name is not None:
            return self._name
        return self.user_upload.filename

    @name.setter
    def name(self, name_string):
        self._name = name_string

    @property
    def processed(self):
        if self.user_upload:
            return self.user_upload.processed

        return True

    def refresh_embeddings(self):
        session = object_session(self)
        self.embeddings = []
        session.commit()
        self.embed()

        return True

    def embed(self, chunk_size=2000, overlap=500):
        from app.services import OpenaiService
        from .embedding import Embedding
        session = object_session(self)
        openai = OpenaiService()
        chunks = [self.content[i:i + chunk_size]
                  for i in range(0, len(self.content), chunk_size-overlap)]

        for chunk in chunks:
            vector = openai.get_embedding(
                text=f"{self.name} | {chunk}")

            new_e = Embedding(
                text_id=self.id,
                user_id=self.user_id,
                vector=vector,
                content=chunk
            )

            session.add(new_e)

        session.commit()

        return True
