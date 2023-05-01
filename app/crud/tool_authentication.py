from sqlalchemy.orm import Session
from app.models import ToolAuthentication
import app.schemas as schemas


def create_tool_authentication(auth_data: schemas.GoogleAuthorizationCode, db: Session, current_user: schemas.User):
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
