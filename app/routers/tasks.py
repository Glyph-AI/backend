from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
import openai
import chardet
import json
import os
from app.services import S3Service, PdfProcessor, DocxProcessor, ImageProcessor, AudioProcessor
from app.models import UserUpload, Embedding, Text, ChatMessage, Embedding
from app.dependencies import get_db

environment = os.environ.get("ENVIRONMENT", "development")
openai.api_key = os.environ.get(
    "OPENAI_API_KEY", "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")


tasks_router = APIRouter(tags=["Background Tasks API"], prefix="/tasks")


class FileProcessSchema(BaseModel):
    user_upload_id: int
    chat_id: int


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


@tasks_router.post("/process_file")
def process_file(request: Request):
    task = json.loads(request.body().decode("utf-8"))
    user_upload_id = task.user_upload_id
    chat_id = task.chat_id
    # instantiate services
    print(f"--LOG: Starting Job on user_upload: {user_upload_id}")
    db = next(get_db())

    s3 = S3Service()
    user_upload = db.query(UserUpload).get(user_upload_id)
    # get the source file
    filename = user_upload.s3_link.split("/")[1]
    local_path = f"/temp/{filename}"
    db_message = ChatMessage(
        chat_id=chat_id,
        role="system",
        content=f"{filename} processing started",
        hidden=False
    )

    db.add(db_message)
    db.commit()
    s3.create_directory("/temp")
    s3.download_file(local_path, f"{user_upload.s3_link}")

    print(f"User Upload {user_upload_id}: Processing File to text")

    file_extension = get_file_extension(local_path)
    if file_extension == "pdf":
        processor = PdfProcessor()
        local_path = processor.process(local_path)
    elif file_extension in ["jpg", "png", "tiff"]:
        processor = ImageProcessor()
        local_path = processor.process(local_path)
    elif file_extension in ["docx"]:
        processor = DocxProcessor()
        local_path = processor.process(local_path)
    elif file_extension == "mp3":
        processor = AudioProcessor()
        local_path = processor.process(local_path)

    # All files are .txt for now, so nothing to do here. We'll need some logic to process files though
    # read source file
    f = open(local_path, "rb")
    contents = f.read()
    encoding = chardet.detect(contents)['encoding']
    decoded = contents.decode(encoding).replace("\x00", "\uFFFD")

    # create a Text object
    new_text = Text(
        name=filename,
        user_id=user_upload.user_id,
        user_upload_id=user_upload.id,
        content=decoded,
        text_type="file"
    )

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    print(f"User Upload {user_upload_id}: Embedding File")

    new_text.refresh_embeddings()

    print(
        f"User Upload {user_upload_id}: Processing Complete. Generating User Notification")

    user_upload.processed = True

    db_message = ChatMessage(
        chat_id=chat_id,
        role="system",
        content=f"{filename} processing complete",
        hidden=False
    )

    db.add(db_message)
    db.commit()

    return True
