# 42 — الهوية البصرية وأيقونة التطبيق

## الألوان المعتمدة

| اللون | الكود |
|-------|-------|
| أحمر تفاعلي | `#C1121F` |
| كحلي فخم | `#003049` |

## Flutter — أيقونة التطبيق

- الحزمة: `flutter_launcher_icons`
- الإعداد: `app_flutter/flutter_launcher_icons.yaml`
- الأصول:
  - `assets/app_icon.png` — أيقونة كاملة بخلفية كحلية
  - `assets/app_icon_foreground.png` — الماركة للأيقونة التكيفية (Android)

```bash
cd app_flutter
flutter pub get
dart run flutter_launcher_icons
```

**Android Adaptive Icons:** خلفية `#003049` + foreground شفاف للماركة.

## Admin — الشعار

| المسار | الاستخدام |
|--------|-----------|
| `admin/static/images/logo.png` | شعار عالي الدقة للوحة التحكم |
| `backend/api/static/images/logo.png` | `GET /static/images/logo.png` |
| `brand/col.png` | مرجع الهوية (نسخة PNG) |

### أماكن الدمج

1. **تسجيل الدخول:** `admin/login.html` — شعار مركزي 220×84px
2. **Navbar:** `js/brand-topbar.js` — يحقن الشعار في كل `.topbar` (120×46px، `object-fit: contain`)
3. **الفواتير:** `admin/templates/invoice.html` + `css/invoice.css` — ترويسة طباعة 180×68px

## CSS — منع التمدد

```css
.brand-logo, .login-logo, .invoice-logo {
  object-fit: contain;
  height: auto;
}
```
