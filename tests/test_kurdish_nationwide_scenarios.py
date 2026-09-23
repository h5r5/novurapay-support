"""Comprehensive test suite for Kurdish language support (Sorani & Kurmanji).

Covers:
- Sorani Kurdish failed transfers and wrong recipient phone disambiguation.
- Kurdish bazaar dollar slang (Gala = $100, Defter = $10,000).
- Kurmanji Kurdish (Latin Hawar script) processing and validation bypass.
- Kurdish sentiment, theft detection, and emergency tagging.
- Kurdish relative date resolution and verbal IQD/USD amounts.
- Kurdish multi-issue composite ticket detection and escalation.
- Kurdish draft response generation with templates_ku.yaml.
"""

from datetime import datetime, timezone
import pytest

from supportpipe.classify.sentiment import analyze_iraqi_sentiment_and_intent
from supportpipe.draft.draft import DraftManager
from supportpipe.draft.validate import check_arabic_script_ratio, validate_draft_response
from supportpipe.extract.extract import extract_entities_offline
from supportpipe.extract.language import detect_ticket_language
from supportpipe.extract.normalize import (
    parse_currency_amount,
    parse_iqd_amount,
    resolve_event_date,
)
from supportpipe.pipeline import process_ticket
from supportpipe.routing.multi_issue import detect_multi_issue
from supportpipe.schemas import Ticket


def test_kurdish_language_detection():
    """Verify distinct detection of Sorani (Arabic script) and Kurmanji (Latin Hawar)."""
    # Sorani
    sorani_sample = "سڵاو، پێنج گەڵا حەواڵە کرد بۆ ژمارەی برام بەڵام نەگەیشت"
    assert detect_ticket_language(sorani_sample) == "ku_ckb"

    # Kurmanji
    kurmanji_sample = "Silav, min sed dolar şand ji bo hevalê xwe lê pere neçû"
    assert detect_ticket_language(kurmanji_sample) == "ku_kmr"

    # Arabic
    arabic_sample = "السلام عليكم، حولت ورقة ونص لحساب اخوية وما وصلت"
    assert detect_ticket_language(arabic_sample) == "ar"

    # English
    english_sample = "Hello, I made a transfer of 100 dollars and it failed"
    assert detect_ticket_language(english_sample) == "en"


def test_kurdish_bazaar_dollar_slang_and_verbal_amounts():
    """Verify Gala ($100) and Kurdish Defter ($10,000) extraction."""
    # 1 Gala = $100
    iqd, usd, curr = parse_currency_amount("گەڵا")
    assert usd == 100
    assert curr == "USD"
    assert iqd == 150_000

    # 1.5 Gala = $150
    iqd, usd, curr = parse_currency_amount("گەڵا و نیو")
    assert usd == 150
    assert curr == "USD"
    assert iqd == 225_000

    # 5 Gala = $500
    iqd, usd, curr = parse_currency_amount("پێنج گەڵا")
    assert usd == 500
    assert curr == "USD"
    assert iqd == 750_000

    # 10 Gala = $1,000
    iqd, usd, curr = parse_currency_amount("دە گەڵا")
    assert usd == 1000
    assert curr == "USD"
    assert iqd == 1_500_000

    # Kurdish Defter = $10,000 (unlike Baghdad Arabic Daftar which is $100,000)
    iqd, usd, curr = parse_currency_amount("دەفتەرێک")
    assert usd == 10_000
    assert curr == "USD"
    assert iqd == 15_000_000

    iqd, usd, curr = parse_currency_amount("دەفتەر")
    assert usd == 10_000
    assert curr == "USD"
    assert iqd == 15_000_000

    iqd, usd, curr = parse_currency_amount("دوو دەفتەر")
    assert usd == 20_000
    assert curr == "USD"
    assert iqd == 30_000_000

    # Kurdish verbal IQD amounts
    assert parse_iqd_amount("بیست و پێنج هەزار") == 25_000
    assert parse_iqd_amount("پەنجا هەزار") == 50_000
    assert parse_iqd_amount("سەد هەزار") == 100_000
    assert parse_iqd_amount("ملیۆن و نیو") == 1_500_000
    assert parse_iqd_amount("دوو ملیۆن") == 2_000_000

    # Kurmanji verbal amounts
    _, usd, curr = parse_currency_amount("sed dolar")
    assert usd == 100
    assert curr == "USD"
    assert parse_iqd_amount("bîst û pênc hezar") == 25_000


def test_kurdish_relative_date_resolution():
    """Verify Kurdish relative date phrases resolve correctly."""
    ref_time = "2026-09-22T12:00:00+03:00"  # Tuesday

    # Today
    assert resolve_event_date("ئەمڕۆ بەیانی", ref_time) == "2026-09-22"
    assert resolve_event_date("îro", ref_time) == "2026-09-22"

    # Yesterday
    assert resolve_event_date("دوێنێ", ref_time) == "2026-09-21"
    assert resolve_event_date("duh", ref_time) == "2026-09-21"

    # Day before yesterday
    assert resolve_event_date("پێری", ref_time) == "2026-09-20"
    assert resolve_event_date("pêr", ref_time) == "2026-09-20"

    # Dynamic days ago
    assert resolve_event_date("پێش 4 ڕۆژ", ref_time) == "2026-09-18"
    assert resolve_event_date("berî 5 rojan", ref_time) == "2026-09-17"


