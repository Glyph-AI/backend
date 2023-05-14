from fastapi import Depends, UploadFile
import os
from sqlalchemy.orm import Session
from app.models import User
from typing import Union
from app.services import S3Service
import app.schemas as schemas
from app.errors import Errors
import errno


def get_user_by_id(db: Session, current_user: schemas.User, id: int):
    return db.query(User).get(id)


def get_user_by_email(db: Session, email):
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_create_data: Union[schemas.UserCreateSSO, schemas.UserCreate]):
    db_user = User(**user_create_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(user_update_data: schemas.UserUpdate, db: Session, current_user: schemas.User):
    if user_update_data.id != current_user.id:
        raise Errors.credentials_error

    user = get_user_by_id(db, current_user, user_update_data.id)

    for key, value in user_update_data.dict(exclude_none=True).items():
        if key == "id":
            continue

        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def upload_profile_picture(file: UploadFile, db: Session, current_user: schemas.User):
    fileObject = file.file
    tmp_dir = f"/tmp/{file.filename}"

    try:
        os.makedirs("/tmp")
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir("/tmp"):
            pass
        else:
            raise e

    with open(tmp_dir, "wb+") as f:
        f.write(fileObject.read())

    # upload to storage
    bucket = os.getenv("PUBLIC_BUCKET", "public")
    store = os.getenv("STORE_URL")
    if os.getenv("ENVIRONMENT") == "development":
        store = "localhost:9000"
    s3 = S3Service(bucket)
    s3.upload_file(tmp_dir, file.filename)

    user = get_user_by_id(db, current_user, current_user.id)

    user.profile_picture_location = f"{store}/{bucket}/{file.filename}"
    db.commit()
    db.refresh(user)

    return user
