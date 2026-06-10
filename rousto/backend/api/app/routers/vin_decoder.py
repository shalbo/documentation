from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.vin_decoder_services import decode_vin, list_decoders_admin

router = APIRouter(tags=["vin-decoder"])


@router.get("/vin/decode")
def get_vin_decode(
    vin: str = Query(..., min_length=8, max_length=17),
    db: Session = Depends(get_db),
):
    try:
        data = decode_vin(db, vin)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_VIN", "message": str(exc)},
        ) from exc
    if not data:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "VIN_NOT_FOUND",
                "message": "لم نتعرف على رقم الهيكل في قاعدة السوق الليبي",
            },
        )
    return {"data": data}


@router.get("/admin/vin-decoders")
def admin_list_vin_decoders(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = list_decoders_admin(db)
    return {"data": data, "meta": {"total": len(data), "market": "libya"}}
