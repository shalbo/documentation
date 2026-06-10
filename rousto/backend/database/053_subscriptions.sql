-- Vendor subscriptions + tier search priority + profile tier link

ALTER TABLE tiers
    ADD COLUMN IF NOT EXISTS search_priority SMALLINT NOT NULL DEFAULT 100;

CREATE TABLE IF NOT EXISTS subscriptions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_id       UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    tier_id         UUID NOT NULL REFERENCES tiers(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'expired', 'cancelled', 'pending')),
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ,
    payment_method  VARCHAR(40),
    payment_note    TEXT,
    upgraded_by     VARCHAR(80),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_vendor ON subscriptions (vendor_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions (status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_expires ON subscriptions (expires_at);

ALTER TABLE vendor_profiles
    ADD COLUMN IF NOT EXISTS tier_id UUID REFERENCES tiers(id);

CREATE INDEX IF NOT EXISTS idx_vendor_profiles_tier ON vendor_profiles (tier_id);
