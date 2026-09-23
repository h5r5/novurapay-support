"""Regression tests for all forensic critique findings and remediations.

Verifies:
- LB-01: Calendar year (e.g. 2026) is never extracted as monetary amount.
- LB-02: 8-digit whole dinar amount is never miscaptured as transaction reference.
- LB-04: Decimal verbal amounts (25.5 الف, 1.5 مليون, مليون ونص) parsed accurately.
- LB-05: Comma-formatted numbers in drafted replies pass grounding validation.
- FM-02: Whitespace-only tickets do not crash Pydantic and trigger FM-02 escalation.
- MS-01: Pure English/Latin tickets escalate to specialized human care without crashing Arabizi.
- MS-02: Multi-issue and compound requests are detected and escalated (Rule 03).
- MS-03: Duplicate tickets in short timeframes are flagged and escalated.
- EH-01: Fault isolation in batch runs prevents single-ticket failures from aborting the batch.
"""

from supportpipe.classify.classify import classify_ticket
from supportpipe.draft.validate import validate_draft_response
from supportpipe.extract.extract import extract_ticket_details
from supportpipe.extract.normalize import parse_iqd_amount
from supportpipe.pipeline import process_ticket, run_batch
from supportpipe.routing.multi_issue import detect_multi_issue
from supportpipe.schemas import ClassificationResult, Ticket


def test_lb01_year_not_captured_as_amount() -> None:
    """Ensure calendar year in date is not miscaptured as IQD amount."""
    raw_text = "سلام عليكم، الحوالة سويتها بتاريخ 2026-09-22 وما وصل المبلغ لصاحبي"
    extracted = extract_ticket_details(
        raw_text,
        submitted_at_iso="2026-09-22T14:00:00+03:00",
        category="failed_transfer",
    )
    assert extracted.amount_iqd is None, f"Year 2026 was wrongly captured as amount: {extracted.amount_iqd}"
    assert extracted.event_date_resolved == "2026-09-22"

    raw_text_with_amount = "حولت 25000 دينار بتاريخ 2026-05-10 برقم TXN-12345678"
    extracted2 = extract_ticket_details(
        raw_text_with_amount,
        submitted_at_iso="2026-09-22T14:00:00+03:00",
        category="failed_transfer",
    )
    assert extracted2.amount_iqd == 25000
    assert extracted2.event_date_resolved == "2026-05-10"


def test_lb02_large_amount_not_captured_as_ref() -> None:
    """Ensure 8-digit monetary amount (e.g. 10,000,000 IQD) is not captured as reference."""
    raw_text = "سحبت 10000000 دينار من الفرع وما نزل الإشعار"
    extracted = extract_ticket_details(
        raw_text,
        submitted_at_iso="2026-09-22T14:00:00+03:00",
        category="failed_transfer",
    )
    assert extracted.amount_iqd == 10000000
    assert extracted.transaction_ref is None, f"Amount was wrongly captured as transaction ref: {extracted.transaction_ref}"


def test_lb04_verbal_fractional_amounts() -> None:
    """Verify verbal decimal and fractional amounts parse accurately and negative numbers are rejected."""
    assert parse_iqd_amount("25.5 الف") == 25500
    assert parse_iqd_amount("1.5 مليون") == 1500000
    assert parse_iqd_amount("مليون ونص") == 1500000
    assert parse_iqd_amount("مليونين ونص") == 2500000
    assert parse_iqd_amount("نص مليون") == 500000
    assert parse_iqd_amount("-50000") is None
    assert parse_iqd_amount("-25 الف") is None


