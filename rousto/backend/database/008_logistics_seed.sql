-- Initial location trail for demo technician (أحمد الفني)

INSERT INTO technician_location_updates (id, technician_id, booking_id, lat, lng, recorded_at)
VALUES
    (
        'tl000000-0000-4000-8000-000000000001',
        'g0000000-0000-4000-8000-000000000001',
        'i0000000-0000-4000-8000-000000000001',
        24.7700000,
        46.7350000,
        NOW() - INTERVAL '15 minutes'
    ),
    (
        'tl000000-0000-4000-8000-000000000002',
        'g0000000-0000-4000-8000-000000000001',
        'i0000000-0000-4000-8000-000000000001',
        24.7720000,
        46.7365000,
        NOW() - INTERVAL '10 minutes'
    );
