from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy import and_
from app.models import Chat, ChatMessage, Bot, BotUser
import app.schemas as schemas


def get_chats(db: Session, current_user: schemas.User):
    return db.query(Chat).join(Bot).join(BotUser).filter(Chat.user_id == current_user.id, or_(BotUser.creator == True, Bot.sharing_enabled == True)).all()


def create_chat(chat_data: schemas.ChatBase, db: Session, current_user: schemas.User):
    db_chat = Chat(**chat_data.dict())
    db_chat.user_id = current_user.id
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_chat_by_id(chat_id: int, db: Session, current_user: schemas.User):
    output = db.query(Chat).filter(Chat.user_id == current_user.id,
                                   Chat.id == chat_id)
    return output.first()


def create_message(chat_id: int, newMessage: schemas.ChatMessageCreate, db: Session, current_user: schemas.User):
    db_new_message = ChatMessage(**newMessage.dict())
    db.add(db_new_message)
    db.commit()
    db.refresh(db_new_message)

    return get_chat_by_id(chat_id, db, current_user)
