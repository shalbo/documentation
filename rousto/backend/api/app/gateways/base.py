"""Base adapter for Libyan payment gateways."""

from __future__ import annotations

import hashlib
import hmac
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class GatewayInitResult:
    payment_id: uuid.UUID
    gateway_ref: str
    redirect_url: str | None
    status: str
    expires_at: datetime | None = None


class LibyanGatewayAdapter(ABC):
    slug: str
    name_ar: str

    @abstractmethod
    def create_payment(
        self,
        *,
        amount_lyd: float,
        user_id: uuid.UUID,
        order_type: str,
        order_id: uuid.UUID | None,
        return_url: str,
    ) -> GatewayInitResult:
        ...

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        ...

    @abstractmethod
    def parse_webhook_status(self, payload: dict) -> tuple[str, str]:
        """Return (gateway_ref, status) where status is completed|failed."""

    def _ref(self, prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:16].upper()}"


def sign_payload(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
