-- Driver types, tow driver vendor account, fares, pending job pool dispatch

UPDATE technicians SET driver_type = 'service'
WHERE id = 'g0000000-0000-4000-8000-000000000001';

UPDATE technicians SET driver_type = 'tow'
WHERE id = 'g0000000-0000-4000-8000-000000000002';

-- Tow driver vendor + user (سعد السطحة)
INSERT INTO vendors (
    id, business_name, contact_name, email, phone, city,
    status, technician_id, approved_at, approved_by,
    base_lat, base_lng, service_radius_km
) VALUES (
    'v0000000-0000-4000-8000-000000000003',
    'سطحة سعد',
    'سعد السطحة',
    'saad.tow@example.com',
    '+966551234567',
    'الرياض',
    'approved',
    'g0000000-0000-4000-8000-000000000002',
    NOW() - INTERVAL '14 days',
    'admin',
    24.7680000,
    46.7320000,
    25.0
) ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, full_name, email, phone, avatar_initials, loyalty_points)
VALUES (
    'a0000000-0000-4000-8000-000000000003',
    'سعد السطحة',
    'saad.tow@example.com',
    '+966551234567',
    'س',
    0
) ON CONFLICT (phone) DO NOTHING;

INSERT INTO user_roles (user_id, role_id, granted_by)
SELECT 'a0000000-0000-4000-8000-000000000003', 'r0000000-0000-4000-8000-000000000003', 'seed'
WHERE EXISTS (SELECT 1 FROM users WHERE id = 'a0000000-0000-4000-8000-000000000003')
ON CONFLICT DO NOTHING;

INSERT INTO user_vendor_links (user_id, vendor_id)
SELECT 'a0000000-0000-4000-8000-000000000003', 'v0000000-0000-4000-8000-000000000003'
WHERE EXISTS (SELECT 1 FROM users WHERE id = 'a0000000-0000-4000-8000-000000000003')
ON CONFLICT DO NOTHING;

-- Fare defaults on existing dispatch
UPDATE towing_dispatches
SET base_fare_sar = 75.00,
    per_km_rate_sar = 8.00,
    total_fare_sar = ROUND(75.00 + COALESCE(total_route_km, 0) * 8.00, 2)
WHERE reference = 'TOW-2026-001';

-- Pending dispatch for driver job pool
INSERT INTO bookings (
    id, reference, user_id, service_id, vehicle_id, address_id,
    payment_method_id, scheduled_at, service_price_sar, discount_sar, total_sar, status
) VALUES (
    'i0000000-0000-4000-8000-000000000003',
    'RST-2026-TOW2',
    'a0000000-0000-4000-8000-000000000001',
    'f0000000-0000-4000-8000-000000000007',
    'b0000000-0000-4000-8000-000000000001',
    'c0000000-0000-4000-8000-000000000001',
    NOW() + INTERVAL '2 hours',
    250.00, 0.00, 250.00,
    'confirmed'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO towing_dispatches (
    id, reference, booking_id, user_id,
    pickup_label, pickup_lat, pickup_lng,
    dropoff_label, dropoff_lat, dropoff_lng,
    status, total_route_km, base_fare_sar, per_km_rate_sar, total_fare_sar
) VALUES (
    'td000000-0000-4000-8000-000000000002',
    'TOW-2026-002',
    'i0000000-0000-4000-8000-000000000003',
    'a0000000-0000-4000-8000-000000000001',
    'موقع العطل · العليا',
    24.7135517,
    46.6752957,
    'ورشة روستو · النخيل',
    24.7742650,
    46.7385860,
    'pending',
    8.20,
    75.00,
    8.00,
    140.60
) ON CONFLICT (id) DO NOTHING;

INSERT INTO towing_dispatch_events (id, dispatch_id, status, label_ar, occurred_at, metadata)
VALUES (
    'tde00000-0000-4000-8000-000000000010',
    'td000000-0000-4000-8000-000000000002',
    'pending',
    'طلب سحب جديد',
    NOW() - INTERVAL '5 minutes',
    '{}'
) ON CONFLICT (id) DO NOTHING;
