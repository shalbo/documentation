-- Towing vehicle subtype: tow truck vs flatbed (nullable for legacy courier/tow rows)

ALTER TABLE driver_profiles
    ADD COLUMN IF NOT EXISTS vehicle_type VARCHAR(20)
    CHECK (vehicle_type IS NULL OR vehicle_type IN ('tow_truck', 'flatbed'));

CREATE INDEX IF NOT EXISTS idx_driver_profiles_vehicle_type
    ON driver_profiles (vehicle_type)
    WHERE vehicle_type IS NOT NULL;
