# 29 — الربط الذكي VIN ↔ OEM

جدول وسيط `part_vin_compatibilities` يربط القطع ببادئات VIN (11 رمزاً).

---

## الجدول

| الحقل | الوصف |
|-------|--------|
| `part_id` | FK → `parts` |
| `vin_prefix` | 11 حرفاً (WMI+VDS) |
| فهرس | `idx_part_vin_compat_vin_prefix` |

---

## Scope البحث

`apply_where_compatible_with_vin` — يقص أول 11 رمزاً ويعرض **فقط** القطع المرتبطة في الجدول الوسيط.

`GET /api/v1/parts/search?vin=KMHCT41M0GU...`

---

## التاجر

`vendor-products.html` — حقل متعدد الأسطر لبادئات VIN → `vin_prefixes[]`

---

## Flutter

`PartsScreen` — تبويب **VIN** مع إدخال 17 رمزاً وتحويل تلقائي لأحرف كبيرة.
