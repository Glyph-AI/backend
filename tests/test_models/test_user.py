from tests.factories import *
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from app.services import StripeService

def create_user_with_subscription(db_session):
    user = UserFactory(db_session).create()
    pt = PriceTierFactory(db_session).create()
    sub = SubscriptionFactory(db_session).create(user=user, price_tier=pt)

    return user, pt, sub

def test_user_is_subscribed_and_current_should_return_in_good_standing(db_session):
    user, _, _ = create_user_with_subscription(db_session)

    assert user.subscription_in_good_standing == True

def test_user_is_subscribed_and_not_current_should_return_not_in_good_standing(db_session):
    user, _, _ = create_user_with_subscription(db_session)

    user.is_current = False
    db_session.commit()

    assert user.subscription_in_good_standing  == False

def test_user_is_not_subscribed_and_only_shows_50_messages(db_session):
    user = UserFactory(db_session).create()

    assert user.messages_left == 50
    assert user.allowed_messages == 50

def test_user_is_not_subscribed_shows_only_2_bots(db_session):
    user = UserFactory(db_session).create()

    assert user.bots_left == 2
    assert user.allowed_bots == 2
    assert len(user.bots) == 0

def test_user_is_not_subscribed_shows_only_2_files(db_session):
    user = UserFactory(db_session).create()

    assert user.files_left == 2
    assert user.allowed_files == 2
    assert len(user.user_uploads) == 0

def test_user_is_not_subscribed_with_1_bot_shows_only_1_bot(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert user.bots_left == 1
    assert user.allowed_bots == 2
    assert len(user.bots) == 1

def test_user_is_not_subscribed_with_1_bot_and_1_file_and_shows_only_1_file(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)
    UserUploadFactory(db_session).create(user=user, bot=bot)

    assert user.files_left == 1
    assert user.allowed_files == 2
    assert len(user.user_uploads) == 1

def test_user_is_not_subscribed_with_1_message_and_shows_only_1_message(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)
    ChatMessageFactory(db_session).create(chat=chat)

    assert user.messages_left == 49
    assert user.allowed_messages == 50

def test_user_is_not_subscribed_with_1_message_and_subscribing_updates_messages_left(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)
    ChatMessageFactory(db_session).create(chat=chat)

    assert user.messages_left == 49
    assert user.allowed_messages == 50

    StripeService.get_user_current_window = MagicMock(return_value=(datetime.now() - timedelta(days=30), datetime.now()))
    SubscriptionFactory(db_session).create(user=user)
    user.is_current = True
    db_session.commit()

    assert user.messages_left == 749
    assert user.allowed_messages == 750

def test_user_is_not_subscribed_with_1_bot_and_subscribing_updates_bots_let(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert user.bots_left == 1
    assert user.allowed_bots == 2
    assert len(user.bots) == 1

    SubscriptionFactory(db_session).create(user=user)
    user.is_current = True
    db_session.commit()

    assert user.bots_left == -1
    assert user.allowed_bots == -1
    assert len(user.bots) == 1

def test_user_adding_message_update_message_count(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)
    ChatMessageFactory(db_session).create(chat=chat)

    assert user.messages_left == 49
    assert user.allowed_messages == 50

    for i in range(9):
        ChatMessageFactory(db_session).create(chat=chat)
    
    assert user.messages_left == 40
    assert user.allowed_messages == 50

def test_user_adding_bots_updates_bot_count(db_session):
    user = UserFactory(db_session).create()

    assert user.bots_left == 2
    assert user.allowed_bots == 2

    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert user.bots_left == 1
    assert user.allowed_bots == 2

def test_user_adding_file_updates_file_count(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert user.files_left == 2
    assert user.allowed_files == 2
    assert len(user.user_uploads) == 0


    UserUploadFactory(db_session).create(user=user, bot=bot)

    assert user.files_left == 1
    assert user.allowed_files == 2
    assert len(user.user_uploads) == 1

def test_user_is_allowed_to_create_bots_if_they_have_bots_left(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert user.can_create_bots == True

def test_user_is_allowerd_to_create_messages_if_they_have_messages_left(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)
    ChatMessageFactory(db_session).create(chat=chat)

    assert user.can_create_messages == True


def test_user_is_allowed_to_create_files_if_they_have_files_left(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert user.can_create_files == True

def test_user_cannot_create_bots_if_they_have_none_left(db_session):
    user = UserFactory(db_session).create()

    for i in range(2):
        bot = BotFactory(db_session).create()
        BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    assert user.can_create_bots == False


def test_user_cannot_create_messages_if_they_have_none_left(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    chat = ChatFactory(db_session).create(user=user, bot=bot)

    for i in range(50):
        ChatMessageFactory(db_session).create(chat=chat)

    assert user.can_create_messages == False


def test_user_cannot_create_files_if_they_have_none_left(db_session):
    user = UserFactory(db_session).create()
    bot = BotFactory(db_session).create()
    BotUserFactory(db_session).create(user=user, bot=bot, creator=True)

    for i in range(2):
        UserUploadFactory(db_session).create(user=user, bot=bot)

    assert user.can_create_files == False