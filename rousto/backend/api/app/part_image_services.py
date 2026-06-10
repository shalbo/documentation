"""Part image download, resize, storage, and ZIP bulk linking."""

from __future__ import annotations

import io
import re
import shutil
import tempfile
import uuid
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
from PIL import Image
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Part, PartInventory, SparePartImage, Vendor

PARTS_SUBDIR = "parts"
ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_DIMENSION = 1200
MAX_IMAGE_INPUT_BYTES = 15 * 1024 * 1024
MAX_ZIP_BYTES = 100 * 1024 * 1024
MAX_ZIP_FILES = 5000
MAX_ZIP_UNCOMPRESSED = 200 * 1024 * 1024
HTTP_TIMEOUT = 30.0
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)
OEM_FILE_RE = re.compile(r"^[A-Za-z0-9\u0600-\u06FF\-_.]+$")


@dataclass
class ZipImageError:
    file: str
    message: str


@dataclass
class ZipBulkImagesResult:
    total_files: int = 0
    linked: int = 0
    skipped: int = 0
    errors: list[ZipImageError] = field(default_factory=list)
    unmatched: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "linked": self.linked,
            "skipped": self.skipped,
            "failed": len(self.errors),
            "unmatched": self.unmatched,
            "errors": [{"file": e.file, "message": e.message} for e in self.errors],
        }


def _now() -> datetime:
    return datetime.now(timezone.utc)


def parts_storage_root() -> Path:
    root = Path(settings.scan_storage_path) / PARTS_SUBDIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def public_url_for_path(storage_path: str) -> str:
    return f"{settings.api_prefix}/parts/media/{storage_path}"


def is_valid_image_url(url: str) -> bool:
    if not url or not url.strip():
        return True
    parsed = urlparse(url.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _safe_oem_dir(oem_number: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9\-_]", "-", oem_number.strip())[:60]
    return cleaned or "unknown"


def resize_image_bytes(content: bytes) -> bytes:
    if len(content) > MAX_IMAGE_INPUT_BYTES:
        raise ValueError(
            f"حجم الصورة يتجاوز الحد ({MAX_IMAGE_INPUT_BYTES // (1024 * 1024)} ميجابايت)"
        )
    try:
        with Image.open(io.BytesIO(content)) as img:
            img = img.convert("RGB")
            w, h = img.size
            if max(w, h) > MAX_IMAGE_DIMENSION:
                img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)
            out = io.BytesIO()
            img.save(out, format="WEBP", quality=85, method=6)
            return out.getvalue()
    except Exception as exc:
        raise ValueError("ملف الصورة تالف أو غير مدعوم") from exc


def save_part_image_bytes(oem_number: str, content: bytes) -> tuple[str, str]:
    processed = resize_image_bytes(content)
    file_id = uuid.uuid4().hex[:12]
    rel = f"{PARTS_SUBDIR}/{_safe_oem_dir(oem_number)}/{file_id}.webp"
    dest = Path(settings.scan_storage_path) / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(processed)
    return rel, public_url_for_path(rel)


def download_image_from_url(url: str) -> bytes:
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
            response = client.get(url.strip())
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").split(";")[0].strip()
            if content_type and content_type not in ALLOWED_IMAGE_MIME:
                raise ValueError("الرابط لا يشير إلى صورة JPEG أو PNG أو WebP")
            data = response.content
            if not data:
                raise ValueError("الصورة فارغة")
            return data
    except httpx.HTTPError as exc:
        raise ValueError(f"فشل تحميل الصورة من الرابط: {exc}") from exc


def attach_part_image(
    db: Session,
    part: Part,
    *,
    storage_path: str,
    public_url: str,
    source: str,
    is_primary: bool = True,
    sort_order: int = 0,
) -> SparePartImage:
    if is_primary:
        db.execute(
            update(SparePartImage)
            .where(
                SparePartImage.part_id == part.id,
                SparePartImage.is_primary.is_(True),
            )
            .values(is_primary=False)
        )
        part.image_url = public_url

    row = SparePartImage(
        id=uuid.uuid4(),
        part_id=part.id,
        storage_path=storage_path,
        public_url=public_url,
        is_primary=is_primary,
        sort_order=sort_order,
        source=source,
        created_at=_now(),
    )
    db.add(row)
    db.flush()
    return row


