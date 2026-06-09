import mimetypes
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.ai_diagnosis import DiagnosisFinding, analyze
from app.config import settings
from app.models import ScanFinding, ScanImage, Service, Vehicle, VehicleScan

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGES = 3
STORAGE_KEY_RE = re.compile(r"^[a-zA-Z0-9/_\-.]+$")


def ensure_storage_dir() -> Path:
    path = Path(settings.scan_storage_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_user_vehicle(db: Session, user_id: UUID, vehicle_id: UUID) -> Vehicle | None:
    return db.scalar(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.user_id == user_id)
    )


def resolve_service_id(db: Session, slug: str) -> UUID | None:
    service = db.scalar(
        select(Service).where(Service.slug == slug, Service.is_active.is_(True))
    )
    return service.id if service else None


async def save_scan_images(
    scan_id: UUID,
    uploads: list[UploadFile],
    storage_root: Path,
) -> list[tuple[UUID, str, str, int]]:
    saved: list[tuple[UUID, str, str, int]] = []
    scan_dir = storage_root / str(scan_id)
    scan_dir.mkdir(parents=True, exist_ok=True)

    for index, upload in enumerate(uploads[:MAX_IMAGES]):
        mime = upload.content_type or mimetypes.guess_type(upload.filename or "")[0]
        if mime not in ALLOWED_MIME:
            raise ValueError("نوع الصورة غير مدعوم — استخدم JPEG أو PNG أو WebP")

        ext = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }[mime]
        image_id = uuid4()
        filename = f"{index:02d}_{image_id.hex}{ext}"
        storage_key = f"{scan_id}/{filename}"
        target = storage_root / storage_key
        content = await upload.read()
        if not content:
            raise ValueError("الصورة فارغة")
        target.write_bytes(content)
        saved.append((image_id, storage_key, mime, index))
    return saved


def create_scan_with_analysis(
    db: Session,
    *,
    scan_id: UUID,
    user_id: UUID,
    vehicle_id: UUID,
    scan_type: str,
    saved_images: list[tuple[UUID, str, str, int]],
    findings: list[DiagnosisFinding],
) -> VehicleScan:
    now = datetime.now(timezone.utc)
    scan = VehicleScan(
        id=scan_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        scan_type=scan_type,
        status="completed",
        created_at=now,
        completed_at=now,
    )
    db.add(scan)
    db.flush()

    for image_id, storage_key, mime, sort_order in saved_images:
        db.add(
            ScanImage(
                id=image_id,
                scan_id=scan.id,
                storage_key=storage_key,
                mime_type=mime,
                sort_order=sort_order,
                created_at=now,
            )
        )

    for finding in findings:
        db.add(
            ScanFinding(
                id=uuid4(),
                scan_id=scan.id,
                code=finding.code,
                label_ar=finding.label_ar,
                severity=finding.severity,
                confidence=finding.confidence,
                suggested_service_id=resolve_service_id(db, finding.service_slug),
                details=finding.details,
            )
        )

    db.commit()
    return load_scan(db, scan.id, user_id)


def load_scan(db: Session, scan_id: UUID, user_id: UUID) -> VehicleScan | None:
    return db.scalar(
        select(VehicleScan)
        .options(
            joinedload(VehicleScan.images),
            joinedload(VehicleScan.findings).joinedload(ScanFinding.suggested_service),
        )
        .where(VehicleScan.id == scan_id, VehicleScan.user_id == user_id)
    )


def list_user_scans(db: Session, user_id: UUID) -> list[VehicleScan]:
    return list(
        db.scalars(
            select(VehicleScan)
            .options(
                joinedload(VehicleScan.findings).joinedload(ScanFinding.suggested_service),
            )
            .where(VehicleScan.user_id == user_id)
            .order_by(VehicleScan.created_at.desc())
        )
        .unique()
        .all()
    )


def get_image_file(storage_key: str) -> Path | None:
    if not STORAGE_KEY_RE.match(storage_key):
        return None
    root = ensure_storage_dir().resolve()
    target = (root / storage_key).resolve()
    if not str(target).startswith(str(root)):
        return None
    return target if target.is_file() else None


def serialize_scan(scan: VehicleScan, *, api_prefix: str) -> dict:
    findings = []
    for f in scan.findings:
        item = {
            "code": f.code,
            "label_ar": f.label_ar,
            "severity": f.severity,
            "confidence": float(f.confidence),
            "details": f.details or {},
        }
        if f.suggested_service:
            item["suggested_service"] = {
                "id": str(f.suggested_service.id),
                "slug": f.suggested_service.slug,
                "name_ar": f.suggested_service.name_ar,
                "price_sar": float(f.suggested_service.price_sar),
            }
        findings.append(item)

    images = [
        {
            "id": str(img.id),
            "mime_type": img.mime_type,
            "sort_order": img.sort_order,
            "url": f"{api_prefix}/scans/{scan.id}/images/{img.id}",
        }
        for img in sorted(scan.images, key=lambda i: i.sort_order)
    ]

    return {
        "id": str(scan.id),
        "vehicle_id": str(scan.vehicle_id),
        "scan_type": scan.scan_type,
        "status": scan.status,
        "created_at": scan.created_at.isoformat(),
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "findings": findings,
        "images": images,
    }


def run_analysis(scan_type: str, image_count: int) -> list[DiagnosisFinding]:
    return analyze(scan_type, image_count=image_count)
