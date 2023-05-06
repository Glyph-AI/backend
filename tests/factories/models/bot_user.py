from app.models import BotUser
from .bot import BotFactory
from .user import UserFactory
from .base import BaseFactory

class BotUserFactory(BaseFactory):
    def create(self, user=None, bot=None, creator=False):
        if user is None:
            user = UserFactory(self.db_session).create()

        if bot is None:
            bot = BotFactory(self.db_session).create()

        bot_user = BotUser(user=user, bot=bot, creator=creator)

        self.db_session.add(bot_user)
        self.db_session.commit()
        self.db_session.refresh(bot_user)

        return bot_user