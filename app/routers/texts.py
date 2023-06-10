from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import Text, TextInfo, User, TextCreate
from app.crud import text as text_crud
from app.errors import Errors

texts_router = APIRouter(tags=["Texts API"], prefix="/texts")


@texts_router.get("", response_model=list[Text])
def get_texts(bot_id: int | None = None, text_type: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if bot_id:
        return text_crud.get_texts_by_bot_id(bot_id, db, current_user)

    if text_type:
        return text_crud.get_texts_by_text_type(text_type, db, current_user)

    return text_crud.get_texts(db, current_user)


@texts_router.post("", response_model=Text)
def create_text(text_data: TextCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return text_crud.create_text(text_data, db, current_user)


@texts_router.get("/{text_id}", response_model=Text)
def get_text_by_id(text_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return text_crud.get_text_by_id(text_id, db, current_user)


@texts_router.patch("/{text_id}", response_model=Text)
def update_text_by_id(text_id: int, text_data: TextCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return text_crud.update_text_by_id(text_id, text_data, db, current_user)


@texts_router.post("/{text_id}/embed")
def embed_text_by_id(text_id: int,  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return text_crud.embed_text_by_id(text_id, db, current_user)


@texts_router.delete("/{text_id}", response_model=list[Text])
def delete_text(text_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return text_crud.delete_text_by_id(text_id, db, current_user)


@texts_router.patch("/{text_id}/{bot_id}/status", response_model=list[Text])
def update_text_status_for_bot(text_id: int, bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return text_crud.update_text_status(text_id, bot_id, db, current_user)
