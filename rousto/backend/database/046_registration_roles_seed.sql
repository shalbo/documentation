-- Roles: customer, vendor, driver, workshop (+ existing admin/support/technician)

INSERT INTO roles (id, slug, name_ar, description_ar) VALUES
    ('r0000000-0000-4000-8000-000000000005', 'vendor', 'تاجر', 'بيع قطع الغيار'),
    ('r0000000-0000-4000-8000-000000000006', 'driver', 'سائق', 'توصيل قطع أو ساحبة أعطال'),
    ('r0000000-0000-4000-8000-000000000007', 'workshop', 'ورشة', 'مركز صيانة وخدمات')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO permissions (id, slug, name_ar, resource, action) VALUES
    ('p0000000-0000-4000-8000-000000000018', 'registration:self', 'تسجيل ذاتي', 'registration', 'self'),
    ('p0000000-0000-4000-8000-000000000019', 'registration:manage', 'اعتماد التسجيلات', 'registration', 'manage')
ON CONFLICT (slug) DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000005', id FROM permissions
WHERE slug IN ('vendors:self', 'catalog:read', 'registration:self')
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000006', id FROM permissions
WHERE slug IN ('vendors:self', 'logistics:manage', 'registration:self')
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000007', id FROM permissions
WHERE slug IN ('vendors:self', 'bookings:read', 'registration:self')
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, permission_id)
SELECT 'r0000000-0000-4000-8000-000000000002', id FROM permissions
WHERE slug = 'registration:manage'
ON CONFLICT DO NOTHING;
