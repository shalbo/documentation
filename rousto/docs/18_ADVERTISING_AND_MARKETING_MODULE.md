# 18 — الإعلانات والتسويق | Advertising & Marketing

وحدة **تسويق وإعلانات** لمنصة روستو: حملات، بانرات، شركاء، نشرة بريدية، إحالات، وتتبّع UTM.

- **المصادقة:** [`17_PERMISSIONS_AND_AUTH`](17_PERMISSIONS_AND_AUTH.md)
- **المجلد:** `marketing_*` tables + `admin/marketing.html`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| حملات تسويقية + UTM | A/B testing |
| بانرات ديناميكية (ويب/تطبيق) | إرسال SMS/Email حقيقي |
| شركاء العلامات التجارية | CMS كامل للموقع |
| اشتراك النشرة البريدية | تكامل Facebook/Google Ads |
| برنامج الإحالة + نقاط ولاء | بوابة دفع للحملات |
| إدارة العروض (promotions) | تعدد اللغات |

---

## الجداول

### `marketing_campaigns`

| الحقل | الوصف |
|-------|-------|
| `slug` | معرّف الحملة (`summer-2026`) |
| `channel` | قناة: `web`, `app`, `email`, `social`, `partner` |
| `utm_*` | معاملات UTM للتتبّع |

### `marketing_banners`

| الحقل | الوصف |
|-------|-------|
| `placement` | موضع: `home_hero`, `app_offers`, `booking`, `pricing` |
| `campaign_id` | ربط اختياري بحملة |
| `promotion_id` | ربط اختياري بعرض خصم |

### `marketing_partners`

شريط الشركاء على صفحة الهبوط (بديل HTML ثابت).

### `marketing_newsletter_subscribers`

اشتراكات النشرة من التذييل أو صفحة الأسعار.

### `marketing_referrals` / `marketing_referral_events`

أكواد إحالة مرتبطة بالمستخدمين ونقاط الولاء.

### `marketing_attribution_events`

تتبّع خفيف: `page_view`, `signup`, `booking`.

---

## API Endpoints

### عام

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/marketing/banners` | بانرات نشطة (`?placement=`) |
| GET | `/api/v1/marketing/partners` | شركاء نشطون |
| GET | `/api/v1/marketing/campaigns` | حملات نشطة |
| POST | `/api/v1/marketing/newsletter/subscribe` | اشتراك نشرة |
| POST | `/api/v1/marketing/attribution/track` | تسجيل حدث UTM |
| GET | `/api/v1/marketing/referrals/validate` | التحقق من كود إحالة |

### عميل (مصادق)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/me/referral` | كود الإحالة الخاص بي |
| POST | `/api/v1/me/referral` | إنشاء كود إحالة |

### إدارة (admin)

| Method | Path | الوصف |
|--------|------|-------|
| GET/POST/PATCH | `/api/v1/admin/promotions` | إدارة أكواد الخصم |
| GET/POST/PATCH | `/api/v1/admin/marketing/campaigns` | حملات |
| GET/POST/PATCH | `/api/v1/admin/marketing/banners` | بانرات |
| GET/POST/PATCH | `/api/v1/admin/marketing/partners` | شركاء |
| GET | `/api/v1/admin/marketing/newsletter` | قائمة المشتركين |
| GET/PATCH | `/api/v1/admin/testimonials` | إدارة آراء العملاء |
| GET | `/api/v1/admin/marketing/analytics` | ملخص إحصائي |

---

## الصلاحيات

| الصلاحية | الوصف |
|----------|-------|
| `marketing:read` | قراءة بيانات التسويق |
| `marketing:manage` | إدارة حملات وبانرات وشركاء |
| `promotions:manage` | إدارة أكواد الخصم |
| `testimonials:manage` | نشر وإخفاء آراء العملاء |
| `newsletter:manage` | عرض مشتركي النشرة |

---

## الواجهة

| الملف | الوصف |
|-------|-------|
| `web/index.html` | شركاء + آراء + بانر ديناميكي |
| `web/js/landing-pricing.js` | جلب بيانات التسويق |
| `admin/marketing.html` | لوحة إدارة التسويق |
| `admin/js/marketing-admin.js` | CRUD حملات/بانرات/عروض |

---

## التشغيل

```bash
cd rousto/backend && docker compose up -d
cd rousto && python3 -m http.server 8080
```

- الهبوط: http://localhost:8080/web/index.html
- إدارة التسويق: http://localhost:8080/admin/marketing.html

**مستخدم تجريبي:** `+966501234567` — كود إحالة: `SAUD100`

---

## الخطوة التالية

- تكامل Flutter مع `/marketing/banners` في شاشة العروض
- إرسال بريد حقيقي للنشرة (SendGrid/Mailgun)
