# 21 — الترجمة والجاهزية للإطلاق | i18n & Launch Readiness

## الموديل 1: الترجمة (ar / en)

| المكوّن | التنفيذ |
|---------|---------|
| Flutter | `app_ar.arb` / `app_en.arb`, `LocaleState`, `SettingsScreen`, RTL/LTR |
| Backend | `Accept-Language`, `030/031` migrations, `pick_localized()` |
| Web | `web/i18n/*.json`, `js/i18n.js`, `?lang=en` + `dir` ديناميكي |

## الموديل 2: FCM

- إشعارات: حجز، دعم، سحب، تاجر، سائق (15 كم)
- Flutter: بانر foreground + deep link + اهتزاز للطوارئ

## الموديل 3: الأداء

- Cache invalidation عند تعديل الكتالوج
- ضغط WebP للصور (`scan_services.py`)
- `dispose` للـ Timer في شاشات التتبع

## الموديل 4: الأمان

- Rate limit: OTP، بحث الكتالوج (60/د)، حجز، رفع فحص
- فحص ملكية الحجز/التذاكر/الإشعارات (موجود)
- توسّع: [`23_SECURITY_HARDENING`](23_SECURITY_HARDENING.md) — رؤوس HTTP، تدقيق الدخول، rate limit إدارة

## الموديل 5: SEO والقانونية

- `sitemap.xml` مع hreflang
- OG meta + `og:image`
- `LegalScreen` في Flutter (خصوصية، شروط، ضمان)