def test_kurdish_sorani_end_to_end_pipeline():
    """End-to-end test of Sorani transfer failure with Kurdish draft reply."""
    raw_text = (
        "سڵاو ڕێز، پێنج گەڵا حەواڵە کرد بۆ ژمارەی 07501234567 "
        "بەڵام نەگەیشتووە و پارەکە لە باڵانسم بڕدرا. ژمارەی حەواڵە TXN-778899 تکایە چارەسەری بکەن"
    )
    ticket = Ticket(
        ticket_id="TKT-KU-SORANI-01",
        raw_text=raw_text,
        submitted_at="2026-09-22T10:00:00+03:00",
        synthetic_user_id="USR-ERBIL-01",
    )

    result = process_ticket(ticket)

    # 1. Classification & Language
    assert result.category == "failed_transfer"
    assert detect_ticket_language(ticket.raw_text) == "ku_ckb"

    # 2. Entity extraction
    assert result.extracted_fields.amount_usd == 500
    assert result.extracted_fields.amount_iqd == 750_000
    assert result.extracted_fields.phone_number == "07501234567"
    assert result.extracted_fields.transaction_ref == "TXN-778899"

    # 3. Escalation check
    assert not result.escalated, f"Unexpected escalation: {result.escalation_reason}"

    # 4. Draft response in Sorani Kurdish
    assert result.draft_reply is not None
    # Kurdish greetings and words
    assert any(w in result.draft_reply for w in ["بەڕێز", "سڵاو", "خزمەتگوزاری"])
    # Grounded with extracted reference and phone
    assert "TXN-778899" in result.draft_reply
    assert "07501234567" in result.draft_reply


def test_kurdish_phone_disambiguation_wrong_recipient():
    """Verify sender phone is deprioritized over recipient phone in Kurdish wrong transfer."""
    raw_text = (
        "بە هەڵە پارەم نارد لە ژمارەی من 07709998877 بۆ ژمارەی هەڵە 07503332211 "
        "بڕی دەفتەرێک کۆدی حەواڵە REF-991122 تکایە بیگەڕێننەوە"
    )
    ticket = Ticket(
        ticket_id="TKT-KU-WRONG-01",
        raw_text=raw_text,
        submitted_at="2026-09-22T11:00:00+03:00",
        synthetic_user_id="USR-SULI-01",
    )

    result = process_ticket(ticket)

    assert result.category == "wrong_recipient"
    assert detect_ticket_language(ticket.raw_text) == "ku_ckb"
    assert result.extracted_fields.phone_number == "07503332211"
    assert result.extracted_fields.amount_usd == 10_000
    assert result.extracted_fields.transaction_ref == "REF-991122"


def test_kurdish_kurmanji_latin_script_pipeline():
    """Verify Kurmanji Latin Hawar script is processed cleanly without script gate rejection."""
    raw_text = (
        "Silav, koda hewaleyê TXN-445566 e, min sed dolar şand ji bo hejmara 07508889900 lê heta niha neçûye"
    )
    ticket = Ticket(
        ticket_id="TKT-KU-KMR-01",
        raw_text=raw_text,
        submitted_at="2026-09-22T12:00:00+03:00",
        synthetic_user_id="USR-DUHOK-01",
    )

    result = process_ticket(ticket)

    assert detect_ticket_language(ticket.raw_text) == "ku_kmr"
    assert result.extracted_fields.transaction_ref == "TXN-445566"
    assert result.extracted_fields.amount_usd == 100
    assert result.extracted_fields.phone_number == "07508889900"


def test_kurdish_sentiment_theft_and_emergency():
    """Verify Kurdish theft and hospital emergency keywords trigger high urgency and escalation flags."""
    # Theft/fraud in Kurdish
    theft_text = "ئاگاداربن پارەکەم دزراوە و هەژمارەکەم هاککراوە خێرا ڕایبگرن"
    sentiment = analyze_iraqi_sentiment_and_intent(theft_text)
    assert sentiment.is_theft_scam is True
    assert sentiment.urgency_level == "critical"
    assert sentiment.suggested_priority == "high"

    # Kurmanji theft
    kmr_theft = "Hesabê min hate dizîn û pere winda bûne"
    sentiment_kmr = analyze_iraqi_sentiment_and_intent(kmr_theft)
    assert sentiment_kmr.is_theft_scam is True

    # Emergency in Kurdish
    emergency_text = "بەپەلە یارمەتیم بدەن لە نەخۆشخانەم و پێویستم بە پارەکەیە"
    sentiment_emg = analyze_iraqi_sentiment_and_intent(emergency_text)
    assert sentiment_emg.is_urgent is True
    assert sentiment_emg.urgency_level == "critical"

    # Gratitude in Kurdish
    gratitude_text = "دەستان خۆش بێت سوپاس"
    sentiment_grat = analyze_iraqi_sentiment_and_intent(gratitude_text)
    assert sentiment_grat.is_pure_gratitude is True
    assert sentiment_grat.urgency_level == "low"
    assert "pure_gratitude" in sentiment_grat.sentiment_tags


def test_kurdish_multi_issue_detection():
    """Verify Kurdish multi-issue compound requests trigger multi-issue detection and escalation."""
    multi_text = (
        "سڵاو حەواڵەکەم نەگەیشتووە و پارەم لێ بڕدراوە، "
        "لە هەمان کاتدا کارتەکەم ماستەرکارد لە ئەپ کار ناکات و ڕاگیراوە"
    )
    is_multi, reason = detect_multi_issue(multi_text)
    assert is_multi is True
    assert reason is not None
    assert "لە هەمان کاتدا" in reason or "connective" in reason.lower() or "disjoint" in reason.lower()
