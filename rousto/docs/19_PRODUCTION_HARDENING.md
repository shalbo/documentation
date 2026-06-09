# 19 — صقل الإنتاج والأمان | Production Hardening

مراجعة أمنية وأداء لمنصة روستو قبل الإطلاق.

> **ملاحظة:** المشروع مبني على **FastAPI + PostgreSQL + Flutter + HTML/CSS/JS** — وليس Laravel أو Next.js. المكافئات مُطبّقة أدناه.

---

## 1. الأمان والمصادقة

| إجراء | التطبيق |
|-------|---------|
| حماية Mass Assignment | Pydantic schemas تُحدد الحقول المسموحة؛ لا تحديث مباشر من `request.json` |
| فحص الملكية | حجوزات، تذاكر دعم (`booking_id`)، موقع الفني (`booking_id`) |
| Rate Limiting | 5 طلبات/دقيقة على OTP وrefresh والنشرة (`app/rate_limit.py`) |
| تعطيل رؤوس التطوير | `ALLOW_LEGACY_HEADERS=false` يُعطّل `X-User-Id` و`X-Vendor-Id` |
| JWT إلزامي | ربط الفني بـ `UserVendorLink` عند استخدام Bearer |
| رفع الملفات | حد `MAX_UPLOAD_BYTES` (5MB) على صور الفحص |

### متغيرات الإنتاج

```bash
ENVIRONMENT=production
ALLOW_LEGACY_HEADERS=false
OTP_DEV_MODE=false
DISABLE_OPENAPI=true
JWT_SECRET=<secret>
ADMIN_API_KEY=<secret>
CORS_ORIGINS=https://rousto.com
```

---

## 2. تتبع الأخطاء والإشعارات

| المكوّن | الملف |
|---------|-------|
| Sentry (اختياري) | `app/error_reporting.py` — عيّن `SENTRY_DSN` |
| FCM (اختياري) | `app/notifications.py` — عيّن `FCM_ENABLED` |
| Flutter errors | `lib/services/error_reporter.dart` |
| Flutter FCM stub | `lib/services/push_notifications.dart` |

---

## 3. الأداء والتخزين المؤقت

| البيانات | TTL | الملف |
|----------|-----|-------|
| شجرة التصنيفات | 300ث | `routers/catalog.py` + `app/cache.py` |
| صفحة الهبوط | 120ث | `routers/landing.py` |
| Eager loading | موجود | `joinedload` في catalog وscans |

### Flutter
- إيقاف polling التتبّع عند مغادرة التبويب (`TrackingScreen.active`)
- دعم JWT عبر `--dart-define=ACCESS_TOKEN=...`

---

## 4. القانوني وSEO

| الصفحة | الملف |
|--------|-------|
| سياسة الخصوصية | `web/privacy.html` |
| الشروط والأحكام | `web/terms.html` |
| الضمان والاسترجاع | `web/warranty.html` |
| Sitemap | `web/sitemap.xml` |
| Robots | `web/robots.txt` |

---

## التحقق

```bash
cd rousto/backend/api
pip install -r requirements.txt
pytest tests/ -k unit -q
```