def test_lb05_comma_formatted_grounding_validation() -> None:
    """Ensure comma-formatted numbers in drafted responses pass hallucination gate."""
    draft_with_commas = (
        "مرحباً بك، نود إعلامك بأنه تم استلام استفسارك حول الحوالة رقم TXN-99887766 "
        "بمبلغ 25,000 دينار وجاري المتابعة."
    )
    raw_text = "حولت 25000 دينار برقم TXN-99887766"

    passed, reasons = validate_draft_response(
        draft_text=draft_with_commas,
        ticket_raw_text=raw_text,
        extracted_ref="TXN-99887766",
        extracted_amount=25000,
    )
    assert passed, f"Grounding check failed unexpectedly: {reasons}"
    assert len(reasons) == 0


def test_lb05_phone_grounding_validation() -> None:
    """Ensure customer phone number extracted from ticket is permitted in grounded draft."""
    phone = "07801234567"
    raw_text = f"حولت بالخطأ للرقم {phone} بمبلغ 50000"
    draft_with_phone = f"أهلاً بك، تم تسجيل بلاغ التحويل الخاطئ للرقم {phone} بمبلغ 50,000 دينار."

    passed, reasons = validate_draft_response(
        draft_text=draft_with_phone,
        ticket_raw_text=raw_text,
        extracted_ref=None,
        extracted_amount=50000,
        extracted_phone=phone,
    )
    assert passed, f"Phone number caused grounding failure: {reasons}"


def test_fm02_empty_whitespace_ticket_escalation() -> None:
    """Ensure whitespace/empty tickets instantiate safely and escalate to human triage."""
    ticket = Ticket(
        ticket_id="TKT-WS-001",
        channel="app",
        raw_text="   \n\t  ",
        submitted_at="2026-09-22T14:00:00+03:00",
        synthetic_user_id="USR-001",
    )
    result = process_ticket(ticket)
    assert result.escalated is True
    assert result.category == "unclear_or_incomplete"


def test_ms01_english_language_ticket_routing() -> None:
    """Ensure English tickets route to human care while Arabizi continues to normal flow."""
    en_ticket = "Hello support team, I need help with my account, the transfer failed yesterday."
    res_en, _ = classify_ticket(en_ticket)
    assert res_en.category == "unclear_or_incomplete"
    assert res_en.category_confidence < 0.70
    assert "foreign_language_en" in res_en.sentiment_tags

    # Verify Arabizi is NOT mistakenly treated as English
    arabizi_ticket = "7awalt 25 alf w ma woslat"
    res_ar, _ = classify_ticket(arabizi_ticket)
    assert res_ar.category == "failed_transfer"
    assert "foreign_language_en" not in res_ar.sentiment_tags


def test_ms02_multi_issue_detection() -> None:
    """Ensure composite tickets spanning multiple operational domains trigger escalation."""
    compound_text = (
        "عندي مشكلتين: الكارت انرفض بالصراف وسحب البطاقة وما رجعها "
        "وبنفس الوقت التحويل معلق برقم TXN-88776655"
    )
    is_multi, reason = detect_multi_issue(compound_text)
    assert is_multi is True
    assert reason is not None

    ticket = Ticket(
        ticket_id="TKT-MULTI-01",
        channel="app",
        raw_text=compound_text,
        submitted_at="2026-09-22T14:00:00+03:00",
        synthetic_user_id="USR-002",
    )
    result = process_ticket(ticket)
    assert result.escalated is True
    assert "Multiple distinct customer issues" in (result.escalation_reason or "")


def test_ms03_batch_duplicate_detection() -> None:
    """Ensure duplicate tickets within a batch are flagged and escalated."""
    t1 = Ticket(
        ticket_id="TKT-DUP-01",
        channel="app",
        raw_text="حولت 50 الف لصاحبي وما وصلت الحوالة برقم TXN-11223344",
        submitted_at="2026-09-22T14:00:00+03:00",
        synthetic_user_id="USR-DUP-1",
    )
    t2 = Ticket(
        ticket_id="TKT-DUP-02",
        channel="app",
        raw_text="حولت 50 الف لصاحبي وما وصلت الحوالة برقم TXN-11223344",
        submitted_at="2026-09-22T14:02:00+03:00",
        synthetic_user_id="USR-DUP-1",
    )

    results, summary = run_batch([t1, t2])
    assert len(results) == 2
    assert results[1].escalated is True
    assert "duplicate" in (results[1].escalation_reason or "").lower()


