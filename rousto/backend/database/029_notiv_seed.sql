-- Rousto — NOTIV seed: templates + sample inbox for dev user

INSERT INTO notification_templates (id, slug, category, title_template, body_template, action_url_template) VALUES
    ('nt000000-0000-4000-8000-000000000001', 'booking_status', 'booking',
     'تحديث حجز {{reference}}', '{{label}}', '/web/tracking.html?ref={{reference}}'),
    ('nt000000-0000-4000-8000-000000000002', 'support_reply', 'support',
     'رد على تذكرة {{reference}}', '{{preview}}', '/web/support.html?ticket={{reference}}'),
    ('nt000000-0000-4000-8000-000000000003', 'towing_status', 'towing',
     'تحديث سحب {{reference}}', '{{label}}', '/web/towing-map.html?ref={{reference}}'),
    ('nt000000-0000-4000-8000-000000000004', 'promo_offer', 'promo',
     '{{title}}', '{{body}}', '{{action_url}}'),
    ('nt000000-0000-4000-8000-000000000005', 'security_alert', 'security',
     'تنبيه أمان', '{{message}}', '/web/account.html'),
    ('nt000000-0000-4000-8000-000000000006', 'system_announcement', 'system',
     '{{title}}', '{{body}}', NULL);

INSERT INTO user_notification_preferences (user_id, category, push_enabled, in_app_enabled) VALUES
    ('a0000000-0000-4000-8000-000000000001', 'booking', true, true),
    ('a0000000-0000-4000-8000-000000000001', 'support', true, true),
    ('a0000000-0000-4000-8000-000000000001', 'towing', true, true),
    ('a0000000-0000-4000-8000-000000000001', 'promo', true, true),
    ('a0000000-0000-4000-8000-000000000001', 'security', true, true),
    ('a0000000-0000-4000-8000-000000000001', 'system', true, true);

INSERT INTO notifications (id, user_id, category, template_slug, title, body, data_json, action_url, is_read, created_at) VALUES
    ('nf000000-0000-4000-8000-000000000001',
     'a0000000-0000-4000-8000-000000000001', 'booking', 'booking_status',
     'تحديث حجز RST-2026-001', 'تم تأكيد الحجز',
     '{"booking_ref": "RST-2026-001", "status": "confirmed"}',
     '/web/delivery-map.html', false, now() - interval '2 hours'),
    ('nf000000-0000-4000-8000-000000000002',
     'a0000000-0000-4000-8000-000000000001', 'promo', 'promo_offer',
     'عرض الصيف', 'خصم 20% على غسيل السيارة الكامل',
     '{"campaign_slug": "summer-wash"}',
     '/web/booking.html', true, now() - interval '1 day');
