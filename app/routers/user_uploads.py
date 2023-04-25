from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
# from app.models import UserUpload
from app.schemas import User, ChatMessageCreateHidden, UserUpload
from app.crud import user_upload as user_upload_crud
from app.crud import chat_message as chat_message_crud
from app.worker import process_file

from app.errors import Errors

user_uploads_router = APIRouter(
    tags=["User Uploads API"], prefix="")

# ALLOWED_FILE_EXTENSIONS = ["txt"]


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


def process_file_upload(upload_file_record: UserUpload):
    pass


@user_uploads_router.post("/bots/{bot_id}/chats/{chat_id}/user_upload")
def upload_file(bot_id: int, chat_id: int, file: UploadFile, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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


@user_uploads_router.get("/user_uploads/", response_model=list[UserUpload])
def get_user_uploads(bot_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if bot_id:
        return user_upload_crud.get_user_uploads_by_bot_id(bot_id, db, current_user)

    return user_upload_crud.get_user_uploads(db, current_user)


@user_uploads_router.delete("/user_uploads/{id}", response_model=list[UserUpload])
def delete_user_upload(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_upload_crud.delete_user_upload(id, db, current_user)


@user_uploads_router.patch("/user_uploads/{id}", response_model=list[UserUpload])
def update_context_status(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return user_upload_crud.update_context_status(id, db, current_user)
