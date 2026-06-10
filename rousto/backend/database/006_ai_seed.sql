-- Demo scan for development (سعود العتيبي — dashboard warning)

INSERT INTO vehicle_scans (
    id, user_id, vehicle_id, scan_type, status, created_at, completed_at
) VALUES (
    's0000000-0000-4000-8000-000000000001',
    'a0000000-0000-4000-8000-000000000001',
    'b0000000-0000-4000-8000-000000000001',
    'dashboard_warning',
    'completed',
    NOW() - INTERVAL '2 days',
    NOW() - INTERVAL '2 days'
);

INSERT INTO scan_images (id, scan_id, storage_key, mime_type, sort_order)
VALUES (
    'si000000-0000-4000-8000-000000000001',
    's0000000-0000-4000-8000-000000000001',
    'demo/dashboard_warning.jpg',
    'image/jpeg',
    0
);

INSERT INTO scan_findings (
    id, scan_id, code, label_ar, severity, confidence, suggested_service_id, details
) VALUES (
    'sf000000-0000-4000-8000-000000000001',
    's0000000-0000-4000-8000-000000000001',
    'check_engine',
    'ضوء فحص المحرك — يُنصح بفحص إلكتروني',
    'medium',
    0.820,
    'f0000000-0000-4000-8000-000000000006',
    '{"source": "seed"}'
);
