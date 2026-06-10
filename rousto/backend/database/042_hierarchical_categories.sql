-- Hierarchical spare parts catalog (tree categories)

ALTER TABLE part_categories
    ADD COLUMN IF NOT EXISTS parent_id UUID REFERENCES part_categories(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS icon_key VARCHAR(40);

CREATE INDEX IF NOT EXISTS idx_part_categories_parent
    ON part_categories (parent_id, is_active)
    WHERE parent_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_part_categories_roots
    ON part_categories (sort_order)
    WHERE parent_id IS NULL AND is_active = true;
