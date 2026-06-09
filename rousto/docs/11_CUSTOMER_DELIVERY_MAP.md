# 11 — خريطة توصيل العميل | Customer Delivery Map

خريطة تفاعلية للعميل لمتابعة **وصول الفني** — مسار GPS، نسبة التقدّم، ETA، واستطلاع مباشر.

- **اللوجستيات:** [07_LOGISTICS_AND_LAST_MILE.md](07_LOGISTICS_AND_LAST_MILE.md)
- **خريطة الفني:** [10_VENDOR_MAP_LOCATION.md](10_VENDOR_MAP_LOCATION.md)
- **المخطط:** `technician_location_updates` + `bookings` + `addresses`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| خريطة توصيل غنية (فني + عميل + مسار) | Google Maps SDK |
| نسبة تقدّم التوصيل | WebSocket |
| استطلاع كل 20 ثانية | إشعارات push |
| صفحة ويب للعميل | تطبيق سائق منفصل |
| تحسين شاشة Flutter للتتبّع | Geofencing |

---

## مراحل التوصيل

| `delivery_phase` | الحالة | الوصف |
|------------------|--------|-------|
| `waiting` | pending / confirmed | بانتظار الفني |
| `assigned` | technician_assigned | تم التعيين |
| `en_route` | en_route | في الطريق |
| `arrived` | in_progress | جاري الخدمة |
| `completed` | completed | اكتمل |

---

## API Endpoints

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/bookings/{id}/delivery-map` | خريطة توصيل كاملة | Customer |
| GET | `/api/v1/bookings/active/delivery-map` | خريطة الحجز النشط | Customer |

**مصادقة:** `X-User-Id: a0000000-0000-4000-8000-000000000001`

---

## استجابة — `GET /bookings/{id}/delivery-map`

```json
{
  "data": {
    "booking": {
      "id": "i0000000-0000-4000-8000-000000000001",
      "reference": "RST-2026-001",
      "status": "en_route",
      "status_label_ar": "جارية"
    },
    "delivery_phase": "en_route",
    "delivery_phase_label_ar": "الفني في الطريق إليك",
    "is_live": true,
    "refresh_interval_seconds": 20,
    "technician": {
      "full_name": "أحمد الفني",
      "rating": 4.9,
      "location": { "lat": 24.772, "lng": 46.7365 },
      "eta_minutes": 2
    },
    "customer_location": {
      "label": "المنزل · حي النخيل",
      "lat": 24.774265,
      "lng": 46.738586
    },
    "distance_km": 0.42,
    "eta_minutes": 2,
    "initial_distance_km": 0.65,
    "progress_percent": 35.4,
    "trail": [
      { "lat": 24.77, "lng": 46.735, "recorded_at": "..." }
    ],
    "map_bounds": {
      "min_lat": 24.77,
      "max_lat": 24.774265,
      "min_lng": 46.735,
      "max_lng": 46.738586
    },
    "steps": []
  }
}
```

---

## حساب التقدّم

```
المسافة الابتدائية = haversine(أول نقطة في المسار, موقع العميل)
المسافة الحالية   = haversine(موقع الفني, موقع العميل)
التقدّم %          = (1 - الحالية / الابتدائية) × 100
```

---

## الواجهات

| الملف | الغرض |
|-------|-------|
| `web/delivery-map.html` | صفحة ويب للعميل — خريطة + استطلاع |
| `tracking_screen.dart` | شاشة Flutter — مسار + شريط تقدّم |

---

## الملفات التنفيذية

```
rousto/backend/database/016_customer_delivery_seed.sql
rousto/backend/api/app/customer_delivery_services.py
rousto/web/delivery-map.html
rousto/web/js/delivery-map.js
```

---

## الخطوة التالية

- [`12_TOWING_DISPATCH_MAP`](12_TOWING_DISPATCH_MAP.md) — خريطة إرسال السطحات ✅
- `13_AUTH` — OTP + JWT + أدوار
