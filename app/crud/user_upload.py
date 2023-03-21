from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models import UserUpload
import app.schemas as schemas
from app.services import S3Service


def create_user_upload(bot_id: int, db: Session, current_user: schemas.User, file: UploadFile):
    s3 = S3Service()
    s3.create_directory("/temp")
    file_object = file.file
    with open(f"/temp/{file.filename}", "wb") as f:
        f.write(file_object.read())

    s3.upload_file(f"/temp/{file.filename}",
                   f"{current_user.id}/{file.filename}")
    s3.remove_local_file(f"/temp/{file.filename}")

    db_user_upload = UserUpload(
        user_id=current_user.id,
        s3_link=f"{current_user.id}/{file.filename}",
        bot_id=bot_id,
    )
    db.add(db_user_upload)
    db.commit()
    db.refresh(db_user_upload)

    return db_user_upload
