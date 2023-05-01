from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Bot, BotUser, Tool, BotTool
import app.schemas as schemas
from app.errors import Errors

import random
import string


def filter_bots(db: Session, current_user: schemas.User):
    return db.query(Bot).join(BotUser).filter(BotUser.user_id == current_user.id, or_(BotUser.creator == True, Bot.sharing_enabled == True))


def get_bots(db: Session, current_user: schemas.User):
    return filter_bots(db, current_user).all()


def create_bot(db: Session, current_user: schemas.User, bot_data: schemas.BotBase):
    db_bot = Bot(**bot_data.dict())
    db.add(db_bot)
    db.commit()
    db_bot_user = BotUser(user_id=current_user.id,
                          bot_id=db_bot.id, creator=True)
    db.add(db_bot_user)
    db.commit()
    db.refresh(db_bot)
    # add respond_to_user tool
    ru_tool = db.query(Tool).filter(Tool.name == "Respond to User").first()
    db_bot_tool = BotTool(tool_id=ru_tool.id, bot_id=db_bot.id, enabled=True)
    db.add(db_bot_tool)
    db.commit()
    db.refresh(db_bot)
    return db_bot


def get_bot_by_id(bot_id: int, db: Session, current_user: schemas.User):
    bot = filter_bots(db, current_user).filter(Bot.id == bot_id).one_or_none()
    if bot is None:
        raise Errors.credentials_error

    return bot


def update_bot_by_id(bot_id: int, bot_data: schemas.BotUpdate, db: Session, current_user: schemas.User):
    bot = filter_bots(db, current_user).filter(Bot.id == bot_id).one_or_none()
    if bot is None:
        raise Errors.credentials_error

    for key, value in bot_data.dict(exclude_none=True).items():
        setattr(bot, key, value)

        if key == "sharing_enabled" and bot.sharing_code is None:
            # generate a sharing_code if we don't have one
            code_exists = True
            code = None
            while (code_exists):
                code = ''.join(random.choice(
                    string.ascii_uppercase + string.digits) for _ in range(8))
                # check if sharing code exists
                code_exists = len(db.query(Bot).filter(
                    Bot.sharing_code == code).all()) > 0

            bot.sharing_code = code

    db.commit()
    db.refresh(bot)

    return bot


def add_shared_bot(sharing_data: schemas.BotSharingAdd, db: Session, current_user: schemas.User):
    sharing_code = sharing_data.sharing_code
    # get bot for given code
    bot = db.query(Bot).filter(Bot.sharing_code == sharing_code).first()
    if not bot.sharing_enabled:
        raise Errors.credentials_error

    # create a bot_user
    db_bot_user = BotUser(user_id=current_user.id,
                          bot_id=bot.id)
    db.add(db_bot_user)
    db.commit()
    db.commit()
    db.refresh(bot)
    return bot


def change_tool_status(bot_id: int, tool_id: int, db: Session, current_user: schemas.User):
    bot = filter_bots(db, current_user).filter(Bot.id == bot_id).one_or_none()
    if bot is None:
        raise Errors.credentials_error

    tool = db.query(Tool).get(tool_id)
    bot_tool = db.query(BotTool).filter(BotTool.tool_id ==
                                        tool_id, BotTool.bot_id == bot_id).one_or_none()
    if bot_tool is None:
        # create and enable bot_tool
        new_bt = BotTool(bot_id=bot_id, tool_id=tool_id, enabled=True)
        db.add(new_bt)
        db.commit()

    else:
        bot_tool.enabled = not bot_tool.enabled
        db.commit()

    db.refresh(bot)
    return bot
