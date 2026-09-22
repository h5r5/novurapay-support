"""Integration tests for the complete pipeline execution and review queue storage."""

from supportpipe.logging_store import mask_pii
from supportpipe.pipeline import process_ticket, run_batch
from supportpipe.schemas import Ticket


def test_process_clean_transfer_ticket() -> None:
    """Verify processing of a clear failed transfer ticket."""
    ticket = Ticket(
        ticket_id="TKT-TEST-001",
        channel="app",
        raw_text="حولت مبلغ 50,000 دينار لصديقي وما وصل ورقم العملية TXN-99887766 امس بالليل",
        submitted_at="2026-09-22T12:00:00+03:00",
        synthetic_user_id="SYN-USR-001",
    )

    result = process_ticket(ticket)
    assert result.ticket_id == "TKT-TEST-001"
    assert result.category == "failed_transfer"
    assert result.team == "Payments & Transfers"
    assert result.escalated is False
    assert result.extracted_fields.amount_iqd == 50000
    assert result.extracted_fields.transaction_ref == "TXN-99887766"
    assert result.extracted_fields.event_date_resolved == "2026-09-21"
    assert result.draft_reply is not None
    assert "فريق التحويلات" in result.draft_reply


def test_process_vague_ticket_escalates() -> None:
    """Verify processing of a vague ticket triggers escalation with clear reason."""
    ticket = Ticket(
        ticket_id="TKT-TEST-002",
        channel="whatsapp",
        raw_text="مرحبا",
        submitted_at="2026-09-22T13:00:00+03:00",
        synthetic_user_id="SYN-USR-002",
    )

    result = process_ticket(ticket)
    assert result.ticket_id == "TKT-TEST-002"
    assert result.category == "unclear_or_incomplete"
    assert result.escalated is True
    assert result.escalation_reason is not None
    assert "تذكرة مصعدة" in (result.draft_reply or "")


def test_run_batch_summary() -> None:
    """Verify run_batch processes list of tickets and produces accurate summary."""
    tickets = [
        Ticket(
            ticket_id="TKT-B-1",
            channel="app",
            raw_text="حولت 25000 دينار والتحويل معلق رقم العملية TXN-11223344 امس",
            submitted_at="2026-09-22T10:00:00+03:00",
            synthetic_user_id="SYN-01",
        ),
        Ticket(
            ticket_id="TKT-B-2",
            channel="sms",
            raw_text="نسيت باسورد الدخول للتطبيق وما استلم رمز التأكيد",
            submitted_at="2026-09-22T10:05:00+03:00",
            synthetic_user_id="SYN-02",
        ),
        Ticket(
            ticket_id="TKT-B-3",
            channel="app",
            raw_text="الو",
            submitted_at="2026-09-22T10:10:00+03:00",
            synthetic_user_id="SYN-03",
        ),
    ]

    results, summary = run_batch(tickets)
    assert len(results) == 3
    assert summary.total_tickets == 3
    assert summary.category_counts.get("failed_transfer") == 1
    assert summary.category_counts.get("login_problem") == 1
    assert summary.category_counts.get("unclear_or_incomplete") == 1
    assert summary.escalated_count >= 1
    assert summary.avg_latency_ms >= 0.0


def test_pii_masking() -> None:
    """Verify phone and ID masking in logging store."""
    raw_text = "رقم هاتفي هو 07801234567 ورقم هويتي 102938475612"
    masked = mask_pii(raw_text)
    assert "07801234567" not in masked
    assert "102938475612" not in masked
    assert "[PHONE_SCRUBBED]" in masked
    assert "[ID_SCRUBBED]" in masked
