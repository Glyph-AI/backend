from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.dependencies import get_db, get_current_user
from app.schemas import User, UserDeviceBase, UserDevice
import app.models as models

notifications_router = APIRouter(tags=["Notifications API"], prefix="/notifications")

@notifications_router.post("/user_device", response_model=UserDevice)
def create_user_device(device: UserDeviceBase, db: Session=Depends(get_db)):
    # don't create a new device if an old one exists
    user_device = db.query(models.UserDevice).filter(models.UserDevice.device_token == device.device_token).first()

    if user_device:
        user_device.last_used = datetime.now()
        return user_device
    
    new_user_device = models.UserDevice(
        device_token=device.device_token,
        user_id=device.user_id
    )

    db.add(new_user_device)
    db.commit()
    db.refresh(new_user_device)

    return new_user_device
