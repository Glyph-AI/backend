from sqlalchemy.orm import Session
from app.models import Text
import app.schemas as schemas
from app.errors import Errors

def user_texts(db, current_user):
    return db.query(Text).filter(Text.user_id == current_user.id)

def get_texts(db: Session, current_user: schemas.User):
    return user_texts(db, current_user)

def create_text(text_data: schemas.TextCreate, db: Session, current_user: schemas.User):
    new_text = Text(
        user=current_user,
        content=text_data.content,
        name=text_data.name,
        text_type=text_data.text_type
    )

    db.add(new_text)
    db.commit()
    db.refresh()

    return new_text

def get_text_by_id(text_id: int, db: Session, current_user: schemas.User):
    text = user_texts(db, current_user).filter(Text.id == text_id).first()

    if text is None:
        raise Errors.credentials_error
    
    return text

def update_text_by_id(text_id: int, text_data: schemas.TextCreate, db: Session, current_user: schemas.User):
    text = user_texts(db, current_user).filter(Text.id == text_id).first()

    if text is None:
        raise Errors.credentials_error
    
    for key, value in text_data.dict(exclude_none=True).items():
        setattr(text, key, value)

    db.commit()
    db.refresh()

    return text

def delete_text_by_id(text_id: int, db: Session, current_user: schemas.User):
    text = user_texts(db, current_user).filter(Text.id == text_id)

    if text is None:
        raise Errors.credentials_error

    db.delete(text)
    db.commit()

    return get_texts(db, current_user)