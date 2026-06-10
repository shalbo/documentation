-- FAQ entries

INSERT INTO support_faq (id, slug, category, question_ar, answer_ar, sort_order) VALUES
    ('faq00000-0000-4000-8000-000000000001', 'how-to-book', 'booking',
     'كيف أحجز خدمة؟',
     'اختر الخدمة من التطبيق، حدّد السيارة والعنوان وطريقة الدفع، ثم أكّد الحجز.',
     1),
    ('faq00000-0000-4000-8000-000000000002', 'track-technician', 'booking',
     'كيف أتتبّع الفني؟',
     'من شاشة التتبّع أو صفحة خريطة التوصيل يمكنك رؤية موقع الفني والوقت المتوقع للوصول.',
     2),
    ('faq00000-0000-4000-8000-000000000003', 'payment-methods', 'payment',
     'ما طرق الدفع المتاحة؟',
     'ندعم مدى، آبل باي، فيزا، وماستركارد. جميع المبالغ بالدينار.',
     3),
    ('faq00000-0000-4000-8000-000000000004', 'cancel-booking', 'booking',
     'هل يمكن إلغاء الحجز؟',
     'يمكن الإلغاء قبل تعيين الفني من التطبيق أو عبر فتح تذكرة دعم.',
     4),
    ('faq00000-0000-4000-8000-000000000005', 'account-security', 'account',
     'كيف أحمي حسابي؟',
     'فعّل تنبيهات تسجيل الدخول، ولا تشارك رمز التحقق. أبلغ فوراً عن أي نشاط مشبوه.',
     5);

-- Security profile for seed user

INSERT INTO user_security_profiles (user_id, login_alerts_enabled, last_security_review_at)
VALUES (
    'a0000000-0000-4000-8000-000000000001',
    true,
    NOW() - INTERVAL '7 days'
);

-- Sample support ticket

INSERT INTO support_tickets (
    id, reference, user_id, booking_id, category, priority, status, subject, created_at, updated_at
) VALUES (
    'st000000-0000-4000-8000-000000000001',
    'SUP-2026-001',
    'a0000000-0000-4000-8000-000000000001',
    'i0000000-0000-4000-8000-000000000001',
    'booking',
    'high',
    'in_progress',
    'تأخير في وصول الفني',
    NOW() - INTERVAL '2 hours',
    NOW() - INTERVAL '30 minutes'
);

INSERT INTO support_ticket_messages (id, ticket_id, author_type, author_label, message, created_at) VALUES
    ('stm00000-0000-4000-8000-000000000001', 'st000000-0000-4000-8000-000000000001',
     'customer', 'سعود العتيبي',
     'الفني تأخر أكثر من 30 دقيقة عن الموعد المحدد. أرجو المتابعة.',
     NOW() - INTERVAL '2 hours'),
    ('stm00000-0000-4000-8000-000000000002', 'st000000-0000-4000-8000-000000000001',
     'admin', 'فريق الدعم',
     'نعتذر عن التأخير. تواصلنا مع الفني وهو في الطريق إليك الآن.',
     NOW() - INTERVAL '30 minutes');

-- Security audit events

INSERT INTO security_audit_logs (id, user_id, event_type, severity, ip_address, metadata, created_at) VALUES
    ('sal00000-0000-4000-8000-000000000001', 'a0000000-0000-4000-8000-000000000001',
     'session_started', 'info', '192.168.1.10', '{"source": "flutter_app"}', NOW() - INTERVAL '3 hours'),
    ('sal00000-0000-4000-8000-000000000002', 'a0000000-0000-4000-8000-000000000001',
     'ticket_created', 'info', '192.168.1.10', '{"reference": "SUP-2026-001"}', NOW() - INTERVAL '2 hours'),
    ('sal00000-0000-4000-8000-000000000003', NULL,
     'admin_access', 'warn', '10.0.0.5', '{"endpoint": "/admin/support/tickets"}', NOW() - INTERVAL '1 hour');
