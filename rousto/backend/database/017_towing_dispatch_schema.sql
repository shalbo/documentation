-- Rousto — towing dispatch map

CREATE TABLE towing_dispatches (
    id              UUID PRIMARY KEY,
    reference       VARCHAR(12) NOT NULL UNIQUE,
    booking_id      UUID NOT NULL UNIQUE REFERENCES bookings(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    technician_id   UUID REFERENCES technicians(id) ON DELETE SET NULL,
    pickup_label    VARCHAR(120) NOT NULL,
    pickup_lat      NUMERIC(10, 7) NOT NULL,
    pickup_lng      NUMERIC(10, 7) NOT NULL,
    dropoff_label   VARCHAR(120) NOT NULL,
    dropoff_lat     NUMERIC(10, 7) NOT NULL,
    dropoff_lng     NUMERIC(10, 7) NOT NULL,
    status          VARCHAR(30) NOT NULL DEFAULT 'pending'
                    CHECK (status IN (
                        'pending', 'dispatched', 'en_route_pickup', 'at_pickup',
                        'en_route_dropoff', 'completed', 'cancelled'
                    )),
    total_route_km  NUMERIC(6, 2),
    notes           TEXT,
    dispatched_at   TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_towing_dispatches_status ON towing_dispatches (status, created_at DESC);
CREATE INDEX idx_towing_dispatches_user ON towing_dispatches (user_id, created_at DESC);

CREATE TABLE towing_dispatch_events (
    id              UUID PRIMARY KEY,
    dispatch_id     UUID NOT NULL REFERENCES towing_dispatches(id) ON DELETE CASCADE,
    status          VARCHAR(30) NOT NULL,
    label_ar        VARCHAR(120) NOT NULL,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata        JSONB NOT NULL DEFAULT '{}'
);

CREATE INDEX idx_towing_dispatch_events_dispatch
    ON towing_dispatch_events (dispatch_id, occurred_at);
