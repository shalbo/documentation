"""محرك تشخيص تجريبي — يُستبدل بموصل رؤية حقيقي في الإنتاج."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DiagnosisFinding:
    code: str
    label_ar: str
    severity: str
    confidence: float
    service_slug: str
    details: dict


SCAN_TYPE_CATALOG = [
    {
        "id": "dashboard_warning",
        "label_ar": "أضواء تحذير (الطبلون)",
        "description_ar": "صورة لأضواء التحذير المضاءة على لوحة القيادة",
        "icon_key": "warning",
    },
    {
        "id": "tire_tread",
        "label_ar": "الإطارات والتآكل",
        "description_ar": "صورة واضحة لسطح الإطار أو التآكل",
        "icon_key": "tire_repair",
    },
    {
        "id": "fluid_leak",
        "label_ar": "تسرب سوائل",
        "description_ar": "صورة لبقعة زيت أو سائل تحت السيارة",
        "icon_key": "water_drop",
    },
    {
        "id": "body_damage",
        "label_ar": "خدوش وصدمات",
        "description_ar": "صورة للضرر الخارجي في الهيكل",
        "icon_key": "car_crash",
    },
    {
        "id": "battery_corrosion",
        "label_ar": "البطارية والأكسدة",
        "description_ar": "صورة لقطب البطارية أو الأكسدة",
        "icon_key": "battery_charging",
    },
]

_PROFILES: dict[str, list[DiagnosisFinding]] = {
    "dashboard_warning": [
        DiagnosisFinding(
            code="check_engine",
            label_ar="ضوء فحص المحرك — يُنصح بفحص إلكتروني",
            severity="medium",
            confidence=0.82,
            service_slug="diagnostics",
            details={"hint": "قد يشير إلى خلل في المستشعرات أو نظام الاحتراق"},
        ),
    ],
    "tire_tread": [
        DiagnosisFinding(
            code="tire_wear",
            label_ar="تآكل غير متساوٍ في الإطار",
            severity="medium",
            confidence=0.78,
            service_slug="tires",
            details={"hint": "يُنصح بالترصيص وفحص ضغط الإطارات"},
        ),
    ],
    "fluid_leak": [
        DiagnosisFinding(
            code="oil_leak",
            label_ar="تسرب محتمل لزيت المحرك",
            severity="high",
            confidence=0.85,
            service_slug="oil-change",
            details={"hint": "فحص فوري لمنع تلف المحرك"},
        ),
    ],
    "body_damage": [
        DiagnosisFinding(
            code="surface_scratch",
            label_ar="خدش سطحي — فحص إضافي موصى به",
            severity="low",
            confidence=0.71,
            service_slug="diagnostics",
            details={"hint": "قد يخفي ضرراً هيكلياً غير ظاهر"},
        ),
    ],
    "battery_corrosion": [
        DiagnosisFinding(
            code="battery_corrosion",
            label_ar="أكسدة على أقطاب البطارية",
            severity="medium",
            confidence=0.88,
            service_slug="battery",
            details={"hint": "تنظيف الأقطاب واختبار قوة البطارية"},
        ),
    ],
}


def get_scan_type_catalog() -> list[dict]:
    return SCAN_TYPE_CATALOG


def is_valid_scan_type(scan_type: str) -> bool:
    return scan_type in _PROFILES


def analyze(scan_type: str, *, image_count: int) -> list[DiagnosisFinding]:
    if not is_valid_scan_type(scan_type):
        raise ValueError("نوع الفحص غير مدعوم")

    findings = list(_PROFILES[scan_type])
    if image_count > 1 and findings:
        boosted = DiagnosisFinding(
            code=findings[0].code,
            label_ar=findings[0].label_ar,
            severity=findings[0].severity,
            confidence=min(0.95, findings[0].confidence + 0.05),
            service_slug=findings[0].service_slug,
            details={**findings[0].details, "multi_image_boost": True},
        )
        return [boosted]
    return findings
