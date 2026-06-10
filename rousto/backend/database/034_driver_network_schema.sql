-- Rousto — Logistics & Driver Network (Module 24)

ALTER TABLE technicians
    ADD COLUMN IF NOT EXISTS driver_type VARCHAR(20) NOT NULL DEFAULT 'service'
        CHECK (driver_type IN ('service', 'tow', 'courier'));

ALTER TABLE towing_dispatches
    ADD COLUMN IF NOT EXISTS base_fare_sar NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS per_km_rate_sar NUMERIC(6, 2),
    ADD COLUMN IF NOT EXISTS total_fare_sar NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS customer_rating SMALLINT
        CHECK (customer_rating IS NULL OR customer_rating BETWEEN 1 AND 5),
    ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS cancel_reason VARCHAR(200);

CREATE INDEX IF NOT EXISTS idx_technicians_driver_type
    ON technicians (driver_type, is_available);

CREATE INDEX IF NOT EXISTS idx_towing_dispatches_technician
    ON towing_dispatches (technician_id, status);
