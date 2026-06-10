# 27 — موديولات الإنتاج (AutoParts.com Standards)

ثلاثة أنظمة أساسية لإكمال منصة سوق قطع الغيار للإنتاج.

---

## 1. Guaranteed Fitment Selector

| الجدول | الغرض |
|--------|-------|
| `car_makes` | ماركات المركبات |
| `car_models` | موديلات مرتبطة بالماركة |
| `car_years` | سنوات لكل موديل |
| `part_vehicle_compatibilities` | Many-to-Many بين `parts` و `car_years` |

| API | الوصف |
|-----|--------|
| `GET /api/v1/fitment/makes` | قائمة الماركات |
| `GET /api/v1/fitment/models?make_id=` | موديلات الماركة |
| `GET /api/v1/fitment/years?model_id=` | سنوات الموديل |
| `GET /api/v1/fitment/resolve` | حل car_year_id |
| `GET /api/v1/marketplace/home?car_year_id=` | سوق مفلتر بتوافق Exact Fit |
| `GET /api/v1/parts/search?car_year_id=` | بحث مفلتر |

**Flutter:** `VehicleSelector` + `FitmentStorage` (SharedPreferences)

---

## 2. OEM / VIN Advanced Search

| الحقل | الفهرس |
|-------|--------|
| `parts.oem_number` | `idx_parts_oem_number` |
| `parts.vin_prefix` | `idx_parts_vin_prefix` |

| API | الوصف |
|-----|--------|
| `GET /api/v1/parts/search?oem=` | مطابقة OEM دقيقة |
| `GET /api/v1/parts/search?vin=` | بادئة VIN (11 حرف) |
| `GET /api/v1/parts/search?in_stock_only=true` | محلات بمخزون فعلي |

---

## 3. Hybrid Shipping Engine

| النوع | السلوك |
|-------|--------|
| `local_delivery` | نفس المدينة — مندوب GPS أقرب فني |
| `intercity_shipping` | تعرفة ثابتة من `intercity_shipping_rates` |

| الجدول | الغرض |
|--------|-------|
| `part_orders` | طلبات قطع منفصلة عن `bookings` |
| `part_order_settlements` | توزيع عوائد (لا يمس `payment_split_legs`) |
| `intercity_shipping_rates` | تعرفات الأدمن بين المدن |

| API | الوصف |
|-----|--------|
| `POST /api/v1/shipping/quote` | عرض تكلفة الشحن |
| `POST /api/v1/shipping/part-orders` | إنشاء طلب مع تسوية مالية |
| `GET /admin/shipping/intercity-rates` | إدارة التعرفات |

---

## الملفات

- Schema: `039_*`, `040_*`, `041_*`
- Services: `fitment_services.py`, `shipping_services.py`
- Admin: `admin/fitment.html`, `admin/shipping.html`
- Flutter: `fitment_storage.dart`, `vehicle_selector.dart`
