from app.models import BotTool
from .bot import BotFactory
from .user import UserFactory
from .base import BaseFactory

class BotToolFactory(BaseFactory):
    def create(self, bot=None, tool=None, enabled=False):
        if bot is None:
            bot = BotFactory(self.db_session).create()
        
        if tool is None:
            tool = ToolFactory(self.db_session).create()

        bot_tool = BotTool(
            bot=bot,
            tool=tool,
            enabled=enabled
        )

        self.db_session.add(bot_tool)
        self.db_session.commit()
        self.db_session.refresh(bot_tool)
        
        return bot_tool
        