-- Default split rule (15% / 75% / 10%)

INSERT INTO split_rules (
    id, slug, name_ar, platform_rate, technician_rate, reserve_rate, is_default
) VALUES (
    'sr000000-0000-4000-8000-000000000001',
    'default',
    'التقسيم الافتراضي',
    0.1500,
    0.7500,
    0.1000,
    true
);

-- Split legs for seed booking payment (RST-2026-001 · net 90 دينار)
INSERT INTO payment_split_legs (
    id, payment_id, booking_id, rule_id, recipient_type, recipient_id,
    amount_sar, rate_applied, status, released_at
)
SELECT
    'psl00000-0000-4000-8000-000000000001',
    p.id,
    'i0000000-0000-4000-8000-000000000001',
    'sr000000-0000-4000-8000-000000000001',
    'platform',
    NULL,
    13.50,
    0.1500,
    'released',
    NOW() - INTERVAL '3 hours'
FROM payments p
WHERE p.booking_id = 'i0000000-0000-4000-8000-000000000001'
UNION ALL
SELECT
    'psl00000-0000-4000-8000-000000000002',
    p.id,
    'i0000000-0000-4000-8000-000000000001',
    'sr000000-0000-4000-8000-000000000001',
    'technician',
    'g0000000-0000-4000-8000-000000000001',
    67.50,
    0.7500,
    'held',
    NULL
FROM payments p
WHERE p.booking_id = 'i0000000-0000-4000-8000-000000000001'
UNION ALL
SELECT
    'psl00000-0000-4000-8000-000000000003',
    p.id,
    'i0000000-0000-4000-8000-000000000001',
    'sr000000-0000-4000-8000-000000000001',
    'reserve',
    NULL,
    9.00,
    0.1000,
    'held',
    NULL
FROM payments p
WHERE p.booking_id = 'i0000000-0000-4000-8000-000000000001';
