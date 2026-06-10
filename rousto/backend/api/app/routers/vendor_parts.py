from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.category_services import list_child_categories, list_root_categories
from app.db import get_db
from app.deps import get_current_vendor
from app.i18n import resolve_locale
from app.models import Vendor
from app.vendor_parts_services import vendor_create_product

router = APIRouter(prefix="/vendor/parts", tags=["vendor-parts"])


class VendorProductIn(BaseModel):
    category_id: UUID
    part_number: str = Field(min_length=2, max_length=60)
    slug: str = Field(min_length=2, max_length=80, pattern=r"^[a-z][a-z0-9-]*$")
    name_ar: str = Field(min_length=2, max_length=200)
    name_en: str | None = Field(default=None, max_length=200)
    price_sar: float = Field(gt=0)
    qty_available: int = Field(ge=1, le=9999)
    oem_number: str | None = Field(default=None, max_length=60)
    vin_prefix: str | None = Field(default=None, max_length=11)
    is_oem: bool = False
    warranty_months: int = Field(default=6, ge=1, le=36)


@router.get("/categories/roots")
def vendor_category_roots(
    locale: str = Depends(resolve_locale),
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    _ = vendor
    data = list_root_categories(db, locale)
    return {"data": data}


@router.get("/categories/{parent_id}/children")
def vendor_category_children(
    parent_id: UUID,
    locale: str = Depends(resolve_locale),
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    _ = vendor
    data = list_child_categories(db, parent_id, locale)
    return {"data": data}


@router.post("", status_code=201)
def vendor_add_product(
    body: VendorProductIn,
    locale: str = Depends(resolve_locale),
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        data = vendor_create_product(
            db,
            vendor,
            category_id=body.category_id,
            part_number=body.part_number,
            slug=body.slug,
            name_ar=body.name_ar,
            name_en=body.name_en,
            price_sar=body.price_sar,
            qty_available=body.qty_available,
            oem_number=body.oem_number,
            vin_prefix=body.vin_prefix,
            is_oem=body.is_oem,
            warranty_months=body.warranty_months,
            locale=locale,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "PRODUCT_ERROR", "message": str(exc)},
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail={"code": "CREATE_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}
