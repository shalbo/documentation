# 37 — تمييز وفلترة القطع الجديدة والمستعملة

مكافئ Laravel `part_condition` على جدول `spare_parts` — مُنفَّذ في FastAPI + PostgreSQL + لوحة التاجر + Flutter.

---

## قاعدة البيانات

| الحقل | الجدول | النوع | الافتراضي |
|-------|--------|-------|-----------|
| `part_condition` | `parts` | `VARCHAR` CHECK (`new` \| `used`) | `new` |

- Migration: `rousto/backend/database/051_part_condition.sql`
- Index: `idx_parts_part_condition` لتسريع الفلترة

---

## API

### بحث القطع

```
GET /api/v1/parts/search?condition=used
GET /api/v1/parts/search?vin=4T1B11HK5JK123456&condition=used
GET /api/v1/parts/search?oem=TOY-04152&condition=new
```

| المعامل | القيم | الوصف |
|---------|-------|--------|
| `condition` | `new` \| `used` | فلترة حالة القطعة — يعمل مع VIN و OEM وباقي الفلاتر |

الاستجابة تتضمن `part_condition` و `condition` (alias).

### إضافة قطعة (التاجر)

```
POST /api/v1/vendor/parts
{ "part_condition": "used", ... }
```

---

## الرفع الجماعي (Excel/CSV)

عمود جديد: **`condition`**

| القيمة في الملف | التخزين |
|-----------------|---------|
| `new` أو فارغ | `new` |
| `used`, `used_part`, `مستعمل`, `مستعملة`, `ربش` | `used` |

القالب: `GET /api/v1/vendor/parts/bulk-upload/template` — يتضمن سطر توضيحي `# حالة القطعة...`

---

## لوحة التاجر

`rousto/admin/vendor-products.html` — اختيار **جديد** / **مستعمل / ربش** عند الإضافة اليدوية.

---

## تطبيق Flutter

| المكوّن | الملف |
|---------|-------|
| شارة الحالة على البطاقة | `widgets/part_condition_badge.dart` |
| شرائح الفلترة | `screens/parts_screen.dart` — «جديد فقط» / «مستعمل فقط» |
| تمرير الفلتر للـ API | `api_client.dart` → `condition` |

- **مستعمل:** شارة كحلية داكنة (`#003049`)
- **جديد:** شارة فاتحة بخلفية `navy050`
