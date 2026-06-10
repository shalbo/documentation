-- CitySeeder — Libyan cities (West, East, South)

INSERT INTO cities (id, name_ar, name_en, region, is_active) VALUES
    ('c2000000-0000-4000-8000-000000000001', 'طرابلس', 'Tripoli', 'West', true),
    ('c2000000-0000-4000-8000-000000000002', 'مصراتة', 'Misrata', 'West', true),
    ('c2000000-0000-4000-8000-000000000003', 'الزاوية', 'Az Zawiyah', 'West', true),
    ('c2000000-0000-4000-8000-000000000004', 'الخمس', 'Al Khums', 'West', true),
    ('c2000000-0000-4000-8000-000000000005', 'زليتن', 'Zliten', 'West', true),
    ('c2000000-0000-4000-8000-000000000006', 'غريان', 'Ghariyan', 'West', true),
    ('c2000000-0000-4000-8000-000000000007', 'صبراتة', 'Sabratha', 'West', true),
    ('c2000000-0000-4000-8000-000000000008', 'صرمان', 'Surman', 'West', true),
    ('c2000000-0000-4000-8000-000000000009', 'ترهونة', 'Tarhuna', 'West', true),
    ('c2000000-0000-4000-8000-00000000000a', 'مسلاتة', 'Msallata', 'West', true),
    ('c2000000-0000-4000-8000-00000000000b', 'بني وليد', 'Bani Walid', 'West', true),
    ('c2000000-0000-4000-8000-00000000000c', 'نالوت', 'Nalut', 'West', true),
    ('c2000000-0000-4000-8000-00000000000d', 'يفرن', 'Yafren', 'West', true),
    ('c2000000-0000-4000-8000-00000000000e', 'زوارة', 'Zuwara', 'West', true),
    ('c2000000-0000-4000-8000-00000000000f', 'بنغازي', 'Benghazi', 'East', true),
    ('c2000000-0000-4000-8000-000000000010', 'البيضاء', 'Al Bayda', 'East', true),
    ('c2000000-0000-4000-8000-000000000011', 'طبرق', 'Tobruk', 'East', true),
    ('c2000000-0000-4000-8000-000000000012', 'درنة', 'Derna', 'East', true),
    ('c2000000-0000-4000-8000-000000000013', 'أجدابيا', 'Ajdabiya', 'East', true),
    ('c2000000-0000-4000-8000-000000000014', 'المرج', 'Al Marj', 'East', true),
    ('c2000000-0000-4000-8000-000000000015', 'شحات', 'Shahat', 'East', true),
    ('c2000000-0000-4000-8000-000000000016', 'الكفرة', 'Al Kufra', 'East', true),
    ('c2000000-0000-4000-8000-000000000017', 'سبها', 'Sebha', 'South', true),
    ('c2000000-0000-4000-8000-000000000018', 'غات', 'Ghat', 'South', true),
    ('c2000000-0000-4000-8000-000000000019', 'أوباري', 'Ubari', 'South', true),
    ('c2000000-0000-4000-8000-00000000001a', 'مرزق', 'Murzuk', 'South', true),
    ('c2000000-0000-4000-8000-00000000001b', 'الشاطئ', 'Al Shati', 'South', true),
    ('c2000000-0000-4000-8000-00000000001c', 'الجفرة', 'Al Jufra', 'South', true)
ON CONFLICT (name_en) DO UPDATE SET
    name_ar = EXCLUDED.name_ar,
    region = EXCLUDED.region,
    is_active = true,
    updated_at = NOW();

-- ربط مسارات الشحن بين المدن (طرابلس ⇄ مصراتة)
UPDATE intercity_shipping_rates SET
    origin_city_id = 'c2000000-0000-4000-8000-000000000001',
    destination_city_id = 'c2000000-0000-4000-8000-000000000002'
WHERE origin_city = 'طرابلس' AND destination_city = 'مصراتة';

UPDATE intercity_shipping_rates SET
    origin_city_id = 'c2000000-0000-4000-8000-000000000002',
    destination_city_id = 'c2000000-0000-4000-8000-000000000001'
WHERE origin_city = 'مصراتة' AND destination_city = 'طرابلس';
