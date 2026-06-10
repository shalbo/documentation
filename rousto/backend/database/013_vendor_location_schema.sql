-- Rousto — vendor map & location (base + service radius)

ALTER TABLE vendors
    ADD COLUMN base_lat NUMERIC(10, 7),
    ADD COLUMN base_lng NUMERIC(10, 7),
    ADD COLUMN service_radius_km NUMERIC(5, 2) NOT NULL DEFAULT 15.00
        CHECK (service_radius_km > 0 AND service_radius_km <= 100);

CREATE INDEX idx_vendors_base_location
    ON vendors (base_lat, base_lng)
    WHERE status = 'approved' AND base_lat IS NOT NULL;
