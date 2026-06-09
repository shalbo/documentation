from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import Address, LoyaltyTransaction, PaymentMethod, User, Vehicle
from app.schemas import (
    AddressOut,
    LoyaltyOut,
    LoyaltyTransactionOut,
    PaymentMethodOut,
    UserOut,
    UserStats,
    VehicleOut,
)
from app.services import get_user_stats, vehicle_display_name

router = APIRouter(tags=["profile"])


@router.get("/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stats = UserStats(**get_user_stats(db, user.id))
    payload = UserOut(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        avatar_initials=user.avatar_initials,
        loyalty_points=user.loyalty_points,
        stats=stats,
    )
    return {"data": payload.model_dump()}


@router.get("/me/vehicles")
def list_vehicles(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    vehicles = db.scalars(
        select(Vehicle).where(Vehicle.user_id == user.id).order_by(Vehicle.is_default.desc())
    ).all()
    data = []
    for vehicle in vehicles:
        item = VehicleOut.model_validate(vehicle)
        item.display_name = vehicle_display_name(vehicle)
        data.append(item.model_dump())
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/me/addresses")
def list_addresses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    addresses = db.scalars(
        select(Address).where(Address.user_id == user.id).order_by(Address.is_default.desc())
    ).all()
    data = [AddressOut.model_validate(a).model_dump() for a in addresses]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/me/payment-methods")
def list_payment_methods(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    methods = db.scalars(
        select(PaymentMethod)
        .where(PaymentMethod.user_id == user.id)
        .order_by(PaymentMethod.is_default.desc())
    ).all()
    data = [PaymentMethodOut.model_validate(m).model_dump() for m in methods]
    return {"data": data, "meta": {"total": len(data)}}


@router.get("/me/loyalty")
def get_loyalty(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transactions = db.scalars(
        select(LoyaltyTransaction)
        .where(LoyaltyTransaction.user_id == user.id)
        .order_by(LoyaltyTransaction.created_at.desc())
        .limit(20)
    ).all()
    payload = LoyaltyOut(
        balance=user.loyalty_points,
        transactions=[
            LoyaltyTransactionOut.model_validate(t) for t in transactions
        ],
    )
    return {"data": payload.model_dump()}
