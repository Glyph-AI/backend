from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql import func
from app.db.base_class import Base


class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sharing_enabled = Column(Boolean, default=False)
    sharing_code = Column(String, unique=True)
    persona_id = Column(Integer, ForeignKey("personas.id"))
    avatar_location = Column(String)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())

    users = association_proxy("bot_users", "users")
    tools = association_proxy("bot_tools", "tools")
    texts = association_proxy("bot_texts", "texts")
    embeddings = relationship("Embedding", back_populates="bot")
    chats = relationship("Chat", back_populates="bot")
    persona = relationship("Persona", back_populates="bots")

    @property
    def users(self):
        bot_users = self.bot_users
        return [i.user for i in bot_users]

    @property
    def enabled_tools(self):
        return [t.tool for t in self.bot_tools if t.enabled]

    @property
    def enabled_texts(self):
        return [t.text for t in self.bot_texts if t.include_in_context]

    @property
    def creator_id(self):
        bot_users = self.bot_users
        creating_user = [i for i in bot_users if i.creator == True]
        if creating_user == []:
            return None

        return creating_user[0].user_id
