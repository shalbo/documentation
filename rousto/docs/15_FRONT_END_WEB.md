# 15 — واجهة الويب الأمامية | Front-End Web

بوابة **عميل ويب** موحّدة لمنصة روستو — RTL عربي، متصلة بـ REST API.

- **المصادقة:** [`17_PERMISSIONS_AND_AUTH`](17_PERMISSIONS_AND_AUTH.md)
- **المجلد:** `rousto/web/`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| لوحة تحكم العميل | لوحة الإدارة (`admin/`) |
| حجز خدمة عبر API | بوابة دفع حقيقية |
| تتبّع التوصيل والدعم | SPA framework (React/Vue) |
| حسابي (ملف + سيارات + طلبات) | i18n |
| تسجيل دخول OTP + JWT | SMS حقيقي |

---

## الصفحات

| الصفحة | الملف | API |
|--------|-------|-----|
| الهبوط | `index.html` | `/landing/page` |
| تسجيل الدخول | `login.html` | `/auth/otp/*` |
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
├── login.html             # OTP + JWT
└── js/
    ├── api.js             # عميل API + JWT + إعدادات localStorage
    ├── portal-layout.js   # ترويسة/تذييل + دخول/خروج
    ├── login.js
    ├── dashboard.js
    ├── booking.js
    ├── account.js
    ├── landing-pricing.js
    ├── delivery-map.js
    └── support.js
```

### الإعدادات

```javascript
localStorage.rousto_web_config = {
  apiBase: "http://localhost:8000",
  accessToken: "<jwt>",
  refreshToken: "<refresh>",
  userId: "a0000000-0000-4000-8000-000000000001"
}
```

- عند وجود `accessToken` يُرسل `Authorization: Bearer`
- بدون توكن: يُرسل `X-User-Id` للتطوير

---

## التشغيل

```bash
cd rousto/backend && docker compose up -d
cd rousto && python3 -m http.server 8080
```

- تسجيل الدخول: http://localhost:8080/web/login.html
- لوحة التحكم: http://localhost:8080/web/dashboard.html
- الحجز: http://localhost:8080/web/booking.html
- حسابي: http://localhost:8080/web/account.html

**مستخدم تجريبي:** `+966501234567` — الرمز في وضع التطوير: `123456`

---

## الخطوة التالية

- [`17_PERMISSIONS_AND_AUTH`](17_PERMISSIONS_AND_AUTH.md) — OTP + JWT + أدوار ✅
