# 12 — خريطة إرسال السطحات | Towing Dispatch Map

إدارة **طلبات السحب والإرسال** — من موقع العطل إلى الورشة — مع خريطة مزدوجة المرحلة (التقاط ← التسليم).

- **توصيل العميل:** [11_CUSTOMER_DELIVERY_MAP.md](11_CUSTOMER_DELIVERY_MAP.md)
- **اللوجستيات:** [07_LOGISTICS_AND_LAST_MILE.md](07_LOGISTICS_AND_LAST_MILE.md)
- **المخطط:** `towing_dispatches`, `towing_dispatch_events`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| طلب سحب (التقاط + تسليم) | Google Maps Directions |
| تعيين سائق سطحة | تطبيق سائق منفصل |
| خريطة مرحلتين (عطل → ورشة) | WebSocket |
| لوحة إرسال إدارية | تسعير ديناميكي معقد |
| تتبّع GPS للسطحة | KYC للسائقين |

---

## مراحل الإرسال

| الحالة | `dispatch_phase` | الوصف |
|--------|------------------|-------|
| `pending` | `waiting` | بانتظار الإرسال |
| `dispatched` | `assigned` | تم تعيين السطحة |
| `en_route_pickup` | `to_pickup` | متجه لموقع العطل |
| `at_pickup` | `at_pickup` | عند السيارة |
| `en_route_dropoff` | `to_dropoff` | متجه للورشة |
| `completed` | `completed` | تم التسليم |
| `cancelled` | `cancelled` | ملغى |

---

## جداول قاعدة البيانات

| الجدول | الغرض |
|--------|-------|
| `towing_dispatches` | طلب السحب + موقعي التقاط/تسليم + السائق |
| `towing_dispatch_events` | سجل مراحل الإرسال |

---

## API Endpoints

### العميل (`X-User-Id`)

| Method | Path | الوصف |
|--------|------|-------|
| POST | `/api/v1/towing/dispatches` | إنشاء طلب سحب |
| GET | `/api/v1/towing/dispatches/{id}/map` | خريطة الإرسال |
| GET | `/api/v1/towing/dispatches/active/map` | خريطة الطلب النشط |

### إدارة (`X-Admin-Key`)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/towing/dispatches` | كل الطلبات |
| GET | `/api/v1/admin/towing/dispatches/map` | خريطة الإرسالات |
| POST | `/api/v1/admin/towing/dispatches/{id}/dispatch` | تعيين سائق |
| POST | `/api/v1/admin/towing/dispatches/{id}/advance` | التقدّم للمرحلة التالية |
| PATCH | `/api/v1/admin/towing/dispatches/{id}/location` | تحديث GPS السطحة |

---

## استجابة الخريطة

```json
{
  "data": {
    "dispatch": {
      "reference": "TOW-2026-001",
      "status": "en_route_pickup",
      "dispatch_phase": "to_pickup",
      "dispatch_phase_label_ar": "السطحة متجهة لموقع العطل"
    },
    "pickup": { "label": "موقع العطل · حي النخيل", "lat": 24.774, "lng": 46.738 },
    "dropoff": { "label": "ورشة روستو · العليا", "lat": 24.713, "lng": 46.675 },
    "active_leg": "to_pickup",
    "tow_truck": {
      "full_name": "سعد السطحة",
      "location": { "lat": 24.768, "lng": 46.732 },
      "eta_minutes": 8
    },
    "distance_km": 1.2,
    "total_route_km": 4.5,
    "progress_percent": 15.0,
    "trail": [],
    "map_bounds": {},
    "is_live": true,
    "refresh_interval_seconds": 20
  }
}
```

---

## الواجهات

| الصفحة | الغرض |
|--------|-------|
| `admin/towing-dispatch.html` | لوحة إرسال + خريطة |
| `web/towing-map.html` | تتبّع العميل لطلب السحب |

---

## الملفات التنفيذية

```
rousto/backend/database/017_towing_dispatch_schema.sql
rousto/backend/database/018_towing_dispatch_seed.sql
rousto/backend/api/app/towing_dispatch_services.py
rousto/backend/api/app/routers/towing_dispatch.py
```

---

## الخطوة التالية

- [`13_CUSTOMER_SUPPORT_AND_SECURITY`](13_CUSTOMER_SUPPORT_AND_SECURITY.md) — دعم العملاء والأمان ✅
- `16_AUTH` — OTP + JWT + أدوار
