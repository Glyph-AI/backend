from sqlalchemy.orm import Session
from app.models import ToolAuthentication
import app.schemas as schemas


def create_tool_authentication(auth_data: schemas.GoogleAuthorizationCode, db: Session, current_user: schemas.User):
    # check if a record already exists
    auth = db.query(ToolAuthentication).filter(
        ToolAuthentication.user_id == auth_data.user_id,
        ToolAuthentication.tool_id == auth_data.tool_id,
        ToolAuthentication.bot_id == auth_data.bot_id
    ).first()
    if auth is not None:
        auth.authorization_code = auth_data.code
        db.commit()
        db.refresh(auth)
        return auth

    db_ta = ToolAuthentication(
        bot_id=auth_data.bot_id,
        user_id=current_user.id,
        tool_id=auth_data.tool_id,
        authorization_code=auth_data.code
    )

    db.add(db_ta)
    db.commit()
    db.refresh(db_ta)

    return db_ta
