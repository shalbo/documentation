# 20 — الإشعارات | NOTIV (Notifications & Push)

نظام **إشعارات داخل التطبيق + Push (FCM)** لمنصة روستو.

- **المصادقة:** [`17_PERMISSIONS_AND_AUTH`](17_PERMISSIONS_AND_AUTH.md)
- **القنوات:** in-app inbox + FCM push
- **المجلد:** `notification_*` + `user_device_tokens`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| صندوق إشعارات in-app | SMS / Email حقيقي |
| Push FCM (Android/iOS/Web) | WebSocket live |
| تفضيلات المستخدم لكل فئة | تعدد اللغات |
| قوالب إشعارات | Marketing automation كامل |
| إشعار حالة الحجز | |

---

## الفئات (categories)

| الفئة | الوصف |
|-------|-------|
| `booking` | تحديثات الحجز والتتبّع |
| `support` | ردود الدعم والتذاكر |
| `towing` | إرسال السطحات |
| `promo` | عروض وتسويق |
| `security` | تنبيهات الأمان |
| `system` | إعلانات النظام |

---

## الجداول

### `notification_templates`

قوالب جاهزة بصيغة `{{reference}}` و`{{label}}`.

### `user_notification_preferences`

تفعيل/تعطيل push وin-app لكل فئة.

### `notifications`

صندوق الإشعارات (inbox) لكل مستخدم.

### `user_device_tokens` (027)

رموز FCM للأجهزة.

---

## API Endpoints

### عميل (مصادق)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/me/notifications` | صندوق الإشعارات |
| GET | `/api/v1/me/notifications/unread-count` | عدد غير المقروء |
| PATCH | `/api/v1/me/notifications/{id}/read` | تعليم كمقروء |
| POST | `/api/v1/me/notifications/read-all` | تعليم الكل مقروء |
| GET | `/api/v1/me/notification-preferences` | التفضيلات |
| PUT | `/api/v1/me/notification-preferences` | تحديث التفضيلات |
| POST | `/api/v1/me/devices/register` | تسجيل FCM token |

### إدارة

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/notifications` | سجل الإشعارات |
| POST | `/api/v1/admin/notifications/send` | إرسال إشعار لمستخدم |

---

## التفعيل

```bash
FCM_ENABLED=true
FCM_CREDENTIALS_PATH=/secrets/firebase-service-account.json
```

```bash
flutter run --dart-define=ENABLE_FCM=true --dart-define=API_BASE_URL=http://localhost:8000
```

---

## الواجهة

| الملف | الوصف |
|-------|-------|
| `web/notifications.html` | صندوق الإشعارات |
| `web/js/notifications.js` | جلب وقراءة الإشعارات |
| `app_flutter/lib/screens/notifications_screen.dart` | شاشة الإشعارات |

---

## الملفات المنفّذة

| المكوّن | الملف |
|---------|-------|
| Schema | `backend/database/028_notiv_schema.sql` |
| Seed | `backend/database/029_notiv_seed.sql` |
| Inbox | `backend/api/app/notification_inbox_services.py` |
| FCM + hooks | `backend/api/app/notifications.py` |
| Router | `backend/api/app/routers/notifications.py` |
| Web | `web/notifications.html`, `web/js/notifications.js` |
| Flutter | `app_flutter/lib/screens/notifications_screen.dart` |
| Tests | `backend/api/tests/test_notiv.py` |

## الخطوة التالية

- WebSocket للإشعارات الفورية بدون polling
- تكامل SMS (Unifonic) للOTP والتنبيهات الحرجة
