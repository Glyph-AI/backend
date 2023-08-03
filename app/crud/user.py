from fastapi import Depends, UploadFile
import os
from sqlalchemy.orm import Session
from app.models import User, Persona, BotText, BotTool, Tool
from typing import Union
from app.services import S3Service
import app.schemas as schemas
from app.errors import Errors
from .bot import create_bot
from .text import create_text
from .chat import create_chat
from app.templates import shopping_list_note

import errno


def get_user_by_id(db: Session, current_user: schemas.User, id: int):
    return db.query(User).get(id)


def get_user_by_email(db: Session, email):
    return db.query(User).filter(User.email == email).first()

def create_tutorial_setup(db, db_user):
    # create a new bot, a new note, and a new chat for this new user
    # create bot
    persona = db.query(Persona).filter(Persona.name == "Friendly Assistant").first()
    new_bot = schemas.BotCreate(name="Shopping List Bot", persona_id=persona.id)
    db_bot = create_bot(db, db_user, new_bot)
    # create note
    new_text = schemas.TextCreate(
        name="Shopping List",
        content=shopping_list_note,
        text_type="note"
    )
    db_text = create_text(new_text, db, db_user)
    db_text.embed()
    bt = BotText(text_id=db_text.id, bot_id=db_bot.id, include_in_context=True)
    db.add(bt)
    db.commit()

    ds_tool = db.query(Tool).filter(Tool.name == "Document Search").first()
    b_tool = BotTool(tool_id=ds_tool.id, bot_id=db_bot.id, enabled=True)
    db.add(b_tool)
    db.commit()
    # create chat
    new_chat = schemas.ChatCreate(name="Personal Chef", bot_id=db_bot.id)
    create_chat(new_chat, db, db_user)

    return True


def create_user(db: Session, user_create_data: Union[schemas.UserCreateSSO, schemas.UserCreate]):
    db_user = User(**user_create_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    create_tutorial_setup(db, db_user)

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
        store = "http://localhost:9000"
    s3 = S3Service(bucket)
    s3_path = f"{current_user.id}/{file.filename}"
    s3.upload_file(tmp_dir, s3_path)

    user = get_user_by_id(db, current_user, current_user.id)

    user.profile_picture_location = f"{store}/{bucket}/{user.id}/{file.filename}"
    db.commit()
    db.refresh(user)

    return user