def import_part_image_from_url(
    db: Session,
    part: Part,
    image_url: str,
) -> SparePartImage | None:
    url = image_url.strip()
    if not url:
        return None
    if not is_valid_image_url(url):
        raise ValueError("رابط الصورة غير صالح — استخدم http أو https")
    raw = download_image_from_url(url)
    storage_path, public_url = save_part_image_bytes(part.oem_number or part.part_number, raw)
    return attach_part_image(
        db,
        part,
        storage_path=storage_path,
        public_url=public_url,
        source="url",
    )


def _oem_from_filename(name: str) -> str:
    return Path(name).stem.strip()


def _vendor_parts_by_oem(db: Session, vendor_id: uuid.UUID) -> dict[str, Part]:
    rows = db.scalars(
        select(Part)
        .join(PartInventory, PartInventory.part_id == Part.id)
        .where(PartInventory.vendor_id == vendor_id)
    ).all()
    mapping: dict[str, Part] = {}
    for part in rows:
        for key in (part.oem_number, part.part_number):
            if key:
                mapping[key.strip().upper()] = part
    return mapping


def _validate_zip_archive(zf: zipfile.ZipFile) -> None:
    infos = zf.infolist()
    if not infos:
        raise ValueError("الأرشيف فارغ")
    if len(infos) > MAX_ZIP_FILES:
        raise ValueError(f"الأرشيف يحتوي أكثر من {MAX_ZIP_FILES} ملف")
    total = sum(i.file_size for i in infos)
    if total > MAX_ZIP_UNCOMPRESSED:
        raise ValueError("حجم الملفات داخل الأرشيف كبير جداً")


def process_bulk_images_zip(
    db: Session,
    vendor: Vendor,
    content: bytes,
    filename: str,
) -> ZipBulkImagesResult:
    if vendor.status != "approved":
        raise ValueError("المحل غير معتمد بعد")
    if len(content) > MAX_ZIP_BYTES:
        raise ValueError("حجم ملف ZIP يتجاوز الحد (100 ميجابايت)")
    if not filename.lower().endswith(".zip"):
        raise ValueError("الصيغة المدعومة: .zip فقط")

    result = ZipBulkImagesResult()
    parts_map = _vendor_parts_by_oem(db, vendor.id)

    tmp_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp_dir = tempfile.mkdtemp(prefix="rousto-parts-zip-")
    try:
        tmp_zip.write(content)
        tmp_zip.close()
        try:
            with zipfile.ZipFile(tmp_zip.name, "r") as zf:
                _validate_zip_archive(zf)
                zf.extractall(tmp_dir)
        except zipfile.BadZipFile as exc:
            raise ValueError("ملف ZIP تالف أو غير صالح") from exc

        image_files: list[Path] = []
        for path in Path(tmp_dir).rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in ALLOWED_IMAGE_EXT:
                result.skipped += 1
                continue
            image_files.append(path)

        result.total_files = len(image_files)
        if not image_files:
            raise ValueError("لا توجد صور مدعومة داخل الأرشيف (jpg, png, webp)")

        try:
            for img_path in image_files:
                rel_name = str(img_path.relative_to(tmp_dir))
                oem_key = _oem_from_filename(img_path.name).upper()
                if not oem_key or not OEM_FILE_RE.match(_oem_from_filename(img_path.name)):
                    result.errors.append(
                        ZipImageError(rel_name, "اسم الملف غير صالح كرقم OEM")
                    )
                    continue
                part = parts_map.get(oem_key)
                if not part:
                    result.unmatched.append(rel_name)
                    continue
                try:
                    raw = img_path.read_bytes()
                    storage_path, public_url = save_part_image_bytes(
                        part.oem_number or part.part_number,
                        raw,
                    )
                    attach_part_image(
                        db,
                        part,
                        storage_path=storage_path,
                        public_url=public_url,
                        source="zip",
                    )
                    result.linked += 1
                except ValueError as exc:
                    result.errors.append(ZipImageError(rel_name, str(exc)))
            db.commit()
        except Exception:
            db.rollback()
            raise
    finally:
        Path(tmp_zip.name).unlink(missing_ok=True)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return result


def get_part_image_file(storage_path: str) -> Path | None:
    if ".." in storage_path or storage_path.startswith("/"):
        return None
    if not storage_path.startswith(f"{PARTS_SUBDIR}/"):
        return None
    base = Path(settings.scan_storage_path).resolve()
    target = (base / storage_path).resolve()
    if not str(target).startswith(str(base)):
        return None
    if not target.is_file():
        return None
    return target
