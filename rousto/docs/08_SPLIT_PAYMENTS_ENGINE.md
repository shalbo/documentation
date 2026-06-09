# 08 — محرك تقسيم المدفوعات | Split Payments Engine

تقسيم تلقائي لكل دفعة حجز بين **المنصة** و**الفني** و**الاحتياطي**.

- **التحقيق من الدخل:** [04_BUSINESS_MONETIZATION.md](04_BUSINESS_MONETIZATION.md)
- **المخطط:** `split_rules`, `payment_split_legs`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| قواعد تقسيم قابلة للإعداد | بوابات دفع حقيقية (Stripe/HyperPay) |
| أرجل دفع لكل حجز (3 أطراف) | تحويل بنكي فعلي |
| معاينة التقسيم قبل الدفع | محفظة متعددة العملات |
| إطلاق حصة الفني عند الاكتمال | KYC للفنيين |
| API للعميل والإدارة | فواتير ضريبية |

---

## قواعد التقسيم الافتراضية

| المستفيد | النسبة | الحالة الابتدائية |
|----------|--------|-------------------|
| المنصة (`platform`) | 15٪ | `released` |
| الفني (`technician`) | 75٪ | `held` |
| الاحتياطي (`reserve`) | 10٪ | `held` |

```
المبلغ الصافي (بعد الخصومات)
  × 15٪ → عمولة المنصة
  × 75٪ → حصة الفني (تُطلَق عند اكتمال الخدمة)
  × 10٪ → احتياطي المنصة
```

---

## جداول قاعدة البيانات

| الجدول | الغرض |
|--------|-------|
| `split_rules` | نسب التقسيم (قاعدة افتراضية + قواعد مستقبلية) |
| `payment_split_legs` | كل سجل دفع → 3 أرجل بحالة مستقلة |

حالات الأرجل: `pending` · `held` · `released` · `paid` · `failed`

---

## API Endpoints

| Method | Path | الوصف | Auth |
|--------|------|-------|------|
| GET | `/api/v1/payments/split-rules` | القواعد النشطة | لا |
| POST | `/api/v1/payments/split/preview` | معاينة التقسيم | لا |
| GET | `/api/v1/bookings/{id}/payment-split` | تفاصيل تقسيم حجز | نعم |
| POST | `/api/v1/payments/splits/release` | إطلاق حصة الفني | Admin |

### معاينة — `POST /api/v1/payments/split/preview`

```json
{ "amount_sar": 90.0 }
```

```json
{
  "data": {
    "amount_sar": 90.0,
    "rule_slug": "default",
    "legs": [
      { "recipient_type": "platform", "label_ar": "عمولة المنصة", "rate": 0.15, "amount_sar": 13.5 },
      { "recipient_type": "technician", "label_ar": "حصة الفني", "rate": 0.75, "amount_sar": 67.5 },
      { "recipient_type": "reserve", "label_ar": "احتياطي", "rate": 0.10, "amount_sar": 9.0 }
    ]
  }
}
```

### تفاصيل حجز — `GET /api/v1/bookings/{id}/payment-split`

```json
{
  "data": {
    "booking_id": "...",
    "payment_id": "...",
    "net_sar": 90.0,
    "legs": [
      {
        "recipient_type": "technician",
        "amount_sar": 67.5,
        "status": "held",
        "label_ar": "حصة الفني"
      }
    ]
  }
}
```

---

## التكامل

1. **`POST /bookings`** — عند الدفع يُنشَأ `Payment` + 3 أرجل في `payment_split_legs`
2. **`booking_revenue`** — يبقى ملخصاً مجمعاً (توافق مع `04`)
3. **اكتمال الحجز** — عند `completed` تُطلَق حصة الفني تلقائياً

---

## واجهة التطبيق

| الشاشة | التحسين |
|--------|---------|
| `booking_screen.dart` | معاينة التقسيم تحت ملخص الفاتورة |

---

## الملفات

```
rousto/docs/08_SPLIT_PAYMENTS_ENGINE.md
rousto/backend/database/009_split_payments_schema.sql
rousto/backend/database/010_split_payments_seed.sql
rousto/backend/api/app/split_payments.py
rousto/backend/api/app/routers/split_payments.py
rousto/backend/api/tests/test_split_payments.py
```

---

## التشغيل

```bash
curl http://localhost:8000/api/v1/payments/split-rules
curl -X POST http://localhost:8000/api/v1/payments/split/preview \
  -H "Content-Type: application/json" \
  -d '{"amount_sar": 90}'
```

---

## الخطوة التالية

- `09_AUTH` — OTP + JWT
- `10_PAYMENT_GATEWAY` — بوابة دفع حقيقية
