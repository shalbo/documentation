-- Store visibility toggle (vendor portal — hide inventory from customer app)

ALTER TABLE vendors
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true;

ALTER TABLE vendor_profiles
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true;

CREATE INDEX idx_vendors_store_active ON vendors (is_active, status)
    WHERE status = 'approved';
