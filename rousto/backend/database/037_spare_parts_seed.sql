-- Spare parts catalog, inventory, sample booking part, tow vehicle

INSERT INTO part_suppliers (id, slug, name_ar, name_en, is_oem) VALUES
    ('ps000000-0000-4000-8000-000000000001', 'toyota-oem', 'تويوتا OEM', 'Toyota OEM', true),
    ('ps000000-0000-4000-8000-000000000002', 'bosch', 'بوش', 'Bosch', false),
    ('ps000000-0000-4000-8000-000000000003', 'mobil', 'موبيل', 'Mobil', false),
    ('ps000000-0000-4000-8000-000000000004', 'ngk', 'NGK', 'NGK', false);

INSERT INTO part_categories (id, slug, name_ar, name_en, sort_order) VALUES
    ('pc000000-0000-4000-8000-000000000001', 'filters', 'فلاتر وزيوت', 'Filters & Oils', 1),
    ('pc000000-0000-4000-8000-000000000002', 'brakes', 'فرامل', 'Brakes', 2),
    ('pc000000-0000-4000-8000-000000000003', 'electrical', 'كهرباء وبطاريات', 'Electrical', 3),
    ('pc000000-0000-4000-8000-000000000004', 'belts', 'سيور ومضخات', 'Belts & Pumps', 4);

INSERT INTO parts (
    id, part_number, slug, name_ar, name_en, category_id, supplier_id,
    is_oem, price_sar, warranty_months, vehicle_compatibility
) VALUES
    ('pt000000-0000-4000-8000-000000000001', 'TOY-04152-YZZA1',
     'toyota-oil-filter-camry', 'فلتر زيت تويوتا كامري', 'Toyota Camry Oil Filter',
     'pc000000-0000-4000-8000-000000000001', 'ps000000-0000-4000-8000-000000000001',
     true, 45.00, 6, '[{"make":"Toyota","model":"Camry","years":"2018-2024"}]'),
    ('pt000000-0000-4000-8000-000000000002', 'MOB-5W30-4L',
     'mobil-5w30-4l', 'زيت موبيل 5W-30 (4 لتر)', 'Mobil 5W-30 4L',
     'pc000000-0000-4000-8000-000000000001', 'ps000000-0000-4000-8000-000000000003',
     false, 120.00, 6, '[{"make":"*","model":"*","years":"*"}]'),
    ('pt000000-0000-4000-8000-000000000003', 'BOSCH-0986AB1234',
     'bosch-brake-pads-front', 'فحمات فرامل أمامية بوش', 'Bosch Front Brake Pads',
     'pc000000-0000-4000-8000-000000000002', 'ps000000-0000-4000-8000-000000000002',
     false, 185.00, 6, '[{"make":"Toyota","model":"Corolla","years":"2016-2023"}]'),
    ('pt000000-0000-4000-8000-000000000004', 'NGK-LFR5A-11',
     'ngk-spark-plug', 'شمعة احتراق NGK', 'NGK Spark Plug LFR5A-11',
     'pc000000-0000-4000-8000-000000000003', 'ps000000-0000-4000-8000-000000000004',
     false, 35.00, 6, '[{"make":"*","model":"*","years":"*"}]'),
    ('pt000000-0000-4000-8000-000000000005', 'TOY-90915-YZZD2',
     'toyota-air-filter', 'فلتر هواء تويوتا', 'Toyota Air Filter',
     'pc000000-0000-4000-8000-000000000001', 'ps000000-0000-4000-8000-000000000001',
     true, 55.00, 6, '[{"make":"Toyota","model":"*","years":"2015-2024"}]'),
    ('pt000000-0000-4000-8000-000000000006', 'BOSCH-A068S',
     'bosch-battery-68ah', 'بطارية بوش 68 أمبير', 'Bosch 68Ah Battery',
     'pc000000-0000-4000-8000-000000000003', 'ps000000-0000-4000-8000-000000000002',
     false, 420.00, 12, '[{"make":"*","model":"*","years":"*"}]');

INSERT INTO part_inventory (id, vendor_id, part_id, qty_available, cost_sar) VALUES
    ('pi000000-0000-4000-8000-000000000001', 'v0000000-0000-4000-8000-000000000001',
     'pt000000-0000-4000-8000-000000000001', 25, 32.00),
    ('pi000000-0000-4000-8000-000000000002', 'v0000000-0000-4000-8000-000000000001',
     'pt000000-0000-4000-8000-000000000002', 40, 95.00),
    ('pi000000-0000-4000-8000-000000000003', 'v0000000-0000-4000-8000-000000000001',
     'pt000000-0000-4000-8000-000000000003', 12, 140.00);

INSERT INTO booking_parts (
    id, booking_id, part_id, vendor_id, qty, unit_price_sar, warranty_expires_at
) VALUES (
    'bp000000-0000-4000-8000-000000000001',
    'i0000000-0000-4000-8000-000000000001',
    'pt000000-0000-4000-8000-000000000001',
    'v0000000-0000-4000-8000-000000000001',
    1, 45.00,
    NOW() + INTERVAL '6 months'
);

INSERT INTO tow_vehicles (id, technician_id, vehicle_type, plate_number, max_capacity_kg) VALUES
    ('tv000000-0000-4000-8000-000000000001',
     'g0000000-0000-4000-8000-000000000002',
     'flatbed', 'أ ب ج 1234', 3500.00);