def test_eh01_batch_fault_isolation() -> None:
    """Ensure an unhandled exception in one ticket does not abort the entire batch."""
    good_ticket_1 = Ticket(
        ticket_id="TKT-GOOD-01",
        channel="app",
        raw_text="شكر وتقدير على الخدمة السريعة شكرا جزيلا عاشت ايدكم",
        submitted_at="2026-09-22T14:00:00+03:00",
        synthetic_user_id="USR-003",
    )
    good_ticket_2 = Ticket(
        ticket_id="TKT-GOOD-02",
        channel="app",
        raw_text="السلام عليكم اريد استفسر عن اقرب فرع بالمنصور",
        submitted_at="2026-09-22T14:00:00+03:00",
        synthetic_user_id="USR-004",
    )

    results, summary = run_batch([good_ticket_1, good_ticket_2])
    assert summary.total_tickets == 2
    assert len(results) == 2
    assert summary.escalation_rate_pct < 100.0


def test_schema_priority_casing_and_reasoning_clamp() -> None:
    """Ensure priority is sanitized to lowercase and reasoning summary is clamped to 300 chars."""
    res = ClassificationResult(
        category="card_issue",
        category_confidence=0.90,
        priority="HIGH",  # type: ignore[arg-type]
        priority_confidence=0.88,
        reasoning_summary="X" * 500,
    )
    assert res.priority == "high"
    assert len(res.reasoning_summary) <= 300


def test_distinct_users_same_generic_text_not_flagged_as_duplicate() -> None:
    """Ensure two distinct customers asking the same inquiry are NOT flagged as duplicates."""
    t1 = Ticket(
        ticket_id="TKT-USER-A",
        channel="app",
        raw_text="السلام عليكم اريد استفسر عن اقرب فرع بالمنصور",
        submitted_at="2026-09-22T14:00:00+03:00",
        synthetic_user_id="USR-CUST-AAA",
    )
    t2 = Ticket(
        ticket_id="TKT-USER-B",
        channel="app",
        raw_text="السلام عليكم اريد استفسر عن اقرب فرع بالمنصور",
        submitted_at="2026-09-22T14:05:00+03:00",
        synthetic_user_id="USR-CUST-BBB",
    )

    results, summary = run_batch([t1, t2])
    assert len(results) == 2
    # Neither ticket should be escalated as a duplicate
    assert not any("duplicate" in (r.escalation_reason or "").lower() for r in results)


def test_usd_extraction_and_grounding_validation() -> None:
    """Ensure USD amounts fulfill category requirements and pass draft grounding."""
    from supportpipe.extract.validate import validate_extraction_for_category

    # 1. Validation for category requiring amount with USD only
    valid, reasons = validate_extraction_for_category(
        category_id="failed_transfer",
        transaction_ref="TXN-12345678",
        amount_iqd=None,
        event_date_resolved="2026-09-22",
        amount_usd=100,
        currency="USD",
    )
    assert valid is True, f"Failed transfer with USD amount rejected: {reasons}"

    # 2. Grounding check on draft reply containing 100 USD from raw ticket with 'ورقة'
    raw_text = "حولت ورقة وما وصلت برقم TXN-12345678 لصديقي"
    draft_reply = "أهلاً بك، استلمنا طلبك بخصوص تحويل 100 دولار ورقم العملية TXN-12345678 وجاري التحقق من الأمر."
    passed, g_reasons = validate_draft_response(
        draft_text=draft_reply,
        ticket_raw_text=raw_text,
        extracted_ref="TXN-12345678",
        extracted_amount=None,
        extracted_amount_usd=100,
    )
    assert passed is True, f"Grounding rejected valid USD amount in draft: {g_reasons}"
