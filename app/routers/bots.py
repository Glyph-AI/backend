from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import User, Bot, BotCreate, BotBase, BotUpdate, BotSharingAdd
from app.crud import bot as bot_crud
from app.errors import Errors

bots_router = APIRouter(tags=["Bots API"], prefix="/bots")


@bots_router.get("", response_model=list[Bot])
async def get_user_bots(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return bot_crud.get_bots(db, current_user)


@bots_router.post("", response_model=Bot)
async def create_bot(bot_data: BotCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # block bot creation if not subscribed
    if not current_user.subscribed:
        raise Errors.subscription_error
    new_bot_data = bot_crud.create_bot(db, current_user, bot_data)
    return new_bot_data


@bots_router.post("/add-shared", response_model=Bot)
async def add_shared_bot(sharing_data: BotSharingAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return bot_crud.add_shared_bot(sharing_data, db, current_user)


@bots_router.get("/{bot_id}", response_model=Bot)
async def get_bot_by_id(bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return bot_crud.get_bot_by_id(bot_id, db, current_user)


@bots_router.patch("/{bot_id}", response_model=Bot)
async def update_bot(bot_id: int, bot_data: BotUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return bot_crud.update_bot_by_id(bot_id, bot_data, db, current_user)
