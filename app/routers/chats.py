from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
# from app.schemas import

from app.errors import Errors

chats_router = APIRouter(Tags=["Chats API"], prefix="/users/{user_id}/chats")


@chats_router.get("/", response_model=list[Chat])
def get_chats_by_user_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass


@chats_router.post("/", response_model=Chat)
def create_chat(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass


@chats_router.post("/message", response_model=Chat)
def send_message(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass
