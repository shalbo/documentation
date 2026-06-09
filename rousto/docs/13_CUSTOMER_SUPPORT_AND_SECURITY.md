# 13 — دعم العملاء والأمان | Customer Support & Security

نظام **تذاكر الدعم**، **الأسئلة الشائعة**، وسجل **أحداث الأمان** لمنصة روستو.

- **المصادقة (لاحقاً):** `17_PERMISSIONS_AND_AUTH`
- **المخطط:** `support_tickets`, `support_ticket_messages`, `support_faq`, `security_audit_logs`

---

## النطاق

| داخل النطاق | خارج النطاق |
|-------------|-------------|
| إنشاء ومتابعة تذاكر الدعم | مركز اتصال هاتفي |
| رسائل بين العميل والإدارة | دردشة مباشرة WebSocket |
| أسئلة شائعة (FAQ) | ذكاء اصطناعي للرد |
| سجل تدقيق أمني | SIEM متقدم |
| الإبلاغ عن نشاط مشبوه | KYC / 2FA حقيقي |
| لوحة إدارة التذاكر | تكامل Zendesk |

---

## التذاكر

| الحقل | القيم |
|-------|-------|
| `category` | booking · payment · account · technical · other |
| `priority` | low · normal · high · urgent |
| `status` | open · in_progress · waiting_customer · resolved · closed |

---

## API Endpoints

### عام

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/support/faq` | الأسئلة الشائعة |

### العميل (`X-User-Id`)

| Method | Path | الوصف |
|--------|------|-------|
| POST | `/api/v1/support/tickets` | فتح تذكرة |
| GET | `/api/v1/support/tickets` | تذاكري |
| GET | `/api/v1/support/tickets/{id}` | تفاصيل + رسائل |
| POST | `/api/v1/support/tickets/{id}/messages` | إضافة رد |
| GET | `/api/v1/me/security` | ملخص الأمان |
| POST | `/api/v1/me/security/report` | الإبلاغ عن نشاط مشبوه |

### إدارة (`X-Admin-Key`)

| Method | Path | الوصف |
|--------|------|-------|
| GET | `/api/v1/admin/support/tickets` | كل التذاكر |
| PATCH | `/api/v1/admin/support/tickets/{id}` | تحديث الحالة/الأولوية |
| POST | `/api/v1/admin/support/tickets/{id}/reply` | رد الإدارة |
| GET | `/api/v1/admin/security/events` | سجل الأحداث الأمنية |

---

## أمثلة

### فتح تذكرة

```json
{
  "category": "booking",
  "subject": "تأخير في وصول الفني",
  "message": "الفني تأخر أكثر من 30 دقيقة عن الموعد",
  "booking_id": "i0000000-0000-4000-8000-000000000001",
  "priority": "high"
}
```

### ملخص الأمان — `GET /me/security`

```json
{
  "data": {
    "login_alerts_enabled": true,
    "recent_events": [
      { "event_type": "ticket_created", "severity": "info", "created_at": "..." }
    ],
    "open_tickets_count": 1
  }
}
```

---

## الواجهات

| الصفحة | الغرض |
|--------|-------|
| `web/support.html` | بوابة العميل — FAQ + تذاكر |
| `admin/support.html` | إدارة التذاكر |
| `admin/security.html` | سجل الأحداث الأمنية |

---

## الملفات التنفيذية

```
rousto/backend/database/019_support_security_schema.sql
rousto/backend/database/020_support_security_seed.sql
rousto/backend/api/app/support_services.py
rousto/backend/api/app/routers/support.py
```

---

## الخطوة التالية

- `17_PERMISSIONS_AND_AUTH` — OTP + JWT + أدوار
