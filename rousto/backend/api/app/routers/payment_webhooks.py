import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api_responses import success
from app.db import get_db
from app.gateways.registry import validate_gateway
from app.service_layer.payments import complete_gateway_webhook

router = APIRouter(tags=["payment-webhooks"])
legacy_router = APIRouter(prefix="/webhooks/payments", tags=["payment-webhooks"])


async def _handle_gateway_callback(
    gateway: str,
    request: Request,
    db: Session,
) -> dict:
    try:
        validate_gateway(gateway)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_GATEWAY", "message": str(exc)},
        ) from exc

    raw = await request.body()
    signature = request.headers.get("X-Signature") or request.headers.get("X-Webhook-Signature", "")
    try:
        payload = json.loads(raw.decode() or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_JSON", "message": "JSON غير صالح"},
        ) from exc

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

    return success(
        {
            "processed": gp is not None,
            "payment_id": str(gp.id) if gp else None,
            "status": gp.status if gp else None,
        },
        message="تمت معالجة إشعار البوابة",
    )


@router.post("/payments/muamalat/callback")
async def muamalat_callback(request: Request, db: Session = Depends(get_db)):
    return await _handle_gateway_callback("muamalat", request, db)


@router.post("/payments/sadad/callback")
async def sadad_callback(request: Request, db: Session = Depends(get_db)):
    return await _handle_gateway_callback("sadad", request, db)


@router.post("/payments/edfali/callback")
async def edfali_callback(request: Request, db: Session = Depends(get_db)):
    return await _handle_gateway_callback("edfali", request, db)


@legacy_router.post("/{gateway}")
async def payment_webhook_legacy(
    gateway: str,
    request: Request,
    db: Session = Depends(get_db),
):
    return await _handle_gateway_callback(gateway, request, db)
