from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import Chat, ChatMessage
import app.schemas as schemas


def get_chats(bot_id: int, db: Session, current_user: schemas.User):
    return db.query(Chat).filter(Chat.bot_id == bot_id, Chat.user_id == current_user.id).all()


def create_chat(chat_data: schemas.ChatBase, bot_id: int, db: Session, current_user: schemas.User):
    db_chat = Chat(**chat_data.dict())
    db_chat.user_id = current_user.id
    db_chat.bot_id = bot_id
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_chat_by_id(bot_id: int, chat_id: int, db: Session, current_user: schemas.User):
    return db.query(Chat).filter(Chat.user_id == current_user.id, Chat.id == chat_id, Chat.bot_id == bot_id).first()


def create_message(bot_id: int, chat_id: int, newMessage: schemas.ChatMessageCreate, db: Session, current_user: schemas.User):
    db_new_message = ChatMessage(**newMessage.dict())
    db.add(db_new_message)
    db.commit()
    db.refresh(db_new_message)

    return get_chat_by_id(bot_id, chat_id, db, current_user)
