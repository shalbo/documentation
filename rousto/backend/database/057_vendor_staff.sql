-- Vendor / workshop sub-accounts (staff)

CREATE TABLE vendor_staff (
    id              UUID PRIMARY KEY,
    vendor_id       UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    name            VARCHAR(120) NOT NULL,
    phone           VARCHAR(20) NOT NULL,
    password_hash   VARCHAR(128) NOT NULL,
    role            VARCHAR(20) NOT NULL
                    CHECK (role IN ('manager', 'sales', 'accountant')),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (vendor_id, phone)
);

CREATE INDEX idx_vendor_staff_vendor ON vendor_staff (vendor_id, is_active);
CREATE INDEX idx_vendor_staff_phone ON vendor_staff (phone);

ALTER TABLE auth_refresh_tokens
    ALTER COLUMN user_id DROP NOT NULL;

ALTER TABLE auth_refresh_tokens
    ADD COLUMN IF NOT EXISTS vendor_staff_id UUID REFERENCES vendor_staff(id) ON DELETE CASCADE;

CREATE INDEX IF NOT EXISTS idx_auth_refresh_staff ON auth_refresh_tokens (vendor_staff_id);
