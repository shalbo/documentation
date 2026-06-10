"""RBAC rules for vendor staff sub-accounts."""

from fastapi import Depends, HTTPException

from app.deps import get_current_principal
from app.permissions import AuthPrincipal, ROLE_VENDOR

STAFF_ROLE_MANAGER = "manager"
STAFF_ROLE_SALES = "sales"
STAFF_ROLE_ACCOUNTANT = "accountant"

WALLET_BLOCKED_ROLES = frozenset({STAFF_ROLE_MANAGER, STAFF_ROLE_SALES})
PRICE_EDIT_BLOCKED_ROLES = frozenset({STAFF_ROLE_SALES})
STAFF_MANAGE_ALLOWED = frozenset({STAFF_ROLE_MANAGER})


def _staff_role(principal: AuthPrincipal) -> str | None:
    return principal.staff_role if principal.is_staff else None


def require_vendor_owner_or_manager(
    principal: AuthPrincipal = Depends(get_current_principal),
) -> AuthPrincipal:
    if principal.is_staff:
        if principal.staff_role not in STAFF_MANAGE_ALLOWED:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "FORBIDDEN",
                    "message": "صلاحية إدارة الموظفين للمدير فقط",
                },
            )
        return principal
    if ROLE_VENDOR in principal.roles or principal.vendor_id:
        return principal
    raise HTTPException(
        status_code=403,
        detail={"code": "FORBIDDEN", "message": "صلاحية التاجر مطلوبة"},
    )


def require_wallet_access(
    principal: AuthPrincipal = Depends(get_current_principal),
) -> AuthPrincipal:
    role = _staff_role(principal)
    if role in WALLET_BLOCKED_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "دورك لا يسمح بالوصول للمحفظة أو السحب المالي",
            },
        )
    return principal


def require_price_edit_access(
    principal: AuthPrincipal = Depends(get_current_principal),
) -> AuthPrincipal:
    role = _staff_role(principal)
    if role in PRICE_EDIT_BLOCKED_ROLES:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "دور المبيعات لا يسمح بتعديل الأسعار",
            },
        )
    return principal
