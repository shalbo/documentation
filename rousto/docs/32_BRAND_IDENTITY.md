# 32 — الهوية البصرية (col.png)

## لوحة الألوان

| Token | Hex | الاستخدام |
|-------|-----|-----------|
| `brand-red` | `#C1121F` | أزرار CTA، تنبيهات، إضافة للسلة |
| `brand-navy` | `#003049` | عناوين، AppBar، أيقونات نشطة |
| `brand-bg` | `#F8F9FA` | خلفيات النظام |

## Flutter

- `app_colors.dart` — الألوان
- `app_theme.dart` — ThemeData (AppBar كحلي، أزرار حمراء، radius 14)
- `app_decorations.dart` — ظلال ناعمة + `BorderRadius.circular(14)`

## Admin

- `admin/css/admin.css` — `--brand-red`, `--brand-navy`
- `admin/tailwind.config.js` — `brand-red`, `brand-navy`, `rounded-brand`

## شاشة قطع الغيار / VIN

- بطاقات بيضاء + نصوص كحلية
- زر «أضف للسلة» أحمر
- شارة تطابق VIN: أخضر هادئ + علامة صح
