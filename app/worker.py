from celery import Celery
import openai
import chardet
import os
from app.models import UserUpload, Embedding, Text
from app.dependencies import get_db
from app.services import S3Service

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://redis:6379")

environment = os.environ.get("ENVIRONMENT", "development")
openai.api_key = os.environ.get(
    "OPENAI_KEY", "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")


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()


@celery.task(name="process_file")
def process_file(user_upload_id):
    # instantiate services
    db = next(get_db())
    s3 = S3Service()
    user_upload = db.query(UserUpload).get(user_upload_id)
    # get the source file
    filename = user_upload.s3_link.split("/")[1]
    local_path = f"/temp/{filename}"
    s3.create_directory("/temp")
    s3.download_file(local_path, f"{user_upload.s3_link}")

    file_extension = get_file_extension(local_path)

    # All files are .txt for now, so nothing to do here. We'll need some logic to process files though
    # read source file
    f = open(local_path, "rb")
    contents = f.read()
    encoding = chardet.detect(contents)['encoding']
    decoded = contents.decode(encoding)

    # create a Text object
    new_text = Text(
        user_id=user_upload.user_id,
        user_upload_id=user_upload.id,
        content=decoded
    )

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    chunk_size = 2000
    overlap = 500
    chunks = [decoded[i:i + chunk_size]
              for i in range(0, len(decoded), chunk_size-overlap)]

    # create an embedding for each chunk
    for chunk in chunks:
        vector = openai.Embedding.create(
            input=f"{filename} | {chunk}", model="text-embedding-ada-002")['data'][0]['embedding']
        new_e = Embedding(
            bot_id=user_upload.bot_id,
            text_id=new_text.id,
            user_id=user_upload.user_id,
            vector=vector,
            content=chunk
        )

        db.add(new_e)

    db.commit()

    return True
