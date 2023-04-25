from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import Bot
import app.schemas as schemas
from app.errors import Errors


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
