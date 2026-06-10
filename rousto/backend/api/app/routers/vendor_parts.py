from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.category_services import list_child_categories, list_root_categories
from app.db import get_db
from app.deps import get_current_vendor
from app.vendor_staff_rbac import require_price_edit_access
from app.i18n import resolve_locale
from app.models import Vendor
from app.part_image_services import process_bulk_images_zip
from app.spare_parts_bulk_services import BULK_COLUMNS, TEMPLATE_CSV, process_bulk_upload
from app.api_responses import success
from app.service_layer.vendors import (
    PRODUCTS_LIMIT_EXCEEDED_MSG,
    vendor_create_product,
    vendor_tier_summary,
)
from app.tier_services import require_excel_upload, tier_limit_http_detail

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
    vin_prefix: str | None = Field(default=None, max_length=17)
    vin_prefixes: list[str] = Field(default_factory=list)
    is_oem: bool = False
    part_condition: str = Field(default="new", pattern=r"^(new|used)$")
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
    _: None = Depends(require_price_edit_access),
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
            vin_prefixes=body.vin_prefixes,
            is_oem=body.is_oem,
            part_condition=body.part_condition,
            warranty_months=body.warranty_months,
            locale=locale,
        )
        db.commit()
    except ValueError as exc:
        if str(exc) == PRODUCTS_LIMIT_EXCEEDED_MSG:
            raise HTTPException(status_code=403, detail=tier_limit_http_detail(exc)) from exc
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


@router.get("/tier")
def vendor_get_tier(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        data = vendor_tier_summary(db, vendor)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "TIER_ERROR", "message": str(exc)},
        ) from exc
    return {"data": data}


@router.get("/bulk-upload/template")
def vendor_bulk_upload_template(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    try:
        require_excel_upload(db, vendor)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=tier_limit_http_detail(exc)) from exc
    return Response(
        content=TEMPLATE_CSV.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="rousto-parts-template.csv"',
        },
    )


@router.post("/bulk-upload")
async def vendor_bulk_upload(
    file: UploadFile = File(...),
    vendor: Vendor = Depends(get_current_vendor),
    _: None = Depends(require_price_edit_access),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_FILE", "message": "لم يُرفَع أي ملف"},
        )
    content = await file.read()
    try:
        result = process_bulk_upload(db, vendor, content, file.filename)
    except ValueError as exc:
        if "Excel/ZIP" in str(exc) or str(exc) == PRODUCTS_LIMIT_EXCEEDED_MSG:
            raise HTTPException(status_code=403, detail=tier_limit_http_detail(exc)) from exc
        raise HTTPException(
            status_code=400,
            detail={"code": "BULK_ERROR", "message": str(exc)},
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"code": "BULK_FAILED", "message": "فشلت المعالجة — لم يُحفظ أي صف"},
        ) from exc

    payload = result.to_dict()
    if result.errors:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "BULK_VALIDATION",
                "message": f"فشل التحقق — {len(result.errors)} خطأ",
                "data": payload,
            },
        )
    return {
        "data": payload,
        "meta": {
            "message": f"تم رفع {result.imported} قطعة بنجاح",
            "columns": BULK_COLUMNS,
        },
    }


@router.post("/bulk-images-zip")
async def vendor_bulk_images_zip(
    file: UploadFile = File(...),
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_FILE", "message": "لم يُرفَع أي ملف"},
        )
    try:
        require_excel_upload(db, vendor)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=tier_limit_http_detail(exc)) from exc
    content = await file.read()
    try:
        result = process_bulk_images_zip(db, vendor, content, file.filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "ZIP_ERROR", "message": str(exc)},
        ) from exc
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={"code": "ZIP_FAILED", "message": "فشلت معالجة الأرشيف"},
        ) from exc

    payload = result.to_dict()
    return {
        "data": payload,
        "meta": {
            "message": f"تم ربط {result.linked} صورة بنجاح",
        },
    }
