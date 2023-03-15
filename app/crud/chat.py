from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import Chat
import app.schemas as schemas


def get_chats(bot_id: int, db: Session, current_user: schemas.User):
    return db.query(Chat).filter(Chat.bot_id == bot_id, Chat.user_id == current_user.id).all()


def create_chat(chat_data: schemas.ChatBase, bot_id: int, db: Session, current_user: schemas.User):
    db_chat = Chat(**chat_data.dict())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat
