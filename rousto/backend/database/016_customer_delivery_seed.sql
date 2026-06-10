-- Extra GPS trail point for customer delivery map demo (closer to customer)

INSERT INTO technician_location_updates (id, technician_id, booking_id, lat, lng, recorded_at)
VALUES (
    'tl000000-0000-4000-8000-000000000003',
    'g0000000-0000-4000-8000-000000000001',
    'i0000000-0000-4000-8000-000000000001',
    24.7732000,
    46.7378000,
    NOW() - INTERVAL '5 minutes'
);

UPDATE technicians
SET current_lat = 24.7732000, current_lng = 46.7378000
WHERE id = 'g0000000-0000-4000-8000-000000000001';

UPDATE booking_status_events
SET metadata = jsonb_set(
    COALESCE(metadata, '{}'::jsonb),
    '{distance_km}',
    '0.65'::jsonb,
    true
)
WHERE booking_id = 'i0000000-0000-4000-8000-000000000001'
  AND status = 'en_route';
