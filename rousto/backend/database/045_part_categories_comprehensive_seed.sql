-- Comprehensive main & sub category tree (equivalent to Laravel CategorySeeder)

-- إعادة تسمية الأقسام المسطّحة القديمة لتجنب تعارض slug
UPDATE part_categories SET slug = 'filters-legacy', is_active = false
    WHERE id = 'pc000000-0000-4000-8000-000000000001';
UPDATE part_categories SET slug = 'brakes-legacy', is_active = false
    WHERE id = 'pc000000-0000-4000-8000-000000000002';
UPDATE part_categories SET slug = 'electrical-legacy', is_active = false
    WHERE id = 'pc000000-0000-4000-8000-000000000003';
UPDATE part_categories SET slug = 'belts-legacy', is_active = false
    WHERE id = 'pc000000-0000-4000-8000-000000000004';

-- 1. الأقسام الرئيسية
INSERT INTO part_categories (id, slug, name_ar, name_en, sort_order, parent_id, icon_key) VALUES
    ('c1000000-0000-4000-8000-000000000001', 'engine', 'المحرك وملحقاته', 'Engine & Accessories', 1, NULL, 'engine'),
    ('c1000000-0000-4000-8000-000000000002', 'suspension', 'منظومة الحركة والفرامل', 'Drivetrain & Brakes', 2, NULL, 'suspension'),
    ('c1000000-0000-4000-8000-000000000003', 'electrical', 'الكهرباء والإلكترونيات', 'Electrical & Electronics', 3, NULL, 'electrical'),
    ('c1000000-0000-4000-8000-000000000004', 'fuel', 'منظومة الوقود والعادم', 'Fuel & Exhaust', 4, NULL, 'fuel'),
    ('c1000000-0000-4000-8000-000000000005', 'ac', 'التكييف والتبريد', 'AC & Cooling', 5, NULL, 'ac'),
    ('c1000000-0000-4000-8000-000000000006', 'fluids', 'الفلاتر والزيوت والمواد الاستهلاكية', 'Filters, Oils & Consumables', 6, NULL, 'fluids'),
    ('c1000000-0000-4000-8000-000000000007', 'body', 'الهيكل الخارجي والزجاج', 'Body & Glass', 7, NULL, 'body'),
    ('c1000000-0000-4000-8000-000000000008', 'interior', 'الأكسسوارات والقطع الداخلية', 'Interior & Accessories', 8, NULL, 'interior')
ON CONFLICT (slug) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    parent_id = NULL,
    icon_key = EXCLUDED.icon_key,
    is_active = true;

