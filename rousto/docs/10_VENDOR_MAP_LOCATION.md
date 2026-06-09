# 10 — خريطة وموقع الفني | Vendor Map & Location

تمكين **الفني المُوافَق** من إدارة موقعه على الخريطة، تتبّع المهمة النشطة، وتحديث GPS مباشرة — مع لوحة إدارية لعرض الفنيين.

- **اللوجستيات:** [07_LOGISTICS_AND_LAST_MILE.md](07_LOGISTICS_AND_LAST_MILE.md)
- **انضمام الفنيين:** [09_VENDOR_ONBOARDING_FINANCIALS.md](09_VENDOR_ONBOARDING_FINANCIALS.md)
- **المخطط:** أعمدة `base_lat/base_lng` على `vendors` + `technician_location_updates`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| موقع قاعدة الخدمة + نطاق التغطية | Google Maps SDK |
| تحديث GPS مباشر من بوابة الفني | WebSocket / push |
| مهمة نشطة + وجهة العميل على الخريطة | Geofencing تلقائي |
| سجل آخر 20 نقطة GPS | تطبيق جوال Flutter للفني |
| خريطة إدارية لكل الفنيين المُوافَقين | تحسين مسار متعدد المحطات |
| تبديل التوفر (`is_available`) | |

---

## نموذج الموقع

| المصدر | الحقل | الوصف |
|--------|-------|-------|
| `vendors` | `base_lat`, `base_lng` | موقع قاعدة الخدمة (الورشة/النقطة الثابتة) |
| `vendors` | `service_radius_km` | نطاق التغطية بالكيلومتر (افتراضي 15) |
| `technicians` | `current_lat`, `current_lng` | الموقع المباشر للفني |
| `technician_location_updates` | سجل | آخر نقاط GPS |

---

## API Endpoints

### بوابة الفني (`X-Vendor-Id`)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/vendor/me/map` | خريطة كاملة: قاعدة + مباشر + مهمة + مسار |
| PUT | `/api/v1/vendor/me/location/base` | تحديث موقع القاعدة ونطاق التغطية |
| PATCH | `/api/v1/vendor/me/location/live` | تحديث GPS المباشر |
| GET | `/api/v1/vendor/me/jobs/active` | المهمة النشطة مع الوجهة والـ ETA |
| PATCH | `/api/v1/vendor/me/availability` | تفعيل/إيقاف التوفر |

### إدارة

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/vendors/map` | كل الفنيين المُوافَقين على الخريطة |

---

## استجابة الخريطة — `GET /vendor/me/map`

```json
{
  "data": {
    "vendor_id": "v0000000-0000-4000-8000-000000000001",
    "business_name": "خدمات أحمد للسيارات",
    "is_available": true,
    "base_location": {
      "lat": 24.77,
      "lng": 46.735,
      "service_radius_km": 20.0
    },
    "live_location": {
      "lat": 24.7705,
      "lng": 46.7362,
      "recorded_at": "2026-06-09T10:30:00Z"
    },
    "active_job": {
      "booking_id": "i0000000-0000-4000-8000-000000000001",
      "reference": "RST-2026-001",
      "status": "en_route",
      "destination": {
        "label": "المنزل · حي النخيل",
        "lat": 24.774265,
        "lng": 46.738586
      },
      "distance_km": 0.42,
      "eta_minutes": 2
    },
    "trail": [
      { "lat": 24.77, "lng": 46.735, "recorded_at": "..." }
    ]
  }
}
```

---

## قواعد العمل

1. **الموافقة مطلوبة** — كل endpoints الموقع تتطلب `status = approved` و`technician_id`.
2. **GPS المباشر** — يُحدَّث `technicians.current_lat/lng` ويُسجَّل في `technician_location_updates`.
3. **المهمة النشطة** — أول حجز بحالة `technician_assigned` أو `en_route` أو `in_progress` للفني.
4. **المسار** — آخر 20 نقطة GPS (للمهمة النشطة إن وُجدت، وإلا عام).
5. **التوفر** — `is_available` على جدول `technicians` يتحكم في التعيين التلقائي.

---

## الواجهات

| الصفحة | الغرض |
|--------|-------|
| `admin/vendor-portal.html` | بوابة الفني — خريطة + تحديث موقع + مهمة نشطة |
| `admin/vendor-map.html` | لوحة إدارية — كل الفنيين على خريطة |

---

## الملفات التنفيذية

```
rousto/backend/database/
├── 013_vendor_location_schema.sql
└── 014_vendor_location_seed.sql

rousto/backend/api/app/
├── vendor_map_services.py
└── routers/vendor_map.py

rousto/admin/
├── vendor-portal.html
├── vendor-map.html
└── js/vendor-map.js
```

---

## الخطوة التالية

- `11_AUTH` — OTP + JWT + أدوار (`customer`, `technician`, `admin`)
