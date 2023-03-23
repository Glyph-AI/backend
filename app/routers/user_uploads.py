from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models import UserUpload
from app.schemas import User, ChatMessageCreateHidden
from app.crud import user_upload as user_upload_crud
from app.crud import chat_message as chat_message_crud
from app.worker import process_file

from app.errors import Errors

user_uploads_router = APIRouter(
    tags=["User Uploads API"], prefix="/bots/{bot_id}/chats/{chat_id}/user_upload")

# ALLOWED_FILE_EXTENSIONS = ["txt"]


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def process_file_upload(upload_file_record: UserUpload):
    pass


@user_uploads_router.post("/")
def upload_file(bot_id: int, chat_id: int, file: UploadFile,  background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file_extension = get_file_extension(file.filename)
    # if file_extension not in ALLOWED_FILE_EXTENSIONS:
    #     raise Errors.invalid_file_type

    # create a upload file record
    upload_file_record = user_upload_crud.create_user_upload(
        bot_id, db, current_user, file)
    
    # create message for upload
    upload_message = ChatMessageCreateHidden(
        role="system",
        content=f"{file.filename} uploaded",
        chat_id=chat_id,
        hidden=False
    )

    chat_message_crud.create_chat_message(db, upload_message)

    # process to embeddings (maybe a background process)
    task = process_file.delay(upload_file_record.id, chat_id)

    return JSONResponse({"task_id": task.id})
