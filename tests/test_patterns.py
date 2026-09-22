"""Unit tests for the weekly pattern and anomaly detection report (Stretch Goal)."""

from supportpipe.patterns.report import analyze_ticket_patterns, format_markdown_pattern_report
from supportpipe.schemas import ExtractedFields, PipelineResult, Ticket


def test_analyze_ticket_patterns_detects_payment_spike() -> None:
    """Verify that a high concentration of failed transfers triggers a systemic payment flag."""
    tickets = [
        Ticket(
            ticket_id=f"TKT-P-{i}",
            channel="app",
            raw_text="حولت وما وصل",
            submitted_at="2026-09-22T10:00:00+03:00",
            synthetic_user_id=f"SYN-{i}",
        )
        for i in range(10)
    ]

    results = [
        PipelineResult(
            ticket_id=f"TKT-P-{i}",
            category="failed_transfer",
            category_confidence=0.90,
            priority="high",
            priority_confidence=0.85,
            extracted_fields=ExtractedFields(),
            team="Payments & Transfers",
            escalated=False,
            provider_path="mock+template",
        )
        for i in range(10)
    ]

    analysis = analyze_ticket_patterns(results, tickets)
    assert analysis["total_tickets_analyzed"] == 10
    assert len(analysis["detected_systemic_incidents"]) >= 1
    assert "Payment Gateway" in analysis["detected_systemic_incidents"][0]["incident_type"]

    md_report = format_markdown_pattern_report(analysis)
    assert "تقرير الأنماط الأسبوعية" in md_report
    assert "failed_transfer" in md_report
