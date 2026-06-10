-- Hybrid shipping engine — local delivery vs intercity (separate from booking wallets)

CREATE TABLE intercity_shipping_rates (
    id                  UUID PRIMARY KEY,
    origin_city         VARCHAR(60) NOT NULL,
    destination_city    VARCHAR(60) NOT NULL,
    flat_fee_sar        NUMERIC(10, 2) NOT NULL CHECK (flat_fee_sar >= 0),
    carrier_name        VARCHAR(80) NOT NULL,
    carrier_slug        VARCHAR(40) NOT NULL,
    eta_days            SMALLINT NOT NULL DEFAULT 2,
    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (origin_city, destination_city)
);

CREATE TABLE part_orders (
    id                      UUID PRIMARY KEY,
    reference               VARCHAR(12) NOT NULL UNIQUE,
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    part_id                 UUID NOT NULL REFERENCES parts(id),
    vendor_id               UUID NOT NULL REFERENCES vendors(id),
    qty                     SMALLINT NOT NULL DEFAULT 1 CHECK (qty > 0),
    subtotal_sar            NUMERIC(10, 2) NOT NULL,
    shipping_type           VARCHAR(24) NOT NULL
                            CHECK (shipping_type IN ('local_delivery', 'intercity_shipping')),
    shipping_fee_sar        NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_sar               NUMERIC(10, 2) NOT NULL,
    origin_city             VARCHAR(60),
    destination_city        VARCHAR(60) NOT NULL,
    dest_lat                NUMERIC(10, 7),
    dest_lng                NUMERIC(10, 7),
    courier_technician_id   UUID REFERENCES technicians(id) ON DELETE SET NULL,
    intercity_carrier       VARCHAR(80),
    status                  VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_part_orders_user ON part_orders (user_id, status);
CREATE INDEX idx_part_orders_vendor ON part_orders (vendor_id, status);

-- Settlements for part orders (does not alter payment_split_legs / split_rules)
CREATE TABLE part_order_settlements (
    id              UUID PRIMARY KEY,
    part_order_id   UUID NOT NULL REFERENCES part_orders(id) ON DELETE CASCADE,
    recipient_type  VARCHAR(20) NOT NULL
                    CHECK (recipient_type IN ('platform', 'vendor', 'courier', 'carrier')),
    recipient_id    UUID,
    amount_sar      NUMERIC(10, 2) NOT NULL CHECK (amount_sar >= 0),
    label_ar        VARCHAR(80) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'held'
                    CHECK (status IN ('pending', 'held', 'released', 'paid')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_part_order_settlements_order ON part_order_settlements (part_order_id);
