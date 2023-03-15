from fastapi import Depends
from sqlalchemy.orm import Session
from app.models import User
import app.schemas as schemas


def get_user_by_id(db: Session, current_user: schemas.User, id: int):
    db.query(User).get(int)


def create_user(db: Session, user_create_data: schemas.UserCreateSSO):
    db_user = User(**user_create_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
