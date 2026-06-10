"""Edfali / Tadawul Cash payment service."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.gateways.edfali import EdfaliGateway
from app.models import User, Vendor
from app.service_layer.payments.checkout_service import initiate_checkout

GATEWAY_SLUG = "edfali"
_adapter = EdfaliGateway()


class EdfaliPaymentService:
    slug = GATEWAY_SLUG
    name_ar = _adapter.name_ar

    def initiate(
        self,
        db: Session,
        user: User,
        *,
        amount_lyd: float,
        order_type: str,
        order_id: uuid.UUID | None,
        return_url: str,
        vendor: Vendor | None = None,
    ) -> dict:
        return initiate_checkout(
            db,
            user,
            amount_lyd=amount_lyd,
            gateway=GATEWAY_SLUG,
            order_type=order_type,
            order_id=order_id,
            return_url=return_url,
            vendor=vendor,
        )

    def verify_callback(self, raw_body: bytes, signature: str) -> bool:
        return _adapter.verify_webhook_signature(raw_body, signature)

    def parse_callback(self, payload: dict) -> tuple[str, str]:
        return _adapter.parse_webhook_status(payload)


edfali_payment_service = EdfaliPaymentService()
