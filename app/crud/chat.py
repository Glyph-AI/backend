from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy import and_
from app.models import Chat, ChatMessage, Bot, BotUser
from app.crud import chat_message as chat_message_crud
import app.schemas as schemas
from app.errors import Errors


def get_chats(db: Session, current_user: schemas.User):
    all_user_chats = db.query(Chat).filter(
        Chat.user_id == current_user.id, or_(Chat.deleted == None, Chat.deleted == False)).all()
    print(str(db.query(Chat).filter(
        Chat.user_id == current_user.id, or_(Chat.deleted == None, Chat.deleted == False))))
    # filter chats with bots that don't have sharing enabled
    user_owned = [
        i for i in all_user_chats if i.bot.creator_id == current_user.id]
    shared = [
        i for i in all_user_chats if i.bot.sharing_enabled and i.bot.creator_id != current_user.id]

    return user_owned + shared


def create_chat(chat_data: schemas.ChatBase, db: Session, current_user: schemas.User):
    db_chat = Chat(**chat_data.dict())
    db_chat.user_id = current_user.id
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    # add initial_message
    cm = schemas.ChatMessageCreateHidden(
        role="assistant", content=db_chat.bot.persona.initial_message, chat_id=db_chat.id, hidden=False)
    chat_message_crud.create_chat_message(db, current_user, cm)
    return db_chat

def delete_chat_by_id(chat_id: int, db: Session, current_user: schemas.User):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()

    if not chat:
        raise Errors.credentials_error
    
    chat.deleted = True
    db.commit()

    return True


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
