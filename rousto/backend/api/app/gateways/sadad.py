"""Sadad (المدار الجديد) — mobile quick pay."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.config import settings
from app.gateways.base import GatewayInitResult, LibyanGatewayAdapter, sign_payload
from app.gateways.muamalat import hmac_compare


class SadadGateway(LibyanGatewayAdapter):
    slug = "sadad"
    name_ar = "سداد — المدار الجديد"

    def create_payment(
        self,
        *,
        amount_lyd: float,
        user_id: uuid.UUID,
        order_type: str,
        order_id: uuid.UUID | None,
        return_url: str,
    ) -> GatewayInitResult:
        ref = self._ref("SDD")
        base = settings.payment_return_url_base.rstrip("/")
        redirect = (
            f"{base}/pay/sadad?"
            f"ref={ref}&amount={amount_lyd:.2f}&return={return_url}"
        )
        return GatewayInitResult(
            payment_id=uuid.uuid4(),
            gateway_ref=ref,
            redirect_url=redirect,
            status="redirected",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        if not settings.sadad_webhook_secret:
            return settings.gateway_sandbox_mode
        return hmac_compare(sign_payload(settings.sadad_webhook_secret, payload), signature)

    def parse_webhook_status(self, payload: dict) -> tuple[str, str]:
        ref = payload.get("payment_id") or payload.get("ref", "")
        ok = payload.get("payment_status") in {"SUCCESS", "completed", "paid"}
        return ref, "completed" if ok else "failed"
