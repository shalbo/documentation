-- Libyan cities & regions (delivery zones, intercity shipping, store filters)

CREATE TABLE cities (
    id          UUID PRIMARY KEY,
    name_ar     VARCHAR(80) NOT NULL,
    name_en     VARCHAR(80) NOT NULL UNIQUE,
    region      VARCHAR(20) NOT NULL CHECK (region IN ('West', 'East', 'South')),
    is_active   BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cities_region ON cities (region, is_active);
CREATE INDEX idx_cities_name_ar ON cities (name_ar) WHERE is_active = true;

-- Foreign keys to cities (nullable during migration; string city kept for compat)
ALTER TABLE users
    ADD COLUMN IF NOT EXISTS city_id UUID REFERENCES cities(id) ON DELETE SET NULL;

ALTER TABLE vendors
    ADD COLUMN IF NOT EXISTS city_id UUID REFERENCES cities(id) ON DELETE SET NULL;

ALTER TABLE vendor_profiles
    ADD COLUMN IF NOT EXISTS city_id UUID REFERENCES cities(id) ON DELETE SET NULL;

ALTER TABLE driver_profiles
    ADD COLUMN IF NOT EXISTS city_id UUID REFERENCES cities(id) ON DELETE SET NULL;

ALTER TABLE workshop_profiles
    ADD COLUMN IF NOT EXISTS city_id UUID REFERENCES cities(id) ON DELETE SET NULL;

ALTER TABLE part_orders
    ADD COLUMN IF NOT EXISTS origin_city_id UUID REFERENCES cities(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS destination_city_id UUID REFERENCES cities(id) ON DELETE SET NULL;

ALTER TABLE intercity_shipping_rates
    ADD COLUMN IF NOT EXISTS origin_city_id UUID REFERENCES cities(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS destination_city_id UUID REFERENCES cities(id) ON DELETE SET NULL;

CREATE INDEX idx_vendors_city_id ON vendors (city_id) WHERE city_id IS NOT NULL;
CREATE INDEX idx_part_orders_dest_city ON part_orders (destination_city_id);
