-- Normalize tiers to standard / professional / enterprise

UPDATE tiers
SET slug = 'standard',
    name_ar = 'باقة قياسية',
    name_en = 'Standard',
    price = 0,
    products_limit = 100,
    allow_excel_upload = false,
    allow_vin_decoder = false,
    allow_unlimited_chat = false,
    has_gold_badge = false,
    search_priority = 100,
    sort_order = 1,
    is_active = true
WHERE slug IN ('starter', 'standard');

UPDATE tiers
SET slug = 'professional',
    name_ar = 'باقة احترافية',
    name_en = 'Professional',
    price = 99,
    products_limit = 500,
    allow_excel_upload = true,
    allow_vin_decoder = true,
    allow_unlimited_chat = false,
    has_gold_badge = false,
    search_priority = 200,
    sort_order = 2,
    is_active = true
WHERE slug IN ('pro', 'professional');

UPDATE tiers
SET slug = 'enterprise',
    name_ar = 'باقة الشركات',
    name_en = 'Enterprise',
    price = 999,
    products_limit = -1,
    allow_excel_upload = true,
    allow_vin_decoder = true,
    allow_unlimited_chat = true,
    has_gold_badge = true,
    search_priority = 300,
    sort_order = 3,
    is_active = true
WHERE slug = 'enterprise';

-- Deactivate legacy gold tier and move vendors to professional
UPDATE vendors
SET tier_id = (SELECT id FROM tiers WHERE slug = 'professional' LIMIT 1)
WHERE tier_id IN (SELECT id FROM tiers WHERE slug = 'gold');

UPDATE tiers SET is_active = false WHERE slug = 'gold';

-- Sync vendor_profiles.tier_id from vendors
UPDATE vendor_profiles vp
SET tier_id = v.tier_id
FROM vendors v
WHERE vp.vendor_id = v.id AND v.tier_id IS NOT NULL;

-- Backfill active subscriptions (1 year from approval)
INSERT INTO subscriptions (vendor_id, tier_id, status, started_at, expires_at, payment_method)
SELECT
    v.id,
    v.tier_id,
    'active',
    COALESCE(v.approved_at, NOW()),
    COALESCE(v.approved_at, NOW()) + INTERVAL '1 year',
    'seed'
FROM vendors v
WHERE v.tier_id IS NOT NULL
  AND v.status = 'approved'
  AND NOT EXISTS (
      SELECT 1 FROM subscriptions s
      WHERE s.vendor_id = v.id AND s.status = 'active'
  );
