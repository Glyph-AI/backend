from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_bot, get_current_user_public_api
from app.schemas import User, Bot, BotCreate, BotUpdate
import app.crud.bot as bot_crud
from app.errors import Errors

public_bots_router = APIRouter(tags=["Bots"], prefix="/bots")


@public_bots_router.get("", response_model=list[Bot])
async def get_user_bots(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    return bot_crud.get_bots(db, current_user)


@public_bots_router.post("", response_model=Bot)
async def create_bot(bot_data: BotCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    if current_user.bots_left == 0:
        raise Errors.out_of_bots

    return bot_crud.create_bot(db, current_user, bot_data)

@public_bots_router.patch("/{bot_id}")
async def update_bot(bot_data: BotUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_public_api)):
    
