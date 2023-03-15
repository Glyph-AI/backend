from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
# from app.schemas import

from app.errors import Errors

bots_router = APIRouter(tags=["Bots API"], prefix="/users/{user_id}/bots")


@bots_router.get("/")
async def get_user_bots(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass


@bots_router.post("/")
async def create_bot(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass
