import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.db import get_db
from app.gateways.registry import validate_gateway
from app.libyan_payment_services import complete_gateway_webhook

router = APIRouter(prefix="/webhooks/payments", tags=["payment-webhooks"])


@router.post("/{gateway}")
async def payment_webhook(
    gateway: str,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        validate_gateway(gateway)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"code": "INVALID_GATEWAY", "message": str(exc)}) from exc

    raw = await request.body()
    signature = request.headers.get("X-Signature") or request.headers.get("X-Webhook-Signature", "")
    try:
        payload = json.loads(raw.decode() or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail={"code": "INVALID_JSON", "message": "JSON غير صالح"}) from exc

    try:
        gp = complete_gateway_webhook(
            db,
            gateway=gateway,
            payload=payload,
            raw_body=raw,
            signature=signature,
            ip_address=request.client.host if request.client else None,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=403,
            detail={"code": "WEBHOOK_REJECTED", "message": str(exc)},
        ) from exc

    return {
        "data": {
            "processed": gp is not None,
            "payment_id": str(gp.id) if gp else None,
            "status": gp.status if gp else None,
        }
    }
