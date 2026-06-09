-- Rousto — seed data matching the Flutter/HTML app mock content

-- Fixed UUIDs for reproducible development references
-- User: سعود العتيبي
INSERT INTO users (id, full_name, email, phone, avatar_initials, loyalty_points)
VALUES (
    'a0000000-0000-4000-8000-000000000001',
    'سعود العتيبي',
    'saud@example.com',
    '+966501234567',
    'س',
    320
);

INSERT INTO vehicles (id, user_id, make, model, year, color, plate_number, is_default)
VALUES (
    'b0000000-0000-4000-8000-000000000001',
    'a0000000-0000-4000-8000-000000000001',
    'تويوتا', 'كامري', 2022, 'أبيض', 'أ ب ج 1234', true
),
(
    'b0000000-0000-4000-8000-000000000002',
    'a0000000-0000-4000-8000-000000000001',
    'هيونداي', 'سوناتا', 2020, 'فضي', 'د هـ و 5678', false
);

INSERT INTO addresses (id, user_id, label, district, city, latitude, longitude, is_default)
VALUES (
    'c0000000-0000-4000-8000-000000000001',
    'a0000000-0000-4000-8000-000000000001',
    'المنزل', 'حي النخيل', 'الرياض', 24.7742650, 46.7385860, true
),
(
    'c0000000-0000-4000-8000-000000000002',
    'a0000000-0000-4000-8000-000000000001',
    'العمل', 'حي العليا', 'الرياض', 24.7135517, 46.6752957, false
);

INSERT INTO payment_methods (id, user_id, type, last_four, label_ar, is_default)
VALUES (
    'd0000000-0000-4000-8000-000000000001',
    'a0000000-0000-4000-8000-000000000001',
    'mada', '4421', 'مدى **** 4421', true
);

-- Service categories
INSERT INTO service_categories (id, slug, name_ar, sort_order) VALUES
    ('e0000000-0000-4000-8000-000000000001', 'all',     'الكل',    0),
    ('e0000000-0000-4000-8000-000000000002', 'oil',     'زيت',     1),
    ('e0000000-0000-4000-8000-000000000003', 'tires',   'إطارات',  2),
    ('e0000000-0000-4000-8000-000000000004', 'brakes',  'فرامل',   3),
    ('e0000000-0000-4000-8000-000000000005', 'ac',      'تكييف',   4),
    ('e0000000-0000-4000-8000-000000000006', 'electrical', 'كهرباء', 5);

INSERT INTO services (id, category_id, slug, name_ar, subtitle_ar, icon_key, price_sar, duration_minutes) VALUES
    ('f0000000-0000-4000-8000-000000000001', 'e0000000-0000-4000-8000-000000000002',
     'oil-change', 'تغيير الزيت والفلاتر', 'زيت أصلي + فحص شامل', 'oil_barrel', 120.00, 45),
    ('f0000000-0000-4000-8000-000000000002', 'e0000000-0000-4000-8000-000000000003',
     'tires', 'الإطارات والترصيص', 'موازنة وتبديل الإطارات', 'tire_repair', 90.00, 30),
    ('f0000000-0000-4000-8000-000000000003', 'e0000000-0000-4000-8000-000000000004',
     'brakes', 'نظام الفرامل', 'فحص واستبدال الفحمات', 'disc_full', 180.00, 60),
    ('f0000000-0000-4000-8000-000000000004', 'e0000000-0000-4000-8000-000000000005',
     'ac', 'تكييف وتبريد', 'تعبئة فريون وصيانة', 'ac_unit', 150.00, 50),
    ('f0000000-0000-4000-8000-000000000005', 'e0000000-0000-4000-8000-000000000006',
     'battery', 'البطارية والكهرباء', 'فحص وتركيب بطاريات', 'battery_charging', 110.00, 40),
    ('f0000000-0000-4000-8000-000000000006', 'e0000000-0000-4000-8000-000000000006',
     'diagnostics', 'فحص كمبيوتر شامل', 'تشخيص إلكتروني دقيق', 'laptop_mac', 75.00, 35);

INSERT INTO technicians (id, full_name, phone, rating, avatar_initials, is_available, current_lat, current_lng)
VALUES (
    'g0000000-0000-4000-8000-000000000001',
    'أحمد الفني',
    '+966509876543',
    4.9,
    'أ',
    true,
    24.7700000,
    46.7350000
);

INSERT INTO promotions (id, code, title_ar, description_ar, discount_type, discount_value, min_order_sar, max_uses_per_user)
VALUES
    ('h0000000-0000-4000-8000-000000000001', 'ROUSTO',
     'خصم 25٪ على أول حجز', 'استخدم كود ROUSTO عند الدفع', 'percentage', 25.00, 50.00, 1),
    ('h0000000-0000-4000-8000-000000000002', 'GOLD2026',
     'باقة الصيانة الذهبية', 'وفّر حتى 120 دينار سنوياً', 'fixed_amount', 120.00, 200.00, 3);

-- Active booking (oil change — matches tracking screen)
INSERT INTO bookings (
    id, reference, user_id, service_id, vehicle_id, address_id,
    payment_method_id, technician_id, promotion_id,
    scheduled_at, service_price_sar, discount_sar, total_sar, status
) VALUES (
    'i0000000-0000-4000-8000-000000000001',
    'RST-2026-001',
    'a0000000-0000-4000-8000-000000000001',
    'f0000000-0000-4000-8000-000000000001',
    'b0000000-0000-4000-8000-000000000001',
    'c0000000-0000-4000-8000-000000000001',
    'd0000000-0000-4000-8000-000000000001',
    'g0000000-0000-4000-8000-000000000001',
    'h0000000-0000-4000-8000-000000000001',
    now() + interval '2 hours',
    120.00, 30.00, 90.00,
    'en_route'
);

INSERT INTO booking_status_events (booking_id, status, label_ar, occurred_at, metadata) VALUES
    ('i0000000-0000-4000-8000-000000000001', 'confirmed',            'تم تأكيد الحجز',       now() - interval '3 hours', '{}'),
    ('i0000000-0000-4000-8000-000000000001', 'technician_assigned',  'تم تعيين الفني',       now() - interval '2 hours 57 minutes', '{}'),
    ('i0000000-0000-4000-8000-000000000001', 'en_route',             'الفني في الطريق إليك', now() - interval '10 minutes', '{"eta_minutes": 12}');

INSERT INTO payments (booking_id, amount_sar, status, gateway_ref, paid_at)
VALUES (
    'i0000000-0000-4000-8000-000000000001',
    90.00, 'captured', 'PAY-2026-001', now() - interval '3 hours'
);

INSERT INTO loyalty_transactions (user_id, booking_id, points, reason_ar) VALUES
    ('a0000000-0000-4000-8000-000000000001', NULL, 320, 'رصيد نقاط ترحيبي');

INSERT INTO testimonials (author_name, city, quote_ar, rating, is_published) VALUES
    ('فهد السبيعي', 'الرياض', 'خدمة ممتازة والفني وصل في الوقت المحدد. أنصح بها بشدة.', 5, true),
    ('نورة القحطاني', 'جدة', 'سهولة الحجز والدفع من التطبيق وفّرت علي وقت طويل.', 5, true),
    ('عبدالله الشمري', 'الدمام', 'جودة الخدمة عالية والأسعار منافسة. شكراً روستو!', 4, true);
