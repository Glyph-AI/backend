from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import ChatMessage
import app.schemas as schemas


def create_chat_message(db: Session, chat_message: schemas.ChatMessageCreateHidden):
    db_new_message = ChatMessage(**chat_message.dict())
    db.add(db_new_message)
    db.commit()
    db.refresh(db_new_message)

    return db_new_message