-- 2. الأقسام الفرعية
INSERT INTO part_categories (id, slug, name_ar, name_en, sort_order, parent_id, icon_key) VALUES
    ('c1000000-0000-4000-8000-000000000101', 'engine-internal', 'أجزاء المحرك الداخلية', 'Internal Engine Parts', 1,
     'c1000000-0000-4000-8000-000000000001', 'piston'),
    ('c1000000-0000-4000-8000-000000000102', 'engine-cooling', 'نظام التبريد (Cooling)', 'Cooling System', 2,
     'c1000000-0000-4000-8000-000000000001', 'cooling'),
    ('c1000000-0000-4000-8000-000000000103', 'belts-timing', 'السيور والكاتينات', 'Belts & Timing', 3,
     'c1000000-0000-4000-8000-000000000001', 'belt'),
    ('c1000000-0000-4000-8000-000000000104', 'engine-mounts', 'قواعد المحرك والكمبيو', 'Engine Mounts & ECU', 4,
     'c1000000-0000-4000-8000-000000000001', 'engine_mount'),
    ('c1000000-0000-4000-8000-000000000105', 'brakes', 'منظومة الفرامل (Brakes)', 'Brake System', 1,
     'c1000000-0000-4000-8000-000000000002', 'brake_pad'),
    ('c1000000-0000-4000-8000-000000000106', 'suspension-parts', 'منظومة التعليق (Suspension)', 'Suspension System', 2,
     'c1000000-0000-4000-8000-000000000002', 'shock'),
    ('c1000000-0000-4000-8000-000000000107', 'steering', 'منظومة التوجيه (Steering)', 'Steering System', 3,
     'c1000000-0000-4000-8000-000000000002', 'steering'),
    ('c1000000-0000-4000-8000-000000000108', 'wheels-drivetrain', 'العجلات ونقل الحركة', 'Wheels & Drivetrain', 4,
     'c1000000-0000-4000-8000-000000000002', 'wheel'),
    ('c1000000-0000-4000-8000-000000000109', 'ignition', 'منظومة التشغيل والاحتراق', 'Ignition System', 1,
     'c1000000-0000-4000-8000-000000000003', 'spark_plug'),
    ('c1000000-0000-4000-8000-000000000110', 'sensors-ecu', 'الحساسات والكمبيوترات', 'Sensors & ECU', 2,
     'c1000000-0000-4000-8000-000000000003', 'sensor'),
    ('c1000000-0000-4000-8000-000000000111', 'lighting', 'الإنارة والمصابيح', 'Lighting', 3,
     'c1000000-0000-4000-8000-000000000003', 'headlight'),
    ('c1000000-0000-4000-8000-000000000112', 'fuel-system', 'منظومة الوقود وضخ البنزين', 'Fuel System & Pumps', 1,
     'c1000000-0000-4000-8000-000000000004', 'fuel_pump'),
    ('c1000000-0000-4000-8000-000000000113', 'exhaust', 'منظومة الهواء والعادم (الشكمان)', 'Air & Exhaust', 2,
     'c1000000-0000-4000-8000-000000000004', 'exhaust'),
    ('c1000000-0000-4000-8000-000000000114', 'ac-compressor', 'كمبروسرات وراديترات المكيف', 'AC Compressors & Radiators', 1,
     'c1000000-0000-4000-8000-000000000005', 'ac_compressor'),
    ('c1000000-0000-4000-8000-000000000115', 'ac-filters', 'فلاتر وثلاجات التكييف', 'AC Filters & Evaporators', 2,
     'c1000000-0000-4000-8000-000000000005', 'ac_filter'),
    ('c1000000-0000-4000-8000-000000000116', 'maintenance-filters', 'فلاتر الصيانة الدورية', 'Maintenance Filters', 1,
     'c1000000-0000-4000-8000-000000000006', 'oil_filter'),
    ('c1000000-0000-4000-8000-000000000117', 'oils-fluids', 'الزيوت والسوائل التشغيلية', 'Oils & Operating Fluids', 2,
     'c1000000-0000-4000-8000-000000000006', 'oil_barrel'),
    ('c1000000-0000-4000-8000-000000000118', 'body-panels', 'قطع الهيكل والبرواكني', 'Body Panels & Bumpers', 1,
     'c1000000-0000-4000-8000-000000000007', 'bumper'),
    ('c1000000-0000-4000-8000-000000000119', 'glass-mirrors', 'الزجاج والمرايا الجانبية', 'Glass & Side Mirrors', 2,
     'c1000000-0000-4000-8000-000000000007', 'mirror'),
    ('c1000000-0000-4000-8000-000000000120', 'accessories', 'كماليات وأكسسوارات السيارة', 'Car Accessories', 1,
     'c1000000-0000-4000-8000-000000000008', 'accessory'),
    ('c1000000-0000-4000-8000-000000000121', 'interior-salon', 'قطع الصالون الداخلي وأحزمة الأمان', 'Interior & Seat Belts', 2,
     'c1000000-0000-4000-8000-000000000008', 'seat_belt')
ON CONFLICT (slug) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    name_en = EXCLUDED.name_en,
    sort_order = EXCLUDED.sort_order,
    parent_id = EXCLUDED.parent_id,
    icon_key = EXCLUDED.icon_key,
    is_active = true;

-- إعادة ربط القطع التجريبية بالأقسام الفرعية الجديدة
UPDATE parts SET category_id = 'c1000000-0000-4000-8000-000000000116'
    WHERE id IN (
        'pt000000-0000-4000-8000-000000000001',
        'pt000000-0000-4000-8000-000000000005'
    );
UPDATE parts SET category_id = 'c1000000-0000-4000-8000-000000000117'
    WHERE id = 'pt000000-0000-4000-8000-000000000002';
UPDATE parts SET category_id = 'c1000000-0000-4000-8000-000000000105'
    WHERE id = 'pt000000-0000-4000-8000-000000000003';
UPDATE parts SET category_id = 'c1000000-0000-4000-8000-000000000109'
    WHERE id = 'pt000000-0000-4000-8000-000000000004';
UPDATE parts SET category_id = 'c1000000-0000-4000-8000-000000000110'
    WHERE id = 'pt000000-0000-4000-8000-000000000006';

-- تعطيل جذور وأقسام فرعية قديمة من migration 042
UPDATE part_categories SET is_active = false
    WHERE slug IN (
        'cat-engines', 'cat-brakes', 'cat-filters', 'cat-electrical', 'cat-belts',
        'engine-oil', 'air-filters', 'spark-plugs', 'brake-discs', 'timing-belts', 'engine-parts'
    );
