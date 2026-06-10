-- Rousto — split payments engine

CREATE TABLE split_rules (
    id               UUID PRIMARY KEY,
    slug             VARCHAR(40) NOT NULL UNIQUE,
    name_ar          VARCHAR(80) NOT NULL,
    platform_rate    NUMERIC(5, 4) NOT NULL CHECK (platform_rate >= 0 AND platform_rate <= 1),
    technician_rate  NUMERIC(5, 4) NOT NULL CHECK (technician_rate >= 0 AND technician_rate <= 1),
    reserve_rate     NUMERIC(5, 4) NOT NULL CHECK (reserve_rate >= 0 AND reserve_rate <= 1),
    is_default       BOOLEAN NOT NULL DEFAULT false,
    is_active        BOOLEAN NOT NULL DEFAULT true,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT split_rules_rates_sum CHECK (
        platform_rate + technician_rate + reserve_rate = 1.0000
    )
);

CREATE UNIQUE INDEX idx_split_rules_default
    ON split_rules (is_default) WHERE is_default = true AND is_active = true;

CREATE TABLE payment_split_legs (
    id              UUID PRIMARY KEY,
    payment_id      UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    booking_id      UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    rule_id         UUID NOT NULL REFERENCES split_rules(id),
    recipient_type  VARCHAR(20) NOT NULL
                    CHECK (recipient_type IN ('platform', 'technician', 'reserve')),
    recipient_id    UUID REFERENCES technicians(id) ON DELETE SET NULL,
    amount_sar      NUMERIC(10, 2) NOT NULL CHECK (amount_sar >= 0),
    rate_applied    NUMERIC(5, 4) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'held'
                    CHECK (status IN ('pending', 'held', 'released', 'paid', 'failed')),
    released_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_split_legs_booking ON payment_split_legs (booking_id);
CREATE INDEX idx_payment_split_legs_payment ON payment_split_legs (payment_id);
CREATE INDEX idx_payment_split_legs_status ON payment_split_legs (status, recipient_type);
