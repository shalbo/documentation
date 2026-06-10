-- Root categories + re-parent existing flat categories as subcategories

INSERT INTO part_categories (id, slug, name_ar, name_en, sort_order, parent_id, icon_key) VALUES
    ('pc000000-0000-4000-8000-000000000010', 'cat-engines', 'محرك وناقل حركة', 'Engine & Drivetrain', 1, NULL, 'engine'),
    ('pc000000-0000-4000-8000-000000000011', 'cat-brakes', 'فرامل وتعليق', 'Brakes & Suspension', 2, NULL, 'brakes'),
    ('pc000000-0000-4000-8000-000000000012', 'cat-filters', 'فلاتر وزيوت', 'Filters & Fluids', 3, NULL, 'filters'),
    ('pc000000-0000-4000-8000-000000000013', 'cat-electrical', 'كهرباء وبطاريات', 'Electrical & Battery', 4, NULL, 'electrical'),
    ('pc000000-0000-4000-8000-000000000014', 'cat-belts', 'سيور ومضخات', 'Belts & Pumps', 5, NULL, 'belts')
ON CONFLICT (id) DO NOTHING;

UPDATE part_categories SET parent_id = 'pc000000-0000-4000-8000-000000000012', icon_key = 'oil_filter'
    WHERE id = 'pc000000-0000-4000-8000-000000000001';
UPDATE part_categories SET parent_id = 'pc000000-0000-4000-8000-000000000011', icon_key = 'brake_pad'
    WHERE id = 'pc000000-0000-4000-8000-000000000002';
UPDATE part_categories SET parent_id = 'pc000000-0000-4000-8000-000000000013', icon_key = 'battery'
    WHERE id = 'pc000000-0000-4000-8000-000000000003';
UPDATE part_categories SET parent_id = 'pc000000-0000-4000-8000-000000000014', icon_key = 'belt'
    WHERE id = 'pc000000-0000-4000-8000-000000000004';

-- Additional subcategories under roots
INSERT INTO part_categories (id, slug, name_ar, name_en, sort_order, parent_id, icon_key) VALUES
    ('pc000000-0000-4000-8000-000000000021', 'engine-oil', 'زيوت محرك', 'Engine Oil', 1,
     'pc000000-0000-4000-8000-000000000012', 'oil_barrel'),
    ('pc000000-0000-4000-8000-000000000022', 'air-filters', 'فلاتر هواء', 'Air Filters', 2,
     'pc000000-0000-4000-8000-000000000012', 'air_filter'),
    ('pc000000-0000-4000-8000-000000000023', 'spark-plugs', 'شمعات احتراق', 'Spark Plugs', 1,
     'pc000000-0000-4000-8000-000000000013', 'spark_plug'),
    ('pc000000-0000-4000-8000-000000000024', 'brake-discs', 'أقراص فرامل', 'Brake Discs', 2,
     'pc000000-0000-4000-8000-000000000011', 'disc'),
    ('pc000000-0000-4000-8000-000000000025', 'timing-belts', 'سيور توقيت', 'Timing Belts', 1,
     'pc000000-0000-4000-8000-000000000014', 'timing_belt'),
    ('pc000000-0000-4000-8000-000000000026', 'engine-parts', 'قطع محرك', 'Engine Parts', 1,
     'pc000000-0000-4000-8000-000000000010', 'piston')
ON CONFLICT (id) DO NOTHING;
