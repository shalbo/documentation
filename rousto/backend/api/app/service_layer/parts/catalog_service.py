"""Parts catalog facade — delegates to domain modules."""

from app.parts_services import (
    attach_part_to_booking,
    create_part,
    create_warranty_claim,
    get_part_detail,
    list_booking_parts,
    list_part_categories,
    list_parts_admin,
    list_warranty_claims_admin,
    search_parts,
)

__all__ = [
    "attach_part_to_booking",
    "create_part",
    "create_warranty_claim",
    "get_part_detail",
    "list_booking_parts",
    "list_part_categories",
    "list_parts_admin",
    "list_warranty_claims_admin",
    "search_parts",
]
