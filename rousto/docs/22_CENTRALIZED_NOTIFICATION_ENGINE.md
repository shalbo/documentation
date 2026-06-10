# 22 — محرك الإشعارات المركزي ولوحة الإدارة

نظام **NOTIV Engine** — طبقة مركزية فوق صندوق الإشعارات (20) لتسجيل كل إرسال وإدارته من لوحة واحدة.

- **يعتمد على:** [`20_NOTIV`](20_NOTIV.md)
- **لوحة الإدارة:** `admin/notifications.html`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| سجل إرسال مركزي (dispatch log) | SMS / Email |
| بث جماعي حسب الشريحة | Marketing automation |
| إدارة قوالب الإشعارات | WebSocket live |
| إحصائيات المحرك | |

---

## الجداول

### `notification_dispatch_log`

سجل كل محاولة إرسال (مصدر الحدث، المستخدم، القناة، الحالة).

### `notification_broadcasts`

بثوث جماعية (شريحة، عدد المستلمين، Push).

---

## مصادر الأحداث (event_source)

| المصدر | الوصف |
|--------|-------|
| `booking_hook` | تغيير حالة الحجز |
| `support_hook` | رد الدعم |
| `towing_hook` | تحديث السحب |
| `admin_send` | إرسال فردي من الإدارة |
| `admin_broadcast` | بث جماعي |
| `vendor_hook` | إشعار التاجر |
| `driver_hook` | تنبيه السائق |

---

## شرائح البث (target_segment)

- `all_users` — كل المستخدمين النشطين
- `customers` — دور customer
- `technicians` — دور technician
- `admins` — دور admin

---

## API (إدارة)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/notifications` | صندوق كل المستخدمين |
| GET | `/api/v1/admin/notifications/analytics` | إحصائيات المحرك |
| GET | `/api/v1/admin/notifications/dispatch-log` | سجل الإرسال |
| GET | `/api/v1/admin/notifications/templates` | القوالب |
| POST | `/api/v1/admin/notifications/templates` | إنشاء قالب |
| PATCH | `/api/v1/admin/notifications/templates/{id}` | تحديث قالب |
| GET | `/api/v1/admin/notifications/users/search?q=` | بحث مستخدم |
| POST | `/api/v1/admin/notifications/send` | إرسال فردي |
| POST | `/api/v1/admin/notifications/broadcast` | بث جماعي |
| GET | `/api/v1/admin/notifications/broadcasts` | سجل البثوث |

---

## الملفات

| المكوّن | الملف |
|---------|-------|
| Schema | `database/032_notification_engine_schema.sql` |
| Seed | `database/033_notification_engine_seed.sql` |
| Engine | `app/notification_engine_services.py` |
| Admin API | `app/routers/admin_notifications.py` |
| Dashboard | `admin/notifications.html`, `admin/js/notifications-admin.js` |
| Tests | `tests/test_notification_engine.py` |

---

## التشغيل

```bash
cd rousto/backend && docker compose up -d
# لوحة الإشعارات:
# http://localhost:8080/admin/notifications.html
```
