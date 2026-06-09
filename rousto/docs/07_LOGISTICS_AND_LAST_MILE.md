# 07 — اللوجستيات وتوصيل الخدمة | Logistics & Last Mile

إدارة **الوصول الأخير** — تعيين الفني، التتبّع المباشر، ETA، وتحديث الموقع.

- **التتبّع الحالي:** [02_BACKEND_APIS.md](02_BACKEND_APIS.md)
- **المخطط:** [01_DATABASE_SCHEMA.md](01_DATABASE_SCHEMA.md) — `technicians`, `booking_status_events`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| حساب ETA تجريبي (مسافة + سرعة) | Google Maps / Directions API |
| تحديث موقع الفني | تطبيق جوال للفني |
| تقدّم حالة الحجز (dev/admin) | WebSocket / push notifications |
| وجهة العميل في استجابة التتبّع | تحسين أسطول متعدد المحطات |
| سجل مواقع الفني | Geofencing تلقائي |
| استطلاع دوري في Flutter | تطبيق سائق منفصل |

---

## تدفق الحالة

```mermaid
flowchart LR
    confirmed --> technician_assigned
    technician_assigned --> en_route
    en_route --> in_progress
    in_progress --> completed
```

| الحالة | الوصف |
|--------|-------|
| `confirmed` | تم تأكيد الحجز |
| `technician_assigned` | تم تعيين فني |
| `en_route` | الفني في الطريق |
| `in_progress` | جاري تنفيذ الخدمة |
| `completed` | اكتملت الخدمة |

---

## جداول قاعدة البيانات

| الجدول | الغرض |
|--------|-------|
| `technician_location_updates` | سجل تحديثات GPS للفني |

الجداول الموجودة: `technicians.current_lat/lng`, `booking_status_events.metadata` (ETA).

---

## API Endpoints

### التتبّع (محسّن)

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/bookings/{id}/tracking` | فني + وجهة + ETA + مسافة + خط زمني كامل | نعم |

حقول جديدة في الاستجابة:

```json
{
  "destination": {
    "label": "المنزل · حي النخيل",
    "lat": 24.774265,
    "lng": 46.738586
  },
  "distance_km": 0.42,
  "eta_minutes": 12
}
```

### عمليات اللوجستيات (dev/admin)

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| POST | `/api/v1/logistics/bookings/{id}/advance` | الانتقال للحالة التالية | Admin |
| PATCH | `/api/v1/logistics/technicians/{id}/location` | تحديث موقع الفني | Admin |
| POST | `/api/v1/logistics/bookings/{id}/simulate-move` | تحريك الفني نحو العميل (تجريبي) | Admin |

المصادقة: `X-Admin-Key: rousto_admin_dev`

---

## حساب ETA (v1)

```
مسافة = haversine(موقع الفني, عنوان الحجز)
ETA بالدقائق = (مسافة ÷ 30 كم/س) × 60
```

يُحدَّث تلقائياً عند `PATCH location` أو `simulate-move`.

---

## واجهة التطبيق

| التحسين | الملف |
|---------|-------|
| خريطة نسبية (فني + عميل) | `tracking_screen.dart` |
| استطلاع كل 20 ثانية أثناء `en_route` | `tracking_screen.dart` |
| عرض المسافة والـ ETA | `tracking_screen.dart` |
| نماذج الوجهة والموقع | `models.dart` |

---

## الملفات

```
rousto/docs/07_LOGISTICS_AND_LAST_MILE.md
rousto/backend/database/007_logistics_schema.sql
rousto/backend/api/app/logistics_services.py
rousto/backend/api/app/routers/logistics.py
rousto/backend/api/tests/test_logistics.py
rousto/app_flutter/lib/screens/tracking_screen.dart
```

---

## التشغيل

```bash
cd rousto/backend && docker compose down -v && docker compose up -d

# تقديم الحجز التجريبي
curl -X POST http://localhost:8000/api/v1/logistics/bookings/i0000000-0000-4000-8000-000000000001/advance \
  -H "X-Admin-Key: rousto_admin_dev"

# تحريك الفني
curl -X POST http://localhost:8000/api/v1/logistics/bookings/i0000000-0000-4000-8000-000000000001/simulate-move \
  -H "X-Admin-Key: rousto_admin_dev"
```

---

## الخطوة التالية

- [`08_SPLIT_PAYMENTS_ENGINE`](08_SPLIT_PAYMENTS_ENGINE.md) — إطلاق حصة الفني عند `completed` ✅
- `09_AUTH` — OTP + JWT + أدوار (`technician`, `admin`)
- `10_LOGISTICS_REALTIME` — WebSocket + خرائط حقيقية
