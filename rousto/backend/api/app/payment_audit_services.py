"""Backward-compatible re-exports — use app.service_layer.payments.audit_service instead."""

from app.service_layer.payments.audit_service import log_payment_event

__all__ = ["log_payment_event"]
