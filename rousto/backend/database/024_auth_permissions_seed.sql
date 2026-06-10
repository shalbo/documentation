-- Rousto — Permissions & Auth seed data

INSERT INTO roles (id, slug, name_ar, description_ar) VALUES
    ('r0000000-0000-4000-8000-000000000001', 'customer', 'عميل', 'حجز ومتابعة الخدمات'),
    ('r0000000-0000-4000-8000-000000000002', 'admin', 'مدير', 'صلاحيات إدارية كاملة'),
    ('r0000000-0000-4000-8000-000000000003', 'technician', 'فني', 'بوابة الفني والموقع'),
    ('r0000000-0000-4000-8000-000000000004', 'support', 'دعم', 'إدارة تذاكر العملاء');

INSERT INTO permissions (id, slug, name_ar, resource, action) VALUES
    ('p0000000-0000-4000-8000-000000000001', 'bookings:read', 'قراءة الحجوزات', 'bookings', 'read'),
    ('p0000000-0000-4000-8000-000000000002', 'bookings:create', 'إنشاء حجز', 'bookings', 'create'),
    ('p0000000-0000-4000-8000-000000000003', 'bookings:manage', 'إدارة الحجوزات', 'bookings', 'manage'),
    ('p0000000-0000-4000-8000-000000000004', 'catalog:read', 'قراءة الكتالوج', 'catalog', 'read'),
    ('p0000000-0000-4000-8000-000000000005', 'catalog:manage', 'إدارة الكتالوج', 'catalog', 'manage'),
    ('p0000000-0000-4000-8000-000000000006', 'vendors:read', 'قراءة الفنيين', 'vendors', 'read'),
    ('p0000000-0000-4000-8000-000000000007', 'vendors:manage', 'إدارة الفنيين', 'vendors', 'manage'),
    ('p0000000-0000-4000-8000-000000000008', 'vendors:self', 'بوابة الفني', 'vendors', 'self'),
    ('p0000000-0000-4000-8000-000000000009', 'support:read', 'قراءة الدعم', 'support', 'read'),
    ('p0000000-0000-4000-8000-000000000010', 'support:manage', 'إدارة الدعم', 'support', 'manage'),
    ('p0000000-0000-4000-8000-000000000011', 'support:self', 'تذاكر العميل', 'support', 'self'),
    ('p0000000-0000-4000-8000-000000000012', 'security:audit', 'سجل الأمان', 'security', 'audit'),
    ('p0000000-0000-4000-8000-000000000013', 'towing:manage', 'إدارة السطحات', 'towing', 'manage'),
    ('p0000000-0000-4000-8000-000000000014', 'logistics:manage', 'إدارة التوصيل', 'logistics', 'manage'),
    ('p0000000-0000-4000-8000-000000000015', 'payments:manage', 'إدارة المدفوعات', 'payments', 'manage'),
    ('p0000000-0000-4000-8000-000000000016', 'users:manage', 'إدارة المستخدمين', 'users', 'manage'),
    ('p0000000-0000-4000-8000-000000000017', 'landing:read', 'صفحة الهبوط', 'landing', 'read');

-- customer
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000001', id FROM permissions
WHERE slug IN ('bookings:read', 'bookings:create', 'support:self', 'catalog:read', 'landing:read');

-- admin — all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000002', id FROM permissions;

-- technician
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000003', id FROM permissions
WHERE slug IN ('vendors:self', 'bookings:read', 'catalog:read');

-- support
INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000004', id FROM permissions
WHERE slug IN ('support:read', 'support:manage', 'security:audit', 'bookings:read');

-- سعود العتيبي: عميل + مدير
INSERT INTO user_roles (user_id, role_id, granted_by) VALUES
    ('a0000000-0000-4000-8000-000000000001', 'r0000000-0000-4000-8000-000000000001', 'seed'),
    ('a0000000-0000-4000-8000-000000000001', 'r0000000-0000-4000-8000-000000000002', 'seed');

-- مستخدم فني تجريبي (نفس جوال أحمد الفني)
INSERT INTO users (id, full_name, email, phone, avatar_initials, loyalty_points)
VALUES (
    'a0000000-0000-4000-8000-000000000002',
    'أحمد الفني',
    'ahmad.vendor@example.com',
    '+966509876543',
    'أ',
    50
) ON CONFLICT (phone) DO NOTHING;

INSERT INTO user_roles (user_id, role_id, granted_by)
SELECT 'a0000000-0000-4000-8000-000000000002', 'r0000000-0000-4000-8000-000000000003', 'seed'
WHERE EXISTS (SELECT 1 FROM users WHERE id = 'a0000000-0000-4000-8000-000000000002');

INSERT INTO user_vendor_links (user_id, vendor_id)
SELECT 'a0000000-0000-4000-8000-000000000002', 'v0000000-0000-4000-8000-000000000001'
WHERE EXISTS (SELECT 1 FROM users WHERE id = 'a0000000-0000-4000-8000-000000000002');
