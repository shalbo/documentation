# 24 — شبكة اللوجستيات والسائقين | Logistics & Driver Network

طبقة **Driver Network** فوق اللوجستيات (07) وإرسال السطحات (12) — تمييز السائقين، حوض المهام، التسعير، والإلغاء.

- **يعتمد على:** [`07_LOGISTICS_AND_LAST_MILE`](07_LOGISTICS_AND_LAST_MILE.md)، [`12_TOWING_DISPATCH_MAP`](12_TOWING_DISPATCH_MAP.md)
- **لوحة الإدارة:** `admin/drivers.html`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| تمييز السائق (service/tow/courier) | تطبيق سائق مستقل |
| حوض مهام السحب (job pool) | Google Directions |
| قبول المهمة ذاتياً | WebSocket |
| تسعير السحب (أساس + كم) | تسعير ديناميكي معقد |
| إلغاء وتقييم | KYC للسائقين |

---

## أنواع السائقين (`driver_type`)

| النوع | الوصف |
|-------|-------|
| `service` | فني خدمة منزلية |
| `tow` | سائق سطحة |
| `courier` | مندوب توصيل (محجوز) |

---

## تسعير السحب

```
total_fare = base_fare (75 ر.س) + total_route_km × per_km (8 ر.س)
```

---

## API — السائق (JWT فني)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/driver/me/jobs/available` | مهام سحب متاحة ضمن 25 كم |
| POST | `/api/v1/driver/me/jobs/{id}/accept` | قبول مهمة |
| GET | `/api/v1/driver/me/jobs/active` | المهمة النشطة |

---

## API — العميل

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/towing/dispatches` | سجل طلبات السحب |
| POST | `/api/v1/towing/dispatches/{id}/cancel` | إلغاء (pending/dispatched) |
| POST | `/api/v1/towing/dispatches/{id}/rate` | تقييم السائق (1–5) |

---

## API — الإدارة

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/drivers` | قائمة السائقين |
| GET | `/api/v1/admin/drivers/analytics` | إحصائيات الشبكة |
| PATCH | `/api/v1/admin/drivers/{id}/availability` | تفعيل/تعطيل التوفر |

---

## الملفات

| المكوّن | الملف |
|---------|-------|
| Schema | `database/034_driver_network_schema.sql` |
| Seed | `database/035_driver_network_seed.sql` |
| Services | `app/driver_network_services.py` |
| Router | `app/routers/driver_network.py` |
| Dashboard | `admin/drivers.html`, `admin/js/drivers.js` |
| Tests | `tests/test_driver_network.py` |

---

## التشغيل

```bash
cd rousto/backend && docker compose up -d
# لوحة السائقين: http://localhost:8080/admin/drivers.html
# سائق تجريبي: X-Vendor-Id: v0000000-0000-4000-8000-000000000003
```
