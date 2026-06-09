# 15 — واجهة الويب الأمامية | Front-End Web

بوابة **عميل ويب** موحّدة لمنصة روستو — RTL عربي، متصلة بـ REST API.

- **المصادقة (لاحقاً):** `16_AUTH`
- **المجلد:** `rousto/web/`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| لوحة تحكم العميل | لوحة الإدارة (`admin/`) |
| حجز خدمة عبر API | بوابة دفع حقيقية |
| تتبّع التوصيل والدعم | SPA framework (React/Vue) |
| حسابي (ملف + سيارات + طلبات) | تسجيل دخول JWT |
| ترويسة وتذييل موحّد | i18n |

---

## الصفحات

| الصفحة | الملف | API |
|--------|-------|-----|
| الهبوط | `index.html` | `/landing/page` |
| لوحة التحكم | `dashboard.html` | `/me`, `/bookings/active` |
| الحجز | `booking.html` | `/categories/tree`, `POST /bookings` |
| حسابي | `account.html` | `/me`, `/me/vehicles`, `/bookings` |
| الأسعار | `pricing.html` | `/landing/pricing` |
| التتبّع | `delivery-map.html` | `/bookings/active/delivery-map` |
| الدعم | `support.html` | `/support/*` |
| السطحة | `towing-map.html` | `/towing/dispatches/*` |

---

## البنية المشتركة

```
web/
├── css/
│   ├── theme.css          # متغيرات الهوية
│   ├── styles.css         # صفحة الهبوط
│   ├── portal.css         # بوابة العميل
│   └── delivery-map.css   # خرائط
└── js/
    ├── api.js             # عميل API + إعدادات localStorage
    ├── portal-layout.js   # ترويسة/تذييل موحّد
    ├── dashboard.js
    ├── booking.js
    ├── account.js
    ├── landing-pricing.js
    ├── delivery-map.js
    └── support.js
```

### الإعدادات (مؤقتة)

```javascript
localStorage.rousto_web_config = {
  apiBase: "http://localhost:8000",
  userId: "a0000000-0000-4000-8000-000000000001"
}
```

يُرسل `X-User-Id` مع طلبات العميل.

---

## التشغيل

```bash
cd rousto/backend && docker compose up -d
cd rousto && python3 -m http.server 8080
```

- لوحة التحكم: http://localhost:8080/web/dashboard.html
- الحجز: http://localhost:8080/web/booking.html
- حسابي: http://localhost:8080/web/account.html

---

## الخطوة التالية

- `16_AUTH` — OTP + JWT + أدوار
