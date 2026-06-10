# 40 — المدفوعات المحلية الليبية والمحفظة المالية

نظام مدفوعات **ليبي فقط** (LYD) — بدون Stripe/PayPal.

## البوابات المعتمدة

| البوابة | الاستخدام |
|---------|-----------|
| `cod` | كاش عند الاستلام |
| `wallet` | رصيد محفظة Rousto |
| `muamalat` | معاملات — مصرف الجمهورية (OTP + بطاقة) |
| `sadad` | سداد — المدار الجديد (موبايل) |
| `edfali` | إدفع لي / تداول كاش |

البوابات الدولية **محظورة برمجياً** (`BLOCKED_GATEWAYS`).

## الجداول

- `wallets` — عميل / تاجر / سائق / منصة
- `wallet_transactions` — deposit, withdraw, payment, commission
- `withdrawal_requests` — طلب سحب التاجر
- `gateway_payments` — جلسات الدفع
- `payment_audit_logs` — تدقيق مالي

## APIs

### العميل
- `GET /api/v1/payments/libyan/options`
- `POST /api/v1/payments/checkout`
- `GET /api/v1/me/wallet`
- `POST /api/v1/me/wallet/topup`

### Webhooks
- `POST /api/v1/webhooks/payments/{muamalat|sadad|edfali}` + `X-Signature`

### التاجر
- `GET /api/v1/vendor/wallet`
- `POST /api/v1/vendor/wallet/withdraw`

### الأدمن
- `GET /api/v1/admin/payments/overview`
- `GET /api/v1/admin/withdrawals`
- `PATCH /api/v1/admin/withdrawals/{id}`

## العمولة

تُقتطع تلقائياً عند إتمام الدفع (`DB transaction`) حسب `tiers.platform_commission_rate`:
- standard: 15%
- professional: 12%
- enterprise: 8%

## الواجهات

| الشاشة | المسار |
|--------|--------|
| الدفع (Flutter) | `app_flutter/lib/screens/checkout_screen.dart` |
| محفظة التاجر | `admin/vendor-wallet.html` |
| مدفوعات الأدمن | `admin/payments-admin.html` |

## إعدادات البيئة

```
GATEWAY_SANDBOX_MODE=true
MUAMALAT_WEBHOOK_SECRET=...
SADAD_WEBHOOK_SECRET=...
EDFALI_WEBHOOK_SECRET=...
PAYMENT_RETURN_URL_BASE=https://pay.rousto.ly
```
