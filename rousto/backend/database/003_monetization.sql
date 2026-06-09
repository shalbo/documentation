-- Rousto — Business monetization schema
-- See docs/04_BUSINESS_MONETIZATION.md

CREATE TYPE membership_status AS ENUM ('active', 'expired', 'cancelled');
CREATE TYPE billing_period AS ENUM ('monthly', 'yearly', 'one_time');

-- ── Membership plans ────────────────────────────────────────────────────────

CREATE TABLE membership_plans (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug              VARCHAR(40) NOT NULL UNIQUE,
    name_ar           VARCHAR(80) NOT NULL,
    description_ar    VARCHAR(300),
    price_sar         NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (price_sar >= 0),
    billing_period    billing_period NOT NULL DEFAULT 'monthly',
    discount_percent  SMALLINT NOT NULL DEFAULT 0 CHECK (discount_percent BETWEEN 0 AND 100),
    priority_booking  BOOLEAN NOT NULL DEFAULT false,
    free_inspection   BOOLEAN NOT NULL DEFAULT false,
    sort_order        SMALLINT NOT NULL DEFAULT 0,
    is_active         BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE user_memberships (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_id     UUID NOT NULL REFERENCES membership_plans(id),
    status      membership_status NOT NULL DEFAULT 'active',
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_user_memberships_user ON user_memberships(user_id, status);

-- ── Service packages ────────────────────────────────────────────────────────

CREATE TABLE service_packages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(40) NOT NULL UNIQUE,
    name_ar         VARCHAR(120) NOT NULL,
    description_ar  VARCHAR(300),
    price_sar       NUMERIC(10, 2) NOT NULL CHECK (price_sar > 0),
    visits_count    SMALLINT NOT NULL DEFAULT 1,
    validity_days   SMALLINT NOT NULL DEFAULT 365,
    savings_sar     NUMERIC(10, 2) NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE package_items (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    package_id  UUID NOT NULL REFERENCES service_packages(id) ON DELETE CASCADE,
    service_id  UUID NOT NULL REFERENCES services(id),
    quantity    SMALLINT NOT NULL DEFAULT 1
);

CREATE TABLE user_packages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    package_id      UUID NOT NULL REFERENCES service_packages(id),
    visits_remaining SMALLINT NOT NULL,
    purchased_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL
);

-- ── Loyalty rewards catalog ─────────────────────────────────────────────────

CREATE TABLE loyalty_rewards (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug            VARCHAR(40) NOT NULL UNIQUE,
    title_ar        VARCHAR(120) NOT NULL,
    description_ar  VARCHAR(300),
    points_cost     INTEGER NOT NULL CHECK (points_cost > 0),
    discount_sar    NUMERIC(10, 2) NOT NULL CHECK (discount_sar > 0),
    is_active       BOOLEAN NOT NULL DEFAULT true
);

-- ── Promotion redemptions ───────────────────────────────────────────────────

CREATE TABLE promotion_redemptions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id),
    promotion_id  UUID NOT NULL REFERENCES promotions(id),
    booking_id    UUID REFERENCES bookings(id),
    discount_sar  NUMERIC(10, 2) NOT NULL,
    redeemed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_promo_redemptions_user ON promotion_redemptions(user_id);

-- ── Booking revenue split ───────────────────────────────────────────────────

CREATE TABLE booking_revenue (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id          UUID NOT NULL UNIQUE REFERENCES bookings(id) ON DELETE CASCADE,
    gross_sar           NUMERIC(10, 2) NOT NULL,
    membership_discount_sar NUMERIC(10, 2) NOT NULL DEFAULT 0,
    promo_discount_sar  NUMERIC(10, 2) NOT NULL DEFAULT 0,
    points_discount_sar NUMERIC(10, 2) NOT NULL DEFAULT 0,
    net_sar             NUMERIC(10, 2) NOT NULL,
    platform_fee_sar    NUMERIC(10, 2) NOT NULL,
    technician_payout_sar NUMERIC(10, 2) NOT NULL,
    reserve_sar         NUMERIC(10, 2) NOT NULL DEFAULT 0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Extend bookings with monetization fields
ALTER TABLE bookings
    ADD COLUMN membership_discount_sar NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ADD COLUMN points_discount_sar NUMERIC(10, 2) NOT NULL DEFAULT 0;
