from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    BookingRevenue,
    LoyaltyReward,
    LoyaltyTransaction,
    MembershipPlan,
    PromotionRedemption,
    ServicePackage,
    User,
    UserMembership,
)

PLATFORM_FEE_RATE = Decimal("0.15")
TECHNICIAN_PAYOUT_RATE = Decimal("0.75")
RESERVE_RATE = Decimal("0.10")
POINTS_PER_DINAR = 10


def get_active_membership(db: Session, user_id: UUID) -> UserMembership | None:
    now = datetime.now(timezone.utc)
    return db.scalar(
        select(UserMembership)
        .join(MembershipPlan)
        .where(
            UserMembership.user_id == user_id,
            UserMembership.status == "active",
            (UserMembership.expires_at.is_(None)) | (UserMembership.expires_at > now),
        )
        .order_by(UserMembership.started_at.desc())
        .limit(1)
    )


def get_membership_plan_for_user(db: Session, user_id: UUID) -> MembershipPlan | None:
    membership = get_active_membership(db, user_id)
    if not membership:
        free = db.scalar(
            select(MembershipPlan).where(MembershipPlan.slug == "free", MembershipPlan.is_active)
        )
        return free
    return db.get(MembershipPlan, membership.plan_id)


def calculate_membership_discount(plan: MembershipPlan | None, price: float) -> float:
    if not plan or plan.discount_percent <= 0:
        return 0.0
    return float(
        Decimal(str(price)) * Decimal(str(plan.discount_percent)) / Decimal("100")
    )


def calculate_revenue_split(net_sar: float) -> dict:
    net = Decimal(str(net_sar))
    platform = (net * PLATFORM_FEE_RATE).quantize(Decimal("0.01"))
    technician = (net * TECHNICIAN_PAYOUT_RATE).quantize(Decimal("0.01"))
    reserve = (net * RESERVE_RATE).quantize(Decimal("0.01"))
    return {
        "platform_fee_sar": float(platform),
        "technician_payout_sar": float(technician),
        "reserve_sar": float(reserve),
    }


def record_booking_revenue(
    db: Session,
    booking_id: UUID,
    *,
    gross_sar: float,
    membership_discount_sar: float,
    promo_discount_sar: float,
    points_discount_sar: float,
    net_sar: float,
) -> None:
    split = calculate_revenue_split(net_sar)
    db.add(
        BookingRevenue(
            id=uuid4(),
            booking_id=booking_id,
            gross_sar=gross_sar,
            membership_discount_sar=membership_discount_sar,
            promo_discount_sar=promo_discount_sar,
            points_discount_sar=points_discount_sar,
            net_sar=net_sar,
            platform_fee_sar=split["platform_fee_sar"],
            technician_payout_sar=split["technician_payout_sar"],
            reserve_sar=split["reserve_sar"],
            created_at=datetime.now(timezone.utc),
        )
    )


def record_promo_redemption(
    db: Session,
    user_id: UUID,
    promotion_id: UUID,
    booking_id: UUID,
    discount_sar: float,
) -> None:
    db.add(
        PromotionRedemption(
            id=uuid4(),
            user_id=user_id,
            promotion_id=promotion_id,
            booking_id=booking_id,
            discount_sar=discount_sar,
            redeemed_at=datetime.now(timezone.utc),
        )
    )


def redeem_loyalty_reward(
    db: Session, user: User, reward_slug: str
) -> tuple[float, int]:
    reward = db.scalar(
        select(LoyaltyReward).where(
            LoyaltyReward.slug == reward_slug,
            LoyaltyReward.is_active.is_(True),
        )
    )
    if not reward:
        raise ValueError("المكافأة غير موجودة")
    if user.loyalty_points < reward.points_cost:
        raise ValueError("رصيد النقاط غير كافٍ")

    user.loyalty_points -= reward.points_cost
    db.add(
        LoyaltyTransaction(
            id=uuid4(),
            user_id=user.id,
            booking_id=None,
            points=-reward.points_cost,
            reason_ar=f'استبدال: {reward.title_ar}',
            created_at=datetime.now(timezone.utc),
        )
    )
    db.flush()
    return float(reward.discount_sar), reward.points_cost


def subscribe_membership(db: Session, user: User, plan_slug: str) -> UserMembership:
    plan = db.scalar(
        select(MembershipPlan).where(
            MembershipPlan.slug == plan_slug,
            MembershipPlan.is_active.is_(True),
        )
    )
    if not plan:
        raise ValueError("خطة الاشتراك غير موجودة")

    existing = db.scalars(
        select(UserMembership).where(
            UserMembership.user_id == user.id,
            UserMembership.status == "active",
        )
    ).all()
    for m in existing:
        m.status = "cancelled"

    expires_at = None
    if plan.billing_period == "monthly":
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    elif plan.billing_period == "yearly":
        expires_at = datetime.now(timezone.utc) + timedelta(days=365)

    membership = UserMembership(
        id=uuid4(),
        user_id=user.id,
        plan_id=plan.id,
        status="active",
        started_at=datetime.now(timezone.utc),
        expires_at=expires_at,
        created_at=datetime.now(timezone.utc),
    )
    db.add(membership)
    db.flush()
    return membership


def get_monetization_summary(db: Session, user: User) -> dict:
    from app.models import Booking

    plan = get_membership_plan_for_user(db, user.id)
    membership = get_active_membership(db, user.id)

    savings = db.scalar(
        select(
            func.coalesce(
                func.sum(
                    Booking.membership_discount_sar
                    + Booking.discount_sar
                    + Booking.points_discount_sar
                ),
                0,
            )
        ).where(Booking.user_id == user.id)
    ) or 0

    return {
        "membership": {
            "plan_slug": plan.slug if plan else "free",
            "plan_name_ar": plan.name_ar if plan else "مجاني",
            "discount_percent": plan.discount_percent if plan else 0,
            "priority_booking": plan.priority_booking if plan else False,
            "expires_at": membership.expires_at if membership else None,
        },
        "loyalty": {
            "balance": user.loyalty_points,
            "points_per_dinar": POINTS_PER_DINAR,
            "redeemable_dinar": round(user.loyalty_points / POINTS_PER_DINAR, 1),
        },
        "packages_owned": 0,
        "lifetime_savings_sar": float(savings),
    }
