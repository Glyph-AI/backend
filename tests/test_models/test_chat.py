from tests.factories import *
from datetime import datetime, timedelta

def test_chat_can_count_the_messages_in_a_given_period(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)
    messages_in_period = 3
    create_date = datetime.now() - timedelta(days=1)
    period_start = datetime.now() - timedelta(days=30)
    period_end = datetime.now()
    # create three chat message in period
    for i in range(messages_in_period):
        ChatMessageFactory(db_session).create(chat=chat, created_at=create_date)
    
    assert chat.messages_in_period(period_start, period_end) == messages_in_period

def test_chat_does_not_count_message_outside_of_the_period(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)
    messages_in_period = 3
    create_date = datetime.now() - timedelta(days=60)
    period_start = datetime.now() - timedelta(days=30)
    period_end = datetime.now()
    # create three chat message in period
    for i in range(messages_in_period):
        ChatMessageFactory(db_session).create(chat=chat, created_at=create_date)

    print([i.created_at for i in chat.chat_messages])
    
    assert chat.messages_in_period(period_start, period_end) != messages_in_period
    assert chat.messages_in_period(period_start, period_end) == 0

def test_chat_can_properly_count_user_messages(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)

    ChatMessageFactory(db_session).create(chat=chat, role="system")
    ChatMessageFactory(db_session).create(chat=chat, role="user")

    assert chat.user_message_count == 1

def test_chat_can_return_user_messages(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)

    ChatMessageFactory(db_session).create(chat=chat, role="system")
    user_message = ChatMessageFactory(db_session).create(chat=chat, role="user")

    assert len(chat.user_messages) == 1
    assert chat.user_messages[0].id == user_message.id