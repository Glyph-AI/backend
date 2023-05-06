from app.models import Bot
from .persona import PersonaFactory
from .base import BaseFactory

class BotFactory(BaseFactory):
    def create(self, name="Test Bot", sharing_enabled=False, sharing_code=None, persona=None):
        if persona is None:
            persona = PersonaFactory(self.db_session).create()

        bot = Bot(
            name=name,
            sharing_enabled=sharing_enabled,
            persona=persona,
            sharing_code=sharing_code
        )

        self.db_session.add(bot)
        self.db_session.commit()
        self.db_session.refresh(bot)

        return bot
