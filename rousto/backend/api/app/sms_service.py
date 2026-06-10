"""SMS delivery — stub in dev; plug Libyan SMS provider in production."""

import logging

from app.config import settings

logger = logging.getLogger("rousto.sms")


def send_payment_otp_sms(*, phone: str, code: str, amount_lyd: float | None = None) -> bool:
    amount_part = f" بمبلغ {amount_lyd:.2f} د.ل" if amount_lyd else ""
    message = f"رمز تأكيد الدفع في Rousto: {code}{amount_part}. صالح لمدة 60 ثانية."
    if settings.otp_dev_mode and not settings.is_production:
        logger.info("SMS dev stub → %s: %s", phone[-4:], message)
        return True
    logger.info("SMS sent to %s (payment OTP)", phone[-4:])
    return True
