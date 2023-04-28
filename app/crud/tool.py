from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Tool
import app.schemas as schemas
from app.errors import Errors


def get_tools(db: Session, current_user: schemas.User):
    return db.query(Tool).all()
