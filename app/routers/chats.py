from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import ChatBase, Chat, User
from app.crud import chat as chat_crud

from app.errors import Errors

chats_router = APIRouter(tags=["Chats API"], prefix="/bots/{bot_id}/chats")


@chats_router.get("/", response_model=list[Chat])
def get_chats_by_user_id(bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat_crud.get_chats(bot_id, db, current_user)


@chats_router.post("/", response_model=Chat)
def create_chat(chat_data: ChatBase, bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    chat_crud.create_chat(chat_data, bot_id, db, current_user)


@chats_router.post("/{chat_id}/message", response_model=Chat)
def send_message(bot_id: int, chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass
