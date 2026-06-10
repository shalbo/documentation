-- Rousto — Critical Architecture Correction: spare parts domain + tow vehicles

CREATE TABLE part_suppliers (
    id          UUID PRIMARY KEY,
    slug        VARCHAR(40) NOT NULL UNIQUE,
    name_ar     VARCHAR(120) NOT NULL,
    name_en     VARCHAR(120),
    is_oem      BOOLEAN NOT NULL DEFAULT false,
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE part_categories (
    id          UUID PRIMARY KEY,
    slug        VARCHAR(40) NOT NULL UNIQUE,
    name_ar     VARCHAR(120) NOT NULL,
    name_en     VARCHAR(120),
    sort_order  SMALLINT NOT NULL DEFAULT 0,
    is_active   BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE parts (
    id                      UUID PRIMARY KEY,
    part_number             VARCHAR(60) NOT NULL UNIQUE,
    slug                    VARCHAR(80) NOT NULL UNIQUE,
    name_ar                 VARCHAR(200) NOT NULL,
    name_en                 VARCHAR(200),
    description_ar          TEXT,
    category_id             UUID NOT NULL REFERENCES part_categories(id),
    supplier_id             UUID REFERENCES part_suppliers(id) ON DELETE SET NULL,
    is_oem                  BOOLEAN NOT NULL DEFAULT false,
    price_sar               NUMERIC(10, 2) NOT NULL,
    warranty_months         SMALLINT NOT NULL DEFAULT 6,
    vehicle_compatibility   JSONB NOT NULL DEFAULT '[]',
    image_url               VARCHAR(300),
    is_active               BOOLEAN NOT NULL DEFAULT true,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_parts_search ON parts (name_ar, name_en, part_number);
CREATE INDEX idx_parts_category ON parts (category_id, is_active);

CREATE TABLE part_inventory (
    id              UUID PRIMARY KEY,
    vendor_id       UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    part_id         UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    qty_available   INTEGER NOT NULL DEFAULT 0 CHECK (qty_available >= 0),
    cost_sar        NUMERIC(10, 2),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (vendor_id, part_id)
);

CREATE TABLE booking_parts (
    id                  UUID PRIMARY KEY,
    booking_id          UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    part_id             UUID NOT NULL REFERENCES parts(id),
    vendor_id           UUID REFERENCES vendors(id) ON DELETE SET NULL,
    qty                 SMALLINT NOT NULL DEFAULT 1 CHECK (qty > 0),
    unit_price_sar      NUMERIC(10, 2) NOT NULL,
    warranty_expires_at TIMESTAMPTZ,
    installed_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_booking_parts_booking ON booking_parts (booking_id);

CREATE TABLE part_warranty_claims (
    id              UUID PRIMARY KEY,
    booking_part_id UUID NOT NULL REFERENCES booking_parts(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'in_review', 'resolved', 'rejected')),
    admin_notes     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE TABLE tow_vehicles (
    id              UUID PRIMARY KEY,
    technician_id   UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    vehicle_type    VARCHAR(20) NOT NULL
                    CHECK (vehicle_type IN ('flatbed', 'wheel_lift', 'carrier')),
    plate_number    VARCHAR(20) NOT NULL,
    max_capacity_kg NUMERIC(8, 2),
    is_active       BOOLEAN NOT NULL DEFAULT true,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tow_vehicles_technician ON tow_vehicles (technician_id);
