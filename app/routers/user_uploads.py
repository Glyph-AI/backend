from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import User

from app.errors import Errors

user_uploads_router = APIRouter(
    tags=["User Uploads API"], prefix="/bots/{bot_id}/user_upload")


@user_uploads_router.post("/")
def upload_file(bot_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # upload file
    # process to embeddings (maybe a background process)

    pass
