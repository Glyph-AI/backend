from app.models import Chat
from .user import UserFactory
from .bot import BotFactory
from .base import BaseFactory

class ChatFactory(BaseFactory):
    def create(self, name="test chat", user=None, bot=None):
        if user is None:
            user = UserFactory(self.db_session).create()
        
        if bot is None:
            bot = BotFactory(self.db_session).create()

        chat = Chat(
            user=user,
            bot=bot,
            name=name
        )

        self.db_session.add(chat)
        self.db_session.commit()
        self.db_session.refresh(chat)

        return chat