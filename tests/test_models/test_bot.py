from tests.factories import *

def test_bot_can_return_creator_id(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert bot.creator_id == user.id

def test_bot_does_not_return_noncreators_as_creator(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=False)

    assert bot.creator_id == None

def test_bot_returns_its_enabled_tools(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    tool = ToolFactory(db_session).create()
    bot_tool = BotToolFactory(db_session).create(bot=bot, tool=tool, enabled=True)

    assert len(bot.enabled_tools) == 1
    assert bot.enabled_tools[0].name == tool.name

def test_bot_does_not_return_disabled_tools(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    tool = ToolFactory(db_session).create()
    bot_tool = BotToolFactory(db_session).create(bot=bot, tool=tool, enabled=False)

    assert len(bot.enabled_tools) == 0