"""Muamalat (مصرف الجمهورية) — local card payments with OTP."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.gateways.base import GatewayInitResult, LibyanGatewayAdapter, sign_payload


class MuamalatGateway(LibyanGatewayAdapter):
    slug = "muamalat"
    name_ar = "معاملات — مصرف الجمهورية"

    def create_payment(
        self,
        *,
        amount_lyd: float,
        user_id: uuid.UUID,
        order_type: str,
        order_id: uuid.UUID | None,
        return_url: str,
    ) -> GatewayInitResult:
        ref = self._ref("MML")
        base = settings.payment_return_url_base.rstrip("/")
        redirect = (
            f"{base}/pay/muamalat?"
            f"ref={ref}&amount={amount_lyd:.2f}&return={return_url}"
        )
        if settings.gateway_sandbox_mode:
            redirect += "&sandbox=1"
        return GatewayInitResult(
            payment_id=uuid.uuid4(),
            gateway_ref=ref,
            redirect_url=redirect,
            status="redirected",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        )

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        if not settings.muamalat_webhook_secret:
            return settings.gateway_sandbox_mode
        expected = sign_payload(settings.muamalat_webhook_secret, payload)
        return hmac_compare(expected, signature)

    def parse_webhook_status(self, payload: dict) -> tuple[str, str]:
        ref = payload.get("transaction_ref") or payload.get("ref", "")
        status = payload.get("status", "failed")
        return ref, "completed" if status in {"success", "completed", "paid"} else "failed"


def hmac_compare(a: str, b: str) -> bool:
    import hmac as _hmac

    return _hmac.compare_digest(a, b)
