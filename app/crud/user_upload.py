from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import UserUpload, Embedding, Text
import app.schemas as schemas
from app.services import S3Service
from app.errors import Errors
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment



def get_user_uploads(db: Session, current_user: schemas.User):
    return db.query(UserUpload).filter(UserUpload.user_id == current_user.id, or_(UserUpload.deleted == None, UserUpload.deleted == False)).all()


def get_user_uploads_by_bot_id(bot_id: int, db: Session, current_user: schemas.User):
    return db.query(UserUpload).filter(UserUpload.user_id == current_user.id, UserUpload.bot_id == bot_id).filter(or_(UserUpload.deleted == None, UserUpload.deleted == False)).all()


def delete_user_upload(id: int, db: Session, current_user: schemas.User):
    uu = db.query(UserUpload).get(id)
    if uu.user_id != current_user.id:
        raise Errors.credentials_error
    # get texts
    text_ids = [i.id for i in db.query(Text).filter(
        Text.user_upload_id == id).all()]
    # get and delete embeddings
    db.query(Embedding).filter(Embedding.text_id.in_(text_ids)).delete()
    # Delete Texts
    db.query(Text).filter(Text.user_upload_id == id).delete()
    # Delete user_upload
    # check if the file is used by any other uploads
    same_file = db.query(UserUpload).filter(
        UserUpload.s3_link == uu.s3_link).all()
    if len(same_file) == 0:
        s3 = S3Service()
        s3.delete_file(uu.s3_link)

    uu.deleted = True
    db.commit()

    return get_user_uploads(db, current_user)


def create_user_upload(db: Session, current_user: schemas.User, file: UploadFile):
    if not current_user.can_create_files:
        raise Errors.out_of_files
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
        filename=file.filename
    )
    db.add(db_user_upload)
    db.commit()
    db.refresh(db_user_upload)

    return db_user_upload


def update_context_status(id: int, db: Session, current_user: schemas.User):
    uu = db.query(UserUpload).get(id)
    if uu.user_id != current_user.id:
        raise Errors.credentials_error

    uu.include_in_context = not (uu.include_in_context)

    db.commit()

    return get_user_uploads(db, current_user)

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def handle_url_archive(url: str, db: Session, current_user: schemas.User):
    resp = requests.get(url)
    content_type = resp.headers['Content-Type']
    text_content = None
    if "html" in content_type:
        content = resp.text
        soup = BeautifulSoup(content, 'html.parser')
        texts = soup.findAll(text=True)
        visible = filter(tag_visible, texts)
        text_content = " ".join(t.strip() for t in visible)
    elif "text" in content_type:
        text_content = resp.text
    else:
        return { "success": False, "message": "URL Type not supported"}
    
    new_text = Text(
        user_id=current_user.id,
        name=url,
        content=text_content,
    )

    db.add(new_text)
    db.commit()
    db.refresh(new_text)

    new_text.refresh_embeddings()

    return {"success": True, "message": "Archive Successful"}