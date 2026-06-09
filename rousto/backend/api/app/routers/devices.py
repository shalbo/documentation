from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.device_services import deactivate_device_token, register_device_token
from app.models import User

router = APIRouter(tags=["devices"])


class DeviceRegisterIn(BaseModel):
    fcm_token: str = Field(min_length=20, max_length=512)
    platform: str = Field(default="unknown", max_length=20)


class DeviceUnregisterIn(BaseModel):
    fcm_token: str = Field(min_length=20, max_length=512)


@router.post("/me/devices/register")
def register_device(
    body: DeviceRegisterIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        entry = register_device_token(
            db,
            user_id=user.id,
            fcm_token=body.fcm_token,
            platform=body.platform,
        )
        db.commit()
        return {
            "data": {
                "registered": True,
                "device_id": str(entry.id),
                "platform": entry.platform,
            }
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "DEVICE_REGISTER_FAILED", "message": str(exc)},
        ) from exc


@router.post("/me/devices/unregister")
def unregister_device(
    body: DeviceUnregisterIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ok = deactivate_device_token(db, user.id, body.fcm_token)
    db.commit()
    return {"data": {"unregistered": ok}}
