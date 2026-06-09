# 17 — الصلاحيات والمصادقة | Permissions & Auth

نظام **OTP + JWT** مع **أدوار وصلاحيات (RBAC)** لمنصة روستو.

- **المجلط:** `roles`, `permissions`, `user_roles`, `auth_otp_requests`, `auth_refresh_tokens`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| OTP عبر الجوال (وضع تطوير يُرجع الرمز) | SMS حقيقي (Twilio/Unifonic) |
| JWT access + refresh tokens | OAuth2 / social login |
| أدوار: customer, admin, technician, support | ABAC متقدم |
| صلاحيات `resource:action` | 2FA hardware |
| توافق خلفي مع `X-User-Id` / `X-Admin-Key` | Keycloak |

---

## الأدوار

| الدور | الوصف |
|-------|-------|
| `customer` | عميل — حجوزات، ملف شخصي، دعم |
| `admin` | إدارة كاملة |
| `technician` | بوابة الفني (مرتبط بـ vendor) |
| `support` | دعم العملاء (تذاكر) |

---

## الصلاحيات (أمثلة)

| الصلاحية | الوصف |
|----------|-------|
| `bookings:read` | قراءة الحجوزات |
| `bookings:create` | إنشاء حجز |
| `catalog:manage` | إدارة الكتالوج |
| `vendors:manage` | إدارة الفنيين |
| `vendors:self` | بوابة الفني |
| `support:manage` | إدارة التذاكر |
| `security:audit` | سجل الأمان |
| `towing:manage` | إرسال السطحات |

---

## API Endpoints

### عام

| Method | Path | الوصف |
|--------|------|-------|
| POST | `/api/v1/auth/otp/send` | إرسال رمز OTP |
| POST | `/api/v1/auth/otp/verify` | التحقق وإصدار JWT |
| POST | `/api/v1/auth/refresh` | تجديد access token |
| POST | `/api/v1/auth/logout` | إلغاء refresh token |

### مصادق

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/auth/me` | المستخدم + الأدوار + الصلاحيات |
| GET | `/api/v1/auth/permissions` | قائمة الصلاحيات (admin) |

### إدارة (admin)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/auth/users/{id}/roles` | أدوار مستخدم |
| PUT | `/api/v1/admin/auth/users/{id}/roles` | تعيين أدوار |

---

## المصادقة

### JWT (مفضّل)

```
Authorization: Bearer <access_token>
```

### توافق تطوير (legacy)

```
X-User-Id: a0000000-0000-4000-8000-000000000001
X-Admin-Key: rousto_admin_dev
X-Vendor-Id: v0000000-0000-4000-8000-000000000001
```

---

## OTP (تطوير)

```bash
curl -X POST http://localhost:8000/api/v1/auth/otp/send \
  -H "Content-Type: application/json" \
  -d '{"phone": "+966501234567"}'

# الاستجابة تتضمن dev_otp في وضع التطوير

curl -X POST http://localhost:8000/api/v1/auth/otp/verify \
  -H "Content-Type: application/json" \
  -d '{"phone": "+966501234567", "code": "123456"}'
```

---

## الواجهة

| الملف | الوصف |
|-------|-------|
| `web/login.html` | تسجيل دخول OTP |
| `web/js/login.js` | حفظ JWT في localStorage |
| `web/js/api.js` | إرسال `Authorization` تلقائياً |

---

## المتغيرات

| المتغير | الافتراضي |
|---------|-----------|
| `JWT_SECRET` | `rousto_dev_jwt_secret_change_me` |
| `JWT_ACCESS_MINUTES` | `60` |
| `JWT_REFRESH_DAYS` | `7` |
| `OTP_DEV_MODE` | `true` |
