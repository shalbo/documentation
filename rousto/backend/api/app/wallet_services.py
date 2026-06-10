"""Backward-compatible re-exports — use app.service_layer.payments.wallet_service instead."""

from app.service_layer.payments.wallet_service import (
    PLATFORM_OWNER_ID,
    _d,
    approve_withdrawal,
    credit_wallet,
    debit_wallet,
    deduct_driver_commission,
    get_or_create_wallet,
    list_wallet_transactions,
    request_withdrawal,
    settle_vendor_sale,
    tx_out,
    wallet_out,
)

__all__ = [
    "PLATFORM_OWNER_ID",
    "_d",
    "approve_withdrawal",
    "credit_wallet",
    "debit_wallet",
    "deduct_driver_commission",
    "get_or_create_wallet",
    "list_wallet_transactions",
    "request_withdrawal",
    "settle_vendor_sale",
    "tx_out",
    "wallet_out",
]
