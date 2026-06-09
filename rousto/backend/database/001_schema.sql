-- Rousto Auto Care — PostgreSQL schema
-- See docs/01_DATABASE_SCHEMA.md for full specification

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── ENUM types ──────────────────────────────────────────────────────────────

CREATE TYPE payment_method_type AS ENUM (
    'mada', 'apple_pay', 'visa', 'mastercard'
);

CREATE TYPE discount_type AS ENUM (
    'percentage', 'fixed_amount'
);

CREATE TYPE booking_status AS ENUM (
    'pending',
    'confirmed',
    'technician_assigned',
    'en_route',
    'in_progress',
    'completed',
    'cancelled'
);

CREATE TYPE payment_status AS ENUM (
    'pending', 'captured', 'refunded', 'failed'
);

-- ── Tables ──────────────────────────────────────────────────────────────────

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(20)  NOT NULL UNIQUE,
    avatar_initials CHAR(1),
    loyalty_points  INTEGER NOT NULL DEFAULT 0 CHECK (loyalty_points >= 0),
    locale          VARCHAR(5) NOT NULL DEFAULT 'ar',
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE vehicles (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    make          VARCHAR(60) NOT NULL,
    model         VARCHAR(60) NOT NULL,
    year          SMALLINT NOT NULL CHECK (year BETWEEN 1990 AND 2100),
    color         VARCHAR(40),
    plate_number  VARCHAR(20) NOT NULL,
    is_default    BOOLEAN NOT NULL DEFAULT false,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE service_categories (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug       VARCHAR(40) NOT NULL UNIQUE,
    name_ar    VARCHAR(80) NOT NULL,
    sort_order SMALLINT NOT NULL DEFAULT 0,
    is_active  BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE services (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id      UUID NOT NULL REFERENCES service_categories(id),
    slug             VARCHAR(60) NOT NULL UNIQUE,
    name_ar          VARCHAR(120) NOT NULL,
    subtitle_ar      VARCHAR(200),
    icon_key         VARCHAR(40),
    price_sar        NUMERIC(10, 2) NOT NULL CHECK (price_sar >= 0),
    duration_minutes SMALLINT NOT NULL CHECK (duration_minutes > 0),
    is_active        BOOLEAN NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE addresses (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    label      VARCHAR(40) NOT NULL,
    district   VARCHAR(80) NOT NULL,
    city       VARCHAR(60) NOT NULL DEFAULT 'الرياض',
    latitude   NUMERIC(10, 7),
    longitude  NUMERIC(10, 7),
    is_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE payment_methods (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type       payment_method_type NOT NULL,
    last_four  CHAR(4),
    label_ar   VARCHAR(60) NOT NULL,
    is_default BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE technicians (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       VARCHAR(120) NOT NULL,
    phone           VARCHAR(20) NOT NULL UNIQUE,
    rating          NUMERIC(2, 1) NOT NULL DEFAULT 5.0 CHECK (rating BETWEEN 0 AND 5),
    avatar_initials CHAR(1),
    is_available    BOOLEAN NOT NULL DEFAULT true,
    current_lat     NUMERIC(10, 7),
    current_lng     NUMERIC(10, 7),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE promotions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code                VARCHAR(30) NOT NULL UNIQUE,
    title_ar            VARCHAR(120) NOT NULL,
    description_ar      VARCHAR(300),
    discount_type       discount_type NOT NULL,
    discount_value      NUMERIC(10, 2) NOT NULL CHECK (discount_value > 0),
    min_order_sar       NUMERIC(10, 2) NOT NULL DEFAULT 0,
    max_uses_per_user   SMALLINT NOT NULL DEFAULT 1,
    starts_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    ends_at             TIMESTAMPTZ,
    is_active           BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE bookings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference           VARCHAR(12) NOT NULL UNIQUE,
    user_id             UUID NOT NULL REFERENCES users(id),
    service_id          UUID NOT NULL REFERENCES services(id),
    vehicle_id          UUID NOT NULL REFERENCES vehicles(id),
    address_id          UUID NOT NULL REFERENCES addresses(id),
    payment_method_id   UUID REFERENCES payment_methods(id),
    technician_id       UUID REFERENCES technicians(id),
    promotion_id        UUID REFERENCES promotions(id),
    scheduled_at        TIMESTAMPTZ NOT NULL,
    service_price_sar   NUMERIC(10, 2) NOT NULL CHECK (service_price_sar >= 0),
    discount_sar        NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (discount_sar >= 0),
    total_sar           NUMERIC(10, 2) NOT NULL CHECK (total_sar >= 0),
    status              booking_status NOT NULL DEFAULT 'pending',
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE booking_status_events (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id  UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    status      booking_status NOT NULL,
    label_ar    VARCHAR(120) NOT NULL,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata    JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE payments (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id  UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    amount_sar  NUMERIC(10, 2) NOT NULL CHECK (amount_sar >= 0),
    status      payment_status NOT NULL DEFAULT 'pending',
    gateway_ref VARCHAR(100),
    paid_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE loyalty_transactions (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES bookings(id) ON DELETE SET NULL,
    points     INTEGER NOT NULL,
    reason_ar  VARCHAR(200) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE testimonials (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID REFERENCES users(id) ON DELETE SET NULL,
    author_name  VARCHAR(80) NOT NULL,
    city         VARCHAR(60) NOT NULL,
    quote_ar     TEXT NOT NULL,
    rating       SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    is_published BOOLEAN NOT NULL DEFAULT false,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ── Indexes ─────────────────────────────────────────────────────────────────

CREATE INDEX idx_vehicles_user ON vehicles(user_id);
CREATE INDEX idx_addresses_user ON addresses(user_id);
CREATE INDEX idx_payment_methods_user ON payment_methods(user_id);
CREATE INDEX idx_services_category ON services(category_id) WHERE is_active;
CREATE INDEX idx_bookings_user_created ON bookings(user_id, created_at DESC);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_technician ON bookings(technician_id, status)
    WHERE technician_id IS NOT NULL;
CREATE INDEX idx_booking_events_booking ON booking_status_events(booking_id, occurred_at);
CREATE INDEX idx_loyalty_user ON loyalty_transactions(user_id, created_at DESC);

-- ── Triggers ────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER bookings_updated_at
    BEFORE UPDATE ON bookings
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
