-- Vendor subscription tiers (dynamic platform packages)

CREATE TABLE tiers (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug                  VARCHAR(40) NOT NULL UNIQUE,
    name_ar               VARCHAR(80) NOT NULL,
    name_en               VARCHAR(80) NOT NULL,
    price                 NUMERIC(10, 2) NOT NULL DEFAULT 0 CHECK (price >= 0),
    products_limit        INTEGER NOT NULL DEFAULT 50 CHECK (products_limit = -1 OR products_limit >= 0),
    allow_excel_upload    BOOLEAN NOT NULL DEFAULT false,
    allow_vin_decoder     BOOLEAN NOT NULL DEFAULT false,
    allow_unlimited_chat  BOOLEAN NOT NULL DEFAULT false,
    has_gold_badge        BOOLEAN NOT NULL DEFAULT false,
    sort_order            SMALLINT NOT NULL DEFAULT 0,
    is_active             BOOLEAN NOT NULL DEFAULT true,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tiers_sort_order ON tiers (sort_order);
CREATE INDEX idx_tiers_is_active ON tiers (is_active);

ALTER TABLE vendors
    ADD COLUMN tier_id UUID REFERENCES tiers(id);

CREATE INDEX idx_vendors_tier_id ON vendors (tier_id);
