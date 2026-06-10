-- Rousto — logistics: technician location history

CREATE TABLE technician_location_updates (
    id              UUID PRIMARY KEY,
    technician_id   UUID NOT NULL REFERENCES technicians(id) ON DELETE CASCADE,
    booking_id      UUID REFERENCES bookings(id) ON DELETE SET NULL,
    lat             NUMERIC(10, 7) NOT NULL,
    lng             NUMERIC(10, 7) NOT NULL,
    recorded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tech_location_technician
    ON technician_location_updates (technician_id, recorded_at DESC);

CREATE INDEX idx_tech_location_booking
    ON technician_location_updates (booking_id, recorded_at DESC)
    WHERE booking_id IS NOT NULL;
