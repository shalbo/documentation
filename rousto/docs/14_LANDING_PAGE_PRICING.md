# 14 — صفحة الهبوط والأسعار | Landing Page & Pricing

تجميع **ديناميكي** لأسعار الخدمات وخطط الاشتراك والباقات لصفحة الهبوط وصفحة الأسعار.

- **المصادقة (لاحقاً):** `15_AUTH`
- **المخطط:** `landing_hero_stats`, `landing_pricing_plans`, `landing_page_features`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| بطاقات تسويقية (فردي، عائلي، أعمال) | CMS كامل لكل أقسام الموقع |
| جلب أسعار الخدمات من الكتالوج | تعديل أسعار الكتالوج من الواجهة |
| دمج خطط الاشتراك والباقات | بوابة دفع للاشتراك |
| إحصائيات البطل (Hero) | A/B testing |
| صفحة `pricing.html` + قسم `#pricing` | تعدد اللغات |

---

## الجداول

### `landing_hero_stats`

| الحقل | الوصف |
|-------|-------|
| `slug` | معرّف ثابت (`happy_customers`, `rating`, …) |
| `value_ar` | القيمة المعروضة (`+25K`, `4.9★`) |
| `label_ar` | التسمية (`عميل سعيد`) |

### `landing_pricing_plans`

بطاقات تسويقية مستقلة عن `membership_plans` — للعرض على الموقع.

| الحقل | الوصف |
|-------|-------|
| `features` | JSONB — مصفوفة ميزات بالعربية |
| `is_featured` | تمييز البطاقة (شارة «الأكثر شعبية») |
| `price_label_ar` | مثل «شهرياً» أو «ادفع لكل خدمة» |

---

## API Endpoints

### عام (بدون مصادقة)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/landing/pricing` | خدمات + خطط تسويقية + اشتراكات + باقات |
| GET | `/api/v1/landing/page` | بيانات صفحة الهبوط الكاملة (hero + pricing + features) |

---

## أمثلة

### `GET /api/v1/landing/pricing`

```json
{
  "data": {
    "services": [
      {
        "slug": "oil-change",
        "name_ar": "تغيير الزيت والفلاتر",
        "price_sar": 120,
        "icon_emoji": "🛢️"
      }
    ],
    "marketing_plans": [
      {
        "slug": "family",
        "name_ar": "عائلي",
        "price_sar": 29,
        "price_label_ar": "شهرياً",
        "is_featured": true,
        "features": ["خصم 10٪ على كل خدمة", "أولوية الحجز"]
      }
    ],
    "membership_plans": [],
    "packages": []
  },
  "meta": { "currency": "دينار" }
}
```

### `GET /api/v1/landing/page`

```json
{
  "data": {
    "hero": {
      "stats": [
        { "slug": "happy_customers", "value_ar": "+25K", "label_ar": "عميل سعيد" }
      ]
    },
    "pricing": { "services": [], "marketing_plans": [] },
    "features": [
      { "slug": "transparent-pricing", "title_ar": "أسعار ثابتة وواضحة" }
    ]
  }
}
```

---

## الواجهة

| الملف | الوصف |
|-------|-------|
| `web/pricing.html` | صفحة أسعار مخصصة |
| `web/js/landing-pricing.js` | جلب API وعرض البطاقات |
| `web/index.html` | قسم `#pricing` + خدمات ديناميكية |

---

## الخطوة التالية

- `15_AUTH` — OTP + JWT + أدوار
