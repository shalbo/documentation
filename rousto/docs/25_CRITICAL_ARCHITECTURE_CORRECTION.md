# 25 — تصحيح معماري حرج | Critical Architecture Correction

إصلاح فجوات معمارية أساسية اكتُشفت بعد Modules 07–24.

---

## المشاكل التي يُصحّحها

| # | المشكلة | التصحيح |
|---|---------|---------|
| 1 | «قطع غيار أصلية» في التسويق بلا نظام خلفي | كتالوج `parts` منفصل عن `services` |
| 2 | `technicians` يُستخدم للفني والسائق بلا قيود | `assert_service_technician` / `assert_tow_driver` |
| 3 | لا سجل لمركبات السطحات | جدول `tow_vehicles` |
| 4 | بحث العميل يخص الخدمات فقط | `GET /parts/search` + واجهات |

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| كتالوج قطع غيار + موردين + فئات | تكامل ERP خارجي |
| مخزون لكل تاجر | دفع قطع منفصل |
| قطع مرتبطة بالحجز + ضمان | توصيل قطع مستقل |
| فرض `driver_type` على التعيين | تطبيق سائق منفصل |

---

## الجداول الجديدة

| الجدول | الغرض |
|--------|-------|
| `part_suppliers` | الموردون (OEM، بعد ماركت) |
| `part_categories` | فئات القطع |
| `parts` | الكتالوج (رقم قطعة، سعر، ضمان، توافق مركبة) |
| `part_inventory` | مخزون التاجر |
| `booking_parts` | قطع مُركّبة في حجز |
| `part_warranty_claims` | مطالبات ضمان القطع |
| `tow_vehicles` | مركبات السطحات |

---

## فصل المجالات

```
services (عمالة/خدمة)     ≠     parts (قطع غيار)
technician driver_type=service  ≠  driver_type=tow
bookings → service tech only    towing_dispatches → tow drivers only
```

---

## API — العميل

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/parts/categories` | فئات القطع |
| GET | `/api/v1/parts/search?q=` | بحث قطع (`make`, `model`, `category`) |
| GET | `/api/v1/parts/{id}` | تفاصيل قطعة |
| GET | `/api/v1/bookings/{id}/parts` | قطع الحجز |
| POST | `/api/v1/parts/warranty-claims` | مطالبة ضمان |

## API — الإدارة

| Method | Path | الوصف |
|--------|------|-------|
| GET/POST | `/api/v1/admin/parts` | CRUD كتالوج |
| PATCH | `/api/v1/admin/parts/{id}` | تحديث قطعة |
| GET | `/api/v1/admin/part-warranty-claims` | مطالبات الضمان |
| POST | `/api/v1/admin/bookings/{id}/parts` | إرفاق قطعة بحجز |

---

## الملفات

| المكوّن | الملف |
|---------|-------|
| Spec | `docs/25_CRITICAL_ARCHITECTURE_CORRECTION.md` |
| Schema | `database/036_spare_parts_schema.sql` |
| Seed | `database/037_spare_parts_seed.sql` |
| Domain guards | `app/technician_domain.py` |
| Parts logic | `app/parts_services.py` |
| Routers | `app/routers/parts.py`, `admin_parts.py` |
| Admin UI | `admin/parts.html` |
| Web | `web/parts.html` |
| Flutter | `screens/parts_screen.dart` |
| Tests | `tests/test_architecture_correction.py` |

---

## Marketplace-First (Module 26)

المنصة = **سوق قطع غيار مركزي**؛ الصيانة والسطحات خدمة مكمّلة.

| المكوّن | التغيير |
|---------|---------|
| API افتراضي | `GET /api/v1/marketplace/home` |
| بحث جغرافي | `GET /api/v1/parts/{id}/vendors-nearby?lat=&lng=` |
| إدارة | `admin/index.html` → إحصائيات السوق؛ `admin/logistics.html` للوجستيات |
| Flutter | `home_screen.dart` = سوق قطع؛ FAB = حجز ورشة/ساحبة |
| Geo indexes | `database/038_marketplace_geo.sql` |
