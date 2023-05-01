from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import GoogleAuthorizationCode, User
import app.crud.tool_authentication as tool_authentication_crud

tool_auth_router = APIRouter(
    tags=["Tool Authentication API"], prefix="/tools/auth")


@tool_auth_router.post("/google")
async def google_tool_auth(auth_data: GoogleAuthorizationCode, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tool_authentication_crud.create_tool_authentication(
        auth_data, db, current_user)

    return True
