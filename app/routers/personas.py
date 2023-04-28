from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.schemas import User, Persona
import app.models as models

personas_router = APIRouter(tags=["Personas API"], prefix="/personas")


@personas_router.get("", response_model=list[Persona])
async def get_personas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(models.Persona).all()
