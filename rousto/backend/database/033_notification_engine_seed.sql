-- Seed sample dispatch log entries for dev admin dashboard

INSERT INTO notification_broadcasts (
    id, reference, category, title, body, target_segment,
    recipients_count, push_sent_count, in_app_count, created_by
) VALUES (
    'nb000000-0000-4000-8000-000000000001',
    'BCAST-2026-001',
    'system',
    'مرحباً بك في روستو',
    'شكراً لانضمامك — احجز أول خدمة بخصم ROUSTO',
    'all_users',
    1, 0, 1,
    'seed'
);

INSERT INTO notification_dispatch_log (
    id, event_source, notification_id, broadcast_id, user_id,
    category, template_slug, title, channel, push_sent, in_app_created, status
) VALUES
    ('nd000000-0000-4000-8000-000000000001', 'booking_hook',
     'nf000000-0000-4000-8000-000000000001', NULL,
     'a0000000-0000-4000-8000-000000000001',
     'booking', 'booking_status', 'تحديث حجز RST-2026-001', 'both', false, true, 'delivered'),
    ('nd000000-0000-4000-8000-000000000002', 'admin_broadcast', NULL,
     'nb000000-0000-4000-8000-000000000001',
     'a0000000-0000-4000-8000-000000000001',
     'system', NULL, 'مرحباً بك في روستو', 'in_app', false, true, 'delivered');
