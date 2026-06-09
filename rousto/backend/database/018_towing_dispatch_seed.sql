-- Towing category, service, tow driver, booking, and active dispatch

INSERT INTO service_categories (id, slug, name_ar, sort_order) VALUES
    ('e0000000-0000-4000-8000-000000000007', 'towing', 'سحب وإرسال', 6);

INSERT INTO services (id, category_id, slug, name_ar, subtitle_ar, icon_key, price_sar, duration_minutes) VALUES
    ('f0000000-0000-4000-8000-000000000007', 'e0000000-0000-4000-8000-000000000007',
     'towing-recovery', 'سحب وإرسال السيارة', 'سطحة مجهّزة · نقل آمن للورشة', 'local_shipping', 250.00, 90);

INSERT INTO technicians (id, full_name, phone, rating, avatar_initials, is_available, current_lat, current_lng)
VALUES (
    'g0000000-0000-4000-8000-000000000002',
    'سعد السطحة',
    '+966551234567',
    4.8,
    'س',
    true,
    24.7680000,
    46.7320000
);

INSERT INTO bookings (
    id, reference, user_id, service_id, vehicle_id, address_id,
    payment_method_id, technician_id,
    scheduled_at, service_price_sar, discount_sar, total_sar, status
) VALUES (
    'i0000000-0000-4000-8000-000000000002',
    'RST-2026-TOW',
    'a0000000-0000-4000-8000-000000000001',
    'f0000000-0000-4000-8000-000000000007',
    'b0000000-0000-4000-8000-000000000001',
    'c0000000-0000-4000-8000-000000000001',
    'd0000000-0000-4000-8000-000000000001',
    'g0000000-0000-4000-8000-000000000002',
    NOW() + INTERVAL '1 hour',
    250.00, 0.00, 250.00,
    'en_route'
);

INSERT INTO booking_status_events (booking_id, status, label_ar, occurred_at, metadata) VALUES
    ('i0000000-0000-4000-8000-000000000002', 'confirmed', 'تم تأكيد طلب السحب', NOW() - INTERVAL '40 minutes', '{}'),
    ('i0000000-0000-4000-8000-000000000002', 'technician_assigned', 'تم تعيين السطحة', NOW() - INTERVAL '35 minutes', '{}'),
    ('i0000000-0000-4000-8000-000000000002', 'en_route', 'السطحة في الطريق', NOW() - INTERVAL '20 minutes', '{"eta_minutes": 8}');

INSERT INTO towing_dispatches (
    id, reference, booking_id, user_id, technician_id,
    pickup_label, pickup_lat, pickup_lng,
    dropoff_label, dropoff_lat, dropoff_lng,
    status, total_route_km, dispatched_at
) VALUES (
    'td000000-0000-4000-8000-000000000001',
    'TOW-2026-001',
    'i0000000-0000-4000-8000-000000000002',
    'a0000000-0000-4000-8000-000000000001',
    'g0000000-0000-4000-8000-000000000002',
    'موقع العطل · حي النخيل',
    24.7742650,
    46.7385860,
    'ورشة روستو · العليا',
    24.7135517,
    46.6752957,
    'en_route_pickup',
    4.50,
    NOW() - INTERVAL '35 minutes'
);

INSERT INTO towing_dispatch_events (id, dispatch_id, status, label_ar, occurred_at, metadata) VALUES
    ('tde00000-0000-4000-8000-000000000001', 'td000000-0000-4000-8000-000000000001',
     'pending', 'طلب سحب جديد', NOW() - INTERVAL '40 minutes', '{}'),
    ('tde00000-0000-4000-8000-000000000002', 'td000000-0000-4000-8000-000000000001',
     'dispatched', 'تم تعيين سعد السطحة', NOW() - INTERVAL '35 minutes', '{}'),
    ('tde00000-0000-4000-8000-000000000003', 'td000000-0000-4000-8000-000000000001',
     'en_route_pickup', 'متجه لموقع العطل', NOW() - INTERVAL '20 minutes',
     '{"distance_km": 1.2, "eta_minutes": 8}');

INSERT INTO technician_location_updates (id, technician_id, booking_id, lat, lng, recorded_at)
VALUES
    ('tl000000-0000-4000-8000-000000000010', 'g0000000-0000-4000-8000-000000000002',
     'i0000000-0000-4000-8000-000000000002', 24.7650000, 46.7280000, NOW() - INTERVAL '18 minutes'),
    ('tl000000-0000-4000-8000-000000000011', 'g0000000-0000-4000-8000-000000000002',
     'i0000000-0000-4000-8000-000000000002', 24.7680000, 46.7320000, NOW() - INTERVAL '8 minutes');
