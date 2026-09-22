"""Weekly pattern and systemic anomaly detection report generator (Topic 06 Stretch)."""

from collections import Counter
from datetime import datetime
from typing import Any

from supportpipe.schemas import PipelineResult, Ticket


def analyze_ticket_patterns(results: list[PipelineResult], tickets: list[Ticket]) -> dict[str, Any]:
    """Analyze batch of tickets to detect rising categories and potential systemic incidents."""
    total = len(results)
    if total == 0:
        return {"status": "empty_batch"}

    # 1. Category frequencies & velocity
    category_counts = Counter(r.category for r in results)
    top_categories = category_counts.most_common(5)

    # 2. Priority & Escalation distribution
    escalation_reasons = Counter(
        r.escalation_reason for r in results if r.escalated and r.escalation_reason
    )

    # 3. Systemic Incident Detection Heuristics
    # A: Concentrated failed transfers or payment failures
    payment_issues = [
        r for r in results if r.category in ["failed_transfer", "bill_payment_failure"]
    ]
    payment_spike = len(payment_issues) >= 5 and (len(payment_issues) / total > 0.20)

    # B: Concentrated authentication/OTP outages
    login_issues = [r for r in results if r.category == "login_problem"]
    auth_gateway_spike = len(login_issues) >= 5 and (len(login_issues) / total > 0.15)

    systemic_flags = []
    if payment_spike:
        systemic_flags.append(
            {
                "incident_type": "Payment Gateway Delays / Pending Switch Operations",
                "incident_type_ar": "تأخر في بوابة الدفع أو عمليات معلقة في المقاصة",
                "affected_tickets_count": len(payment_issues),
                "severity": "High",
                "recommendation_ar": "التواصل مع فريق العمليات البنكية للتحقق من سلامة خطوط الربط مع بوابات الدفع.",
            }
        )

    if auth_gateway_spike:
        systemic_flags.append(
            {
                "incident_type": "SMS OTP Gateway Failure",
                "incident_type_ar": "عطل أو تأخير في وصول رسائل رمز التحقق (OTP SMS)",
                "affected_tickets_count": len(login_issues),
                "severity": "Medium",
                "recommendation_ar": "التحقق من حالة مزود خدمة الرسائل النصية القصيرة ومسارات التوصيل.",
            }
        )

    return {
        "analysis_timestamp": datetime.now().isoformat(),
        "total_tickets_analyzed": total,
        "category_breakdown": dict(category_counts),
        "top_issues": [
            {"category": cat, "count": count, "pct": round(count / total * 100, 1)}
            for cat, count in top_categories
        ],
        "top_escalation_reasons": [
            {"reason": reason, "count": count}
            for reason, count in escalation_reasons.most_common(3)
        ],
        "detected_systemic_incidents": systemic_flags,
    }


def format_markdown_pattern_report(pattern_data: dict[str, Any]) -> str:
    """Format pattern analysis into an executive weekly support report."""
    md = []
    md.append("# 📈 تقرير الأنماط الأسبوعية والحوادث المحتملة (Weekly Pattern Report)")
    md.append(
        f"*تاريخ التحليل:* `{pattern_data.get('analysis_timestamp')}` | *إجمالي التذاكر:* **{pattern_data.get('total_tickets_analyzed')}**"
    )
    md.append("\n---\n")

    md.append("### 1. أكثر المشاكل تكراراً (Top Recurring Categories)")
    md.append("| الفئة | عدد التذاكر | النسبة المئوية |")
    md.append("|---|---|---|")
    for item in pattern_data.get("top_issues", []):
        md.append(f"| `{item['category']}` | {item['count']} | {item['pct']}% |")

    md.append("\n### 2. التنبيهات والحوادث النظامية المحتملة (Systemic Incidents)")
    incidents = pattern_data.get("detected_systemic_incidents", [])
    if not incidents:
        md.append("لم يتم رصد أي حوادث نظامية طارئة خلال هذه الدفعة. التدفق طبيعي.")
    else:
        for inc in incidents:
            md.append(f"- **{inc['incident_type_ar']}** (`{inc['incident_type']}`)")
            md.append(f"  - مستوى الخطورة: **{inc['severity']}**")
            md.append(f"  - عدد التذاكر المتأثرة: **{inc['affected_tickets_count']}**")
            md.append(f"  - التوصية التشغيلية: {inc['recommendation_ar']}")

    return "\n".join(md)
