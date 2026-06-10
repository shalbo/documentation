# 33 — تدفق التسجيل متعدد الأدوار

## الأدوار

`customer` · `vendor` · `driver` · `workshop` (+ `admin`)

## الجداول

| جدول | الحقول الرئيسية |
|------|-----------------|
| `vendor_profiles` | shop_name, specialty, lat/lng, is_approved |
| `driver_profiles` | service_type, plate, مستندات, is_approved=false |
| `workshop_profiles` | center_name, specialty, lat/lng |

## APIs

| Method | Path |
|--------|------|
| POST | `/api/v1/registration/customer` |
| POST | `/api/v1/registration/vendor` |
| POST | `/api/v1/registration/workshop` |
| POST | `/api/v1/registration/driver` |
| POST | `/api/v1/registration/driver/{id}/documents` |
| GET | `/api/v1/admin/registration/pending` |
| POST | `/api/v1/admin/registration/{role}/{id}/approve` |
| POST | `/api/v1/admin/registration/{role}/{id}/reject` |

## Flutter

- `RegisterRoleScreen` — اختيار زبون/سائق
- `CustomerRegisterScreen` — اسم، هاتف، مدينة
- `DriverRegisterScreen` — خطوتان + رفع مستندات

## Admin

- `registration-approvals.html` — اعتماد (كحلي) / رفض (أحمر)
- `register-portal.html` — تسجيل تاجر وورشة

## Migrations

`046_registration_profiles_schema.sql` + `046_registration_roles_seed.sql`
