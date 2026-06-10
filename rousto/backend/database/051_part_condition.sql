-- New vs used spare parts condition filter

ALTER TABLE parts
    ADD COLUMN IF NOT EXISTS part_condition VARCHAR(10) NOT NULL DEFAULT 'new'
        CHECK (part_condition IN ('new', 'used'));

CREATE INDEX IF NOT EXISTS idx_parts_condition ON parts (part_condition, is_active);
