-- Rousto — vendor onboarding & financials

CREATE TABLE vendors (
    id               UUID PRIMARY KEY,
    business_name    VARCHAR(120) NOT NULL,
    contact_name     VARCHAR(120) NOT NULL,
    email            VARCHAR(255) NOT NULL UNIQUE,
    phone            VARCHAR(20) NOT NULL UNIQUE,
    city             VARCHAR(60) NOT NULL DEFAULT 'الرياض',
    national_id      VARCHAR(20),
    commercial_reg   VARCHAR(40),
    status           VARCHAR(20) NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('draft', 'pending', 'approved', 'rejected', 'suspended')),
    technician_id    UUID REFERENCES technicians(id) ON DELETE SET NULL,
    rejection_reason TEXT,
    approved_at      TIMESTAMPTZ,
    approved_by      VARCHAR(80),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vendors_status ON vendors (status, created_at DESC);
CREATE INDEX idx_vendors_technician ON vendors (technician_id) WHERE technician_id IS NOT NULL;

CREATE TABLE vendor_bank_accounts (
    id              UUID PRIMARY KEY,
    vendor_id       UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    bank_name       VARCHAR(80) NOT NULL,
    account_holder  VARCHAR(120) NOT NULL,
    iban            VARCHAR(34) NOT NULL,
    is_primary      BOOLEAN NOT NULL DEFAULT true,
    is_verified     BOOLEAN NOT NULL DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_vendor_bank_primary
    ON vendor_bank_accounts (vendor_id) WHERE is_primary = true;

CREATE INDEX idx_vendor_bank_vendor ON vendor_bank_accounts (vendor_id);
