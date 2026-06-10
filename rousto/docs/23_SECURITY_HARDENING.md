# 23 — تصلّب الأمان | Security Hardening

طبقة أمان إضافية فوق [19_PRODUCTION_HARDENING](19_PRODUCTION_HARDENING.md) و[21_I18N_AND_LAUNCH](21_I18N_AND_LAUNCH.md) (الموديل 4).

- **لوحة الإدارة:** `admin/security.html`
- **الاختبارات:** `tests/test_security_hardening.py`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| رؤوس HTTP أمنية | WAF خارجي |
| Trusted Hosts | Pen-test خارجي |
| Request ID للتتبع | mTLS بين الخدمات |
| تدقيق محاولات الدخول الفاشلة | |
| Rate limit على API الإدارة | |
| حالة الأمان للإدارة | |

---

## 1. رؤوس HTTP (`security_middleware.py`)

| الرأس | القيمة |
|-------|--------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | تقييد الكاميرا/الموقع/الميكروفون |
| `Strict-Transport-Security` | في الإنتاج فقط |
| `X-Request-Id` | UUID لكل طلب |

---

## 2. Trusted Hosts

```bash
TRUSTED_HOSTS=rousto.com,api.rousto.com
```

يُفعّل `TrustedHostMiddleware` عند تعيين المتغير.

---

## 3. تدقيق الأمان (`security_audit.py`)

| الحدث | الخطورة |
|-------|---------|
| `auth.invalid_token` | warn |
| `auth.legacy_disabled` | warn |
| `auth.otp_verify_failed` | warn |
| `auth.admin_key_failed` | critical |
| `auth.rate_limited` | warn |

---

## 4. Rate limit — API الإدارة

- 30 طلب/دقيقة لكل IP على مسارات `/admin/*` (قابل للتعديل عبر `ADMIN_RATE_LIMIT_PER_MINUTE`)

---

## 5. API

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/security/events` | سجل الأحداث (موجود) |
| GET | `/api/v1/admin/security/status` | حالة التصلّب والإعدادات |

---

## متغيرات الإنتاج

```bash
ENVIRONMENT=production
ALLOW_LEGACY_HEADERS=false
OTP_DEV_MODE=false
DISABLE_OPENAPI=true
TRUSTED_HOSTS=rousto.com,api.rousto.com
PRODUCTION_STRICT=true
ADMIN_RATE_LIMIT_PER_MINUTE=30
```

---

## الملفات

| المكوّن | الملف |
|---------|-------|
| Middleware | `app/security_middleware.py` |
| Audit helpers | `app/security_audit.py` |
| Status API | `app/routers/support.py` |
| security.txt | `web/.well-known/security.txt` |
| Tests | `tests/test_security_hardening.py` |
