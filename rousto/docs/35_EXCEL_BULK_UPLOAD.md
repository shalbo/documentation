# 35 — الرفع الجماعي لقطع الغيار (Excel Bulk Upload)

مكافئ Laravel `SparePartsImport` + `maatwebsite/excel` — مُنفَّذ في FastAPI مع دعم `.csv` و `.xlsx`.

---

## أعمدة الملف

| العمود | مطلوب | الوصف |
|--------|-------|--------|
| `oem_number` | نعم | رقم القطعة / OEM |
| `name_ar` | نعم | الاسم بالعربية |
| `name_en` | لا | الاسم بالإنجليزية |
| `part_brand` | لا | العلامة — يُربط بـ `part_suppliers` |
| `price` | نعم | السعر |
| `quantity` | نعم | الكمية في مخزون التاجر |
| `sub_category` | لا | slug أو اسم القسم الفرعي |
| `compatible_vehicles` | لا | مركبات متوافقة (فاصلة) |
| `vin_prefixes` | لا | بادئات VIN (فاصلة) → `part_vin_compatibilities` |
| `description` | لا | وصف عربي |
| `image_url` | لا | رابط صورة خارجي — يُحمَّل ويُخزَّن في `spare_part_images` |

---

## API (التاجر — `X-Vendor-Id` أو JWT)

| الطريقة | المسار |
|---------|--------|
| GET | `/api/v1/vendor/parts/bulk-upload/template` |
| POST | `/api/v1/vendor/parts/bulk-upload` — `multipart/form-data` حقل `file` |
| POST | `/api/v1/vendor/parts/bulk-images-zip` — أرشيف ZIP (اسم الملف = OEM) |
| GET | `/api/v1/parts/media/{path}` — عرض الصورة المحفوظة |

- يُربط كل صف بـ `vendor_id` من التوكن تلقائياً
- التحقق من كل الصفوف أولاً — عند أي خطأ لا يُحفظ شيء (معاملة واحدة)
- `sub_category` غير المعروف → قسم **غير مصنف** (`uncategorized`)

---

## لوحة التاجر

`rousto/admin/vendor-products.html` — خطوتان متجاورتان:
1. رفع Excel (مع `image_url` اختياري)
2. رفع ZIP للصور (تسمية الملفات برقم OEM) + شريط تقدم

الصور تُعاد ضغطها إلى WebP (حد أقصى 1200px) قبل الحفظ في `storage/parts/`.

---

## الملفات

- `app/spare_parts_bulk_services.py` — محرك الاستيراد
- `database/048_uncategorized_category.sql` — قسم عام/غير مصنف
- `database/049_spare_part_images_schema.sql` — جدول `spare_part_images`
- `app/part_image_services.py` — تحميل URL، ZIP، resize
