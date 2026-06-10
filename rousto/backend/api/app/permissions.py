from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Permission, Role, User, UserRole, UserVendorLink, role_permissions_table

ROLE_CUSTOMER = "customer"
ROLE_ADMIN = "admin"
ROLE_TECHNICIAN = "technician"
ROLE_SUPPORT = "support"
ROLE_VENDOR = "vendor"
ROLE_DRIVER = "driver"
ROLE_WORKSHOP = "workshop"


@dataclass
class AuthPrincipal:
    user: User | None
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)
    vendor_id: UUID | None = None
    auth_method: str = "jwt"
    staff_id: UUID | None = None
    staff_role: str | None = None
    staff_name: str | None = None

    @property
    def is_staff(self) -> bool:
        return self.staff_id is not None

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def is_admin(self) -> bool:
        return ROLE_ADMIN in self.roles


def load_user_roles_and_permissions(db: Session, user_id: UUID) -> tuple[list[str], list[str]]:
    rows = db.execute(
        select(Role.slug, Permission.slug)
        .select_from(UserRole)
        .join(Role, UserRole.role_id == Role.id)
        .join(role_permissions_table, role_permissions_table.c.role_id == Role.id)
        .join(Permission, Permission.id == role_permissions_table.c.permission_id)
        .where(UserRole.user_id == user_id)
    ).all()

    if not rows:
        return [ROLE_CUSTOMER], ["bookings:read", "bookings:create", "support:self", "catalog:read"]

    roles = sorted({r[0] for r in rows})
    permissions = sorted({r[1] for r in rows})
    return roles, permissions


def load_vendor_id_for_user(db: Session, user_id: UUID) -> UUID | None:
    link = db.scalar(
        select(UserVendorLink.vendor_id).where(UserVendorLink.user_id == user_id).limit(1)
    )
    return link


def build_principal(
    db: Session,
    user: User,
    *,
    auth_method: str = "jwt",
) -> AuthPrincipal:
    roles, permissions = load_user_roles_and_permissions(db, user.id)
    vendor_id = load_vendor_id_for_user(db, user.id)
    return AuthPrincipal(
        user=user,
        roles=roles,
        permissions=permissions,
        vendor_id=vendor_id,
        auth_method=auth_method,
    )


def build_staff_principal(staff) -> AuthPrincipal:
    from app.models import VendorStaff

    assert isinstance(staff, VendorStaff)
    return AuthPrincipal(
        user=None,
        roles=[ROLE_VENDOR, f"staff_{staff.role}"],
        permissions=_staff_permissions(staff.role),
        vendor_id=staff.vendor_id,
        auth_method="jwt",
        staff_id=staff.id,
        staff_role=staff.role,
        staff_name=staff.name,
    )


def _staff_permissions(role: str) -> list[str]:
    base = ["catalog:read", "vendors:self"]
    if role == "manager":
        return base + ["staff:manage", "parts:write", "parts:price"]
    if role == "accountant":
        return base + ["wallet:read", "wallet:withdraw", "parts:price"]
    if role == "sales":
        return base + ["parts:write"]
    return base


def serialize_principal(principal: AuthPrincipal) -> dict:
    if principal.is_staff:
        return {
            "staff": {
                "id": str(principal.staff_id),
                "name": principal.staff_name,
                "role": principal.staff_role,
            },
            "roles": principal.roles,
            "permissions": principal.permissions,
            "vendor_id": str(principal.vendor_id) if principal.vendor_id else None,
            "auth_method": principal.auth_method,
            "actor_type": "vendor_staff",
        }
    user = principal.user
    return {
        "user": {
            "id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "avatar_initials": user.avatar_initials,
        },
        "roles": principal.roles,
        "permissions": principal.permissions,
        "vendor_id": str(principal.vendor_id) if principal.vendor_id else None,
        "auth_method": principal.auth_method,
        "actor_type": "user",
    }
