# Rousto Brand Colors (col.png)

| Token | Hex | Usage |
|-------|-----|--------|
| **brand-red** | `#C1121F` | CTA buttons, alerts, primary actions |
| **brand-navy** | `#003049` | Headers, titles, active icons, structural cards |
| **brand-bg** | `#F8F9FA` | App & admin backgrounds |
| brand-red-050 | `#FCE8EA` | Soft red tint badges |
| brand-navy-050 | `#E8EEF2` | Soft navy tint panels |
| brand-green | `#2D9F6F` | VIN match / success badges |

## Flutter

`app_flutter/lib/theme/app_colors.dart` + `app_theme.dart` + `app_decorations.dart`

## Admin / Web

- `admin/css/admin.css` — CSS variables `--brand-red`, `--brand-navy`
- `admin/tailwind.config.js` — `brand-red`, `brand-navy` Tailwind tokens

## Radius

All cards and buttons: **14px** (`BorderRadius.circular(14)` / `rounded-brand`)
