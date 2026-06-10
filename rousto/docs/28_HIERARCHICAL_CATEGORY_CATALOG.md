# 28 — الكتالوج الشجري وتصنيف التاجر

نظام تصنيف احترافي لقطع الغيار بعلاقة شجرية (parent_id).

---

## قاعدة البيانات

| الحقل | الوصف |
|-------|--------|
| `part_categories.parent_id` | NULL = قسم رئيسي، UUID = قسم فرعي |
| `part_categories.icon_key` | أيقونة للكتالوج (Flutter) |
| `parts.category_id` | FK للقسم الفرعي (الورقة) |

---

## APIs

| Method | Path | الوصف |
|--------|------|--------|
| GET | `/api/v1/parts/categories/tree` | الشجرة كاملة |
| GET | `/api/v1/parts/categories/roots` | الأقسام الرئيسية |
| GET | `/api/v1/parts/categories/{parent_id}/children` | الفروع |
| GET | `/api/v1/parts/search?category_id=` | فلترة + fitment |
| GET | `/api/v1/vendor/parts/categories/roots` | للتاجر |
| POST | `/api/v1/vendor/parts` | إضافة منتج (قسم فرعي إلزامي) |

---

## لوحة التاجر

`admin/vendor-products.html` — Cascading Dropdowns:
1. القسم الرئيسي
2. القسم الفرعي (إلزامي قبل الحفظ)

---

## Flutter

`catalog_screen.dart` — أقسام رئيسية بأيقونات → فرعية → `PartsScreen` مفلتر بالقسم + سيارة الجراج.

---

## Migrations

`042_hierarchical_categories.sql` + `042_hierarchical_categories_seed.sql`
