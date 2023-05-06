from app.models import ChatMessage
from .chat import ChatFactory
from .base import BaseFactory

class ChatMessageFactory(BaseFactory):
    def create(self, chat=None, role="user", content="Test Message", hidden=False, archived=False):
        if chat is None:
            chat = ChatFactory(self.db_session).create()

        chat_message = ChatMessage(
            chat=chat,
            role=role,
            content=content,
            hidden=hidden,
            archived=archived
        )

        self.db_session.add(chat_message)
        self.db_session.commit()
        self.db_session.refresh(chat_message)

        return chat_message