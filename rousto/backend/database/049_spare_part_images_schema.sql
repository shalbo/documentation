-- Spare part images (bulk URL import + ZIP archive linking)

CREATE TABLE spare_part_images (
    id            UUID PRIMARY KEY,
    part_id       UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    storage_path  VARCHAR(300) NOT NULL,
    public_url    VARCHAR(400) NOT NULL,
    is_primary    BOOLEAN NOT NULL DEFAULT false,
    sort_order    SMALLINT NOT NULL DEFAULT 0,
    source        VARCHAR(20) NOT NULL DEFAULT 'upload'
        CHECK (source IN ('url', 'zip', 'upload')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_spare_part_images_part_id ON spare_part_images (part_id);
CREATE INDEX idx_spare_part_images_primary ON spare_part_images (part_id) WHERE is_primary = true;
