from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Testimonial
from app.schemas import TestimonialOut

router = APIRouter(prefix="/testimonials", tags=["testimonials"])


@router.get("")
def list_testimonials(db: Session = Depends(get_db)):
    testimonials = db.scalars(
        select(Testimonial)
        .where(Testimonial.is_published.is_(True))
        .order_by(Testimonial.created_at.desc())
    ).all()
    data = [TestimonialOut.model_validate(t).model_dump() for t in testimonials]
    return {"data": data, "meta": {"total": len(data)}}
