from sqlalchemy.orm import Session
from app.models import Text, BotText
import app.schemas as schemas
from app.errors import Errors
from datetime import datetime
from sqlalchemy import or_


def user_texts(db, current_user):
    return db.query(Text).filter(Text.user_id == current_user.id, or_(Text.deleted == None, Text.deleted == False), or_(Text.text_type == "file", Text.text_type == "note"))


def get_texts(db: Session, current_user: schemas.User):
    return user_texts(db, current_user).all()


def get_texts_by_bot_id(bot_id: int, db: Session, current_user: schemas.User):
    return user_texts(db, current_user).join(BotText).filter(BotText.bot_id == bot_id, BotText.include_in_context == True).all()


def get_texts_by_text_type(text_type: str, db: Session, current_user: schemas.User):
    return user_texts(db, current_user).filter(Text.text_type == text_type).all()


def create_text(text_data: schemas.TextCreate, db: Session, current_user: schemas.User):
    new_text = Text(
        user=current_user,
        content=text_data.content,
        name=text_data.name,
        text_type=text_data.text_type
    )

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    return new_text


def get_text_by_id(text_id: int, db: Session, current_user: schemas.User):
    text = user_texts(db, current_user).filter(Text.id == text_id).first()

    if text is None:
        raise Errors.credentials_error

    return text


def embed_text_by_id(text_id: int, db: Session, current_user: schemas.User):
    text = user_texts(db, current_user).filter(Text.id == text_id).first()

    if text is None:
        raise Errors.credentials_error

    text.refresh_embeddings()

    return True


def update_text_by_id(text_id: int, text_data: schemas.TextCreate, db: Session, current_user: schemas.User):
    text = user_texts(db, current_user).filter(Text.id == text_id).first()

    if text is None:
        raise Errors.credentials_error

    for key, value in text_data.dict(exclude_none=True).items():
        setattr(text, key, value)

    db.commit()
    db.refresh(text)

    return text


def delete_text_by_id(text_id: int, db: Session, current_user: schemas.User):
    text = user_texts(db, current_user).filter(
        Text.id == text_id).one_or_none()

    if text is None:
        raise Errors.credentials_error

    text.deleted = True
    text.deleted_at = datetime.now()
    print(text.deleted, text.deleted_at)
    db.commit()

    return get_texts(db, current_user)
