from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.cache import cached
from app.config import settings
from app.db import get_db
from app.landing_pricing_services import CURRENCY_AR, get_landing_page, get_landing_pricing

router = APIRouter(tags=["landing"])


@router.get("/landing/pricing")
def landing_pricing(db: Session = Depends(get_db)):
    def load():
        data = get_landing_pricing(db)
        return {
            "data": data,
            "meta": {
                "currency": CURRENCY_AR,
                "services_count": len(data["services"]),
                "marketing_plans_count": len(data["marketing_plans"]),
                "membership_plans_count": len(data["membership_plans"]),
                "packages_count": len(data["packages"]),
            },
        }

    return cached(settings.cache_landing_ttl, "landing_pricing", load)


@router.get("/landing/page")
def landing_page(db: Session = Depends(get_db)):
    def load():
        data = get_landing_page(db)
        return {"data": data, "meta": {"currency": CURRENCY_AR}}

    return cached(settings.cache_landing_ttl, "landing_page", load)
