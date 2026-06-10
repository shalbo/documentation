# 30 — فك شفرة VIN للسوق الليبي

قاعدة مرجعية `vin_decoders` لتحديد الصانع والموديل والمحرك من بادئة رقم الهيكل (WMI+VDS) — مخصّصة للسيارات الأكثر انتشاراً في طرابلس ومصراتة.

---

## الجدول

| الحقل | الوصف |
|-------|--------|
| `vin_prefix` | 8–11 رمزاً (أطول تطابق يفوز) |
| `make` / `model` | الصانع والموديل |
| `year_range` | نطاق السنوات |
| `engine` | مواصفات المحرك |
| `market` | `libya` |

---

## البيانات المزروعة (18 سجل)

- **Toyota:** Corolla, Camry, Prius, Avalon, Rav4
- **Hyundai:** Elantra, Avante, Tucson, Accent, Santa Fe, Azera
- **Kia:** Cerato, Sportage, Optima/K5, Rio
- **Chevrolet / Renault Samsung:** Cruze/Lacetti, SM3/SM5
- **أوروبي:** Mercedes C-Class, BMW 3 Series, VW Passat, Peugeot, Renault
- **أمريكي:** Malibu, Ford Fusion

---

## API

`GET /api/v1/vin/decode?vin=JTMCE90E123456789`

`GET /api/v1/parts/search?vin=...` — يُرجع `meta.decoded_vehicle` مع نتائج القطع المتوافقة.

`GET /api/v1/admin/vin-decoders` — قائمة المرجع (يتطلب `X-Admin-Key`).

---

## إعادة التشغيل (مكافئ Laravel Seeder)

```bash
cd rousto/backend/api
python3 ../scripts/seed_vin_decoders_libya.py
```

أو عبر Docker عند إنشاء قاعدة بيانات جديدة: `044_vin_decoders_*.sql` مُضمّنة في `docker-compose.yml`.

---

## Flutter

`PartsScreen` — تبويب **VIN** يعرض بطاقة المركبة المفكوكة (`decoded_vehicle`) فوق نتائج القطع.
