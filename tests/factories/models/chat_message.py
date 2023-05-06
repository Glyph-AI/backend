from app.models import ChatMessage
from .chat import ChatFactory
from .base import BaseFactory
from datetime import datetime

class ChatMessageFactory(BaseFactory):
    def create(self, chat=None, role="user", content="Test Message", hidden=False, archived=False, created_at=datetime.now()):
        if chat is None:
            chat = ChatFactory(self.db_session).create()

        chat_message = ChatMessage(
            chat=chat,
            role=role,
            content=content,
            hidden=hidden,
            archived=archived,
            created_at=created_at
        )

        self.db_session.add(chat_message)
        self.db_session.commit()
        self.db_session.refresh(chat_message)

        return chat_message