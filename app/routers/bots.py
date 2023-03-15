from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import User, Bot, BotCreate, BotBase
from app.crud import bot as bot_crud
from app.errors import Errors

bots_router = APIRouter(tags=["Bots API"], prefix="/bots")


@bots_router.get("/", response_model=list[BotBase])
async def get_user_bots(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bot_crud.get_bots(db, current_user)


@bots_router.post("/", response_model=BotBase)
async def create_bot(bot_data: BotCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    bot_crud.create_bot(db, current_user, bot_data)
