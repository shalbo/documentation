-- Libyan market VIN decoder reference (WMI+VDS prefixes)

CREATE TABLE vin_decoders (
    id          UUID PRIMARY KEY,
    vin_prefix  VARCHAR(11) NOT NULL UNIQUE,
    make        VARCHAR(60) NOT NULL,
    model       VARCHAR(80) NOT NULL,
    year_range  VARCHAR(24),
    engine      VARCHAR(120),
    market      VARCHAR(40) NOT NULL DEFAULT 'libya',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vin_decoders_prefix ON vin_decoders (vin_prefix);
CREATE INDEX idx_vin_decoders_make_model ON vin_decoders (make, model);
