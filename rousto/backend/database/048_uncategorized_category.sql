-- Fallback category for bulk uploads with unknown sub_category

INSERT INTO part_categories (id, slug, name_ar, name_en, sort_order, parent_id, icon_key) VALUES
    ('c1000000-0000-4000-8000-000000000009', 'general', 'عام', 'General', 9, NULL, 'folder'),
    ('c1000000-0000-4000-8000-000000000122', 'uncategorized', 'غير مصنف', 'Uncategorized', 1,
     'c1000000-0000-4000-8000-000000000009', 'folder')
ON CONFLICT (slug) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    name_en = EXCLUDED.name_en,
    parent_id = EXCLUDED.parent_id,
    is_active = true;
