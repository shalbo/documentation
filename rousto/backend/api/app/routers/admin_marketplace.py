from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin_key
from app.marketplace_services import get_marketplace_analytics

router = APIRouter(prefix="/admin", tags=["admin-marketplace"])


@router.get("/marketplace/analytics")
def admin_marketplace_analytics(
    _: None = Depends(require_admin_key),
    db: Session = Depends(get_db),
):
    data = get_marketplace_analytics(db)
    return {"data": data}
