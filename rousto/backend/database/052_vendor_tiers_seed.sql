-- Default vendor tiers (products_limit: -1 = unlimited)

INSERT INTO tiers (
    id, slug, name_ar, name_en, price, products_limit,
    allow_excel_upload, allow_vin_decoder, allow_unlimited_chat, has_gold_badge,
    sort_order, is_active
) VALUES
(
    'a1000000-0000-4000-8000-000000000001',
    'starter',
    'باقة البداية',
    'Starter',
    0,
    50,
    false,
    false,
    false,
    false,
    1,
    true
),
(
    'a1000000-0000-4000-8000-000000000002',
    'pro',
    'باقة احترافية',
    'Pro',
    99,
    500,
    true,
    true,
    false,
    false,
    2,
    true
),
(
    'a1000000-0000-4000-8000-000000000003',
    'gold',
    'باقة ذهبية',
    'Gold',
    299,
    3000,
    true,
    true,
    true,
    true,
    3,
    true
),
(
    'a1000000-0000-4000-8000-000000000004',
    'enterprise',
    'باقة المؤسسات',
    'Enterprise',
    999,
    -1,
    true,
    true,
    true,
    true,
    4,
    true
);

-- Assign default tiers to seed vendors
UPDATE vendors
SET tier_id = 'a1000000-0000-4000-8000-000000000003'
WHERE id = 'v0000000-0000-4000-8000-000000000001';

UPDATE vendors
SET tier_id = 'a1000000-0000-4000-8000-000000000001'
WHERE id = 'v0000000-0000-4000-8000-000000000002';
