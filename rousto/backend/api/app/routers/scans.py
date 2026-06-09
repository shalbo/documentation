from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.ai_diagnosis import get_scan_type_catalog, is_valid_scan_type
from app.config import settings
from app.db import get_db
from app.deps import get_current_user
from app.models import User
from app.scan_services import (
    create_scan_with_analysis,
    ensure_storage_dir,
    get_image_file,
    get_user_vehicle,
    load_scan,
    run_analysis,
    save_scan_images,
    serialize_scan,
)

router = APIRouter(prefix="/scans", tags=["scans"])


@router.get("/types")
def list_scan_types():
    return {"data": get_scan_type_catalog()}


@router.post("", status_code=201)
async def create_scan(
    vehicle_id: UUID = Form(...),
    scan_type: str = Form(...),
    images: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not is_valid_scan_type(scan_type):
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_SCAN_TYPE", "message": "نوع الفحص غير مدعوم"},
        )
    if not images:
        raise HTTPException(
            status_code=400,
            detail={"code": "NO_IMAGES", "message": "مطلوب صورة واحدة على الأقل"},
        )

    vehicle = get_user_vehicle(db, user.id, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "المركبة غير موجودة"},
        )

    scan_id = uuid4()
    try:
        storage_root = ensure_storage_dir()
        saved = await save_scan_images(scan_id, images, storage_root)
        findings = run_analysis(scan_type, len(saved))
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_IMAGE", "message": str(exc)},
        ) from exc

    scan = create_scan_with_analysis(
        db,
        scan_id=scan_id,
        user_id=user.id,
        vehicle_id=vehicle_id,
        scan_type=scan_type,
        saved_images=saved,
        findings=findings,
    )
    loaded = load_scan(db, scan.id, user.id)
    return {"data": serialize_scan(loaded, api_prefix=settings.api_prefix)}


@router.get("/{scan_id}")
def get_scan(
    scan_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scan = load_scan(db, scan_id, user.id)
    if not scan:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الفحص غير موجود"},
        )
    return {"data": serialize_scan(scan, api_prefix=settings.api_prefix)}


@router.get("/{scan_id}/images/{image_id}")
def get_scan_image(
    scan_id: UUID,
    image_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scan = load_scan(db, scan_id, user.id)
    if not scan:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الفحص غير موجود"},
        )

    image = next((img for img in scan.images if img.id == image_id), None)
    if not image:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "الصورة غير موجودة"},
        )

    path = get_image_file(image.storage_key)
    if not path:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "ملف الصورة غير موجود"},
        )
    return FileResponse(path, media_type=image.mime_type)
