-- VIN ↔ OEM smart linking — junction table for guaranteed fitment by VIN prefix

CREATE TABLE part_vin_compatibilities (
    id          UUID PRIMARY KEY,
    part_id     UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    vin_prefix  VARCHAR(11) NOT NULL CHECK (char_length(vin_prefix) = 11),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (part_id, vin_prefix)
);

CREATE INDEX idx_part_vin_compat_vin_prefix
    ON part_vin_compatibilities (vin_prefix);

CREATE INDEX idx_part_vin_compat_part_id
    ON part_vin_compatibilities (part_id);
