from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import Bot
import app.schemas as schemas
from app.errors import Errors
import random
import string


def get_bots(db: Session, current_user: schemas.User):
    return db.query(Bot).filter(Bot.user_id == current_user.id).all()


def create_bot(db: Session, current_user: schemas.User, bot_data: schemas.BotBase):
    db_bot = Bot(**bot_data.dict())
    db_bot.user_id = current_user.id
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot


def get_bot_by_id(bot_id: int, db: Session, current_user: schemas.User):
    bot = db.query(Bot).get(bot_id)
    if bot.user_id != current_user.id:
        raise Errors.credentials_error

    return bot


def update_bot_by_id(bot_id: int, bot_data: schemas.BotUpdate, db: Session, current_user: schemas.User):
    bot = db.query(Bot).get(bot_id)
    if bot.user_id != current_user.id:
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
