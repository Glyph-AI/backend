from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import Tool, User
from app.crud import tool as tool_crud
from app.errors import Errors

tools_router = APIRouter(tags=["Tools API"], prefix="/tools")


@tools_router.get("", response_model=list[Tool])
async def get_tools(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return tool_crud.get_tools(db, current_user)
