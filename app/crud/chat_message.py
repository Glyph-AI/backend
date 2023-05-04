from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import ChatMessage
import app.schemas as schemas
from app.errors import Errors


def create_chat_message(db: Session, current_user: schemas.User, chat_message: schemas.ChatMessageCreateHidden):
    if not current_user.can_create_messages:
        raise Errors.out_of_messages

    db_new_message = ChatMessage(**chat_message.dict())
    db.add(db_new_message)
    db.commit()
    db.refresh(db_new_message)

    return db_new_message
