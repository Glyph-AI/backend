from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_bot, get_current_user_public_api
from app.schemas import Text, User, TextInfo, TextPublicCreate, TextCreate
import app.crud.text as text_crud
from app.errors import Errors

public_texts_router = APIRouter(tags=["Texts"], prefix="/text")


@public_texts_router.get("", response_model=list[TextInfo])
async def api_get_texts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    return text_crud.get_texts(db, current_user)


@public_texts_router.get("/{id}", response_model=Text)
async def api_get_text_by_id(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    return text_crud.get_text_by_id(id, db, current_user)


@public_texts_router.post("", response_model=Text)
async def api_create_text(text_data: TextPublicCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    if current_user.files_left == 0:
        raise Errors.out_of_files

    text_create = TextCreate(
        name=text_data.name, content=text_data.content, text_type="external")
    return text_crud.create_text(text_create, db, current_user)


@public_texts_router.patch("/{text_id}", response_model=Text)
async def update_text_by_id(text_id: int, text_data: TextPublicCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    text_create = TextCreate(
        name=text_data.name, content=text_data.content
    )

    return text_crud.update_text_by_id(text_id, text_create, db, current_user)


@public_texts_router.delete("/{text_id}", response_model=list[TextInfo])
async def delete_text_by_id(text_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    return text_crud.delete_text_by_id(text_id, db, current_user)


@public_texts_router.patch("/{text_id}/{bot_id}/status", response_model=list[TextInfo])
async def update_text_status_for_bot(text_id: int, bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    return text_crud.update_text_status_for_bot(text_id, bot_id, db, current_user)
