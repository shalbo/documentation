-- Password login + payment-only OTP verification

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS password_hash VARCHAR(128);

CREATE TABLE payment_intents (
    id              UUID PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount_lyd      NUMERIC(12, 2) NOT NULL,
    gateway         VARCHAR(20) NOT NULL,
    order_type      VARCHAR(40) NOT NULL,
    order_ref_id    UUID,
    vendor_id       UUID REFERENCES vendors(id) ON DELETE SET NULL,
    return_url      TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'pending_otp'
                    CHECK (status IN ('pending_otp', 'processing', 'completed', 'expired', 'failed')),
    gateway_payment_id UUID REFERENCES gateway_payments(id) ON DELETE SET NULL,
    otp_verified_at TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_payment_intents_user ON payment_intents (user_id, status);

CREATE TABLE otp_codes (
    id          UUID PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_id    UUID NOT NULL REFERENCES payment_intents(id) ON DELETE CASCADE,
    code_hash   VARCHAR(128) NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    is_used     BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_otp_codes_order ON otp_codes (order_id, is_used);
