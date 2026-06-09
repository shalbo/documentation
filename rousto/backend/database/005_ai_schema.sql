-- Rousto — AI vehicle scan tables

CREATE TABLE vehicle_scans (
    id            UUID PRIMARY KEY,
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vehicle_id    UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    scan_type     VARCHAR(40) NOT NULL,
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    notes         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at  TIMESTAMPTZ
);

CREATE INDEX idx_vehicle_scans_user ON vehicle_scans (user_id, created_at DESC);
CREATE INDEX idx_vehicle_scans_vehicle ON vehicle_scans (vehicle_id);

CREATE TABLE scan_images (
    id            UUID PRIMARY KEY,
    scan_id       UUID NOT NULL REFERENCES vehicle_scans(id) ON DELETE CASCADE,
    storage_key   VARCHAR(255) NOT NULL,
    mime_type     VARCHAR(80) NOT NULL,
    sort_order    SMALLINT NOT NULL DEFAULT 0,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scan_images_scan ON scan_images (scan_id, sort_order);

CREATE TABLE scan_findings (
    id                    UUID PRIMARY KEY,
    scan_id               UUID NOT NULL REFERENCES vehicle_scans(id) ON DELETE CASCADE,
    code                  VARCHAR(60) NOT NULL,
    label_ar              VARCHAR(200) NOT NULL,
    severity              VARCHAR(20) NOT NULL
                          CHECK (severity IN ('low', 'medium', 'high')),
    confidence            NUMERIC(4, 3) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    suggested_service_id  UUID REFERENCES services(id) ON DELETE SET NULL,
    details               JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_scan_findings_scan ON scan_findings (scan_id);

ALTER TABLE bookings
    ADD COLUMN scan_id UUID REFERENCES vehicle_scans(id) ON DELETE SET NULL;

CREATE INDEX idx_bookings_scan ON bookings (scan_id) WHERE scan_id IS NOT NULL;
