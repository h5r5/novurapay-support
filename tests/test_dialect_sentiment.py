"""Tests for deep Iraqi dialect sentiment, urgency, phone extraction, and nuance recognition."""


from supportpipe.classify.sentiment import analyze_iraqi_sentiment_and_intent
from supportpipe.extract.extract import extract_entities_offline
from supportpipe.extract.normalize import mask_phone_number, normalize_phone_number
from supportpipe.pipeline import process_ticket
from supportpipe.schemas import Ticket


def test_pure_gratitude_vs_polite_urgency() -> None:
    """Verify system distinguishes pure praise from polite urgency and courtesy with complaints."""
    # Case 1: Pure praise
    t1 = analyze_iraqi_sentiment_and_intent("شكرا حليتوا المشكله بسرعه وعاشت ايدكم يا ابطال")
    assert t1.is_pure_gratitude is True
    assert t1.is_urgent is False
    assert t1.urgency_level == "low"
    assert t1.suggested_priority == "low"

    # Case 2: Polite urgency ("شكرا بس ممكن تستعجلون؟")
    t2 = analyze_iraqi_sentiment_and_intent("شكرا بس ممكن تستعجلون بحل المشكلة فدوة؟")
    assert t2.is_pure_gratitude is False
    assert t2.is_polite_urgency is True
    assert t2.is_urgent is True
    assert t2.urgency_level in ["high", "critical"]
    assert t2.suggested_priority == "high"

    # Case 3: Courtesy followed by technical complaint
    t3 = analyze_iraqi_sentiment_and_intent("عاشت ايدكم بس الحوالة ما وصلت لاخوي وخصموا الرصيد")
    assert t3.is_pure_gratitude is False
    assert "courtesy_opening" in t3.sentiment_tags


def test_anger_and_profanity_elevation() -> None:
    """Verify anger, insults, and extreme frustration elevate priority to HIGH and set sentiment tags."""
    ticket_text = "انعل ابوكم يابو الخلفكم كلش ضايج اوت البارحه انبكت عشرتالاف دينار !!"
    analysis = analyze_iraqi_sentiment_and_intent(ticket_text)

    assert analysis.is_angry is True
    assert analysis.is_hostile_vulgar is True
    assert analysis.is_theft_scam is True
    assert analysis.suggested_priority == "high"

    # Pipeline execution check
    ticket = Ticket(
        ticket_id="TKT-ANGER-01",
        channel="app",
        synthetic_user_id="USR-ANGER-01",
        submitted_at="2026-09-22T10:00:00+03:00",
        raw_text=ticket_text,
    )
    res = process_ticket(ticket, provider_override="mock")
    assert res.category == "fraud_report"
    assert res.priority == "high"
    assert res.team == "Security/Fraud"
    assert "hostile_vulgar" in res.sentiment_tags


def test_emergency_hospital_urgency() -> None:
    """Verify life-critical and emergency contexts trigger critical urgency and HIGH priority."""
    ticket_text = "فدوه هسة هسة واكف بالمستشفى وعملية جراحية ومحتاج ادفع الفلوس ومعلكة الحوالة"
    analysis = analyze_iraqi_sentiment_and_intent(ticket_text)

    assert analysis.is_urgent is True
    assert analysis.urgency_level == "critical"
    assert analysis.suggested_priority == "high"

    ticket = Ticket(
        ticket_id="TKT-EMERGENCY-01",
        channel="app",
        synthetic_user_id="USR-EMERG-01",
        submitted_at="2026-09-22T10:00:00+03:00",
        raw_text=ticket_text,
    )
    res = process_ticket(ticket, provider_override="mock")
    assert res.priority == "high"
    assert res.urgency_level in ["high", "critical"]
    assert "urgent_emergency" in res.sentiment_tags


def test_phone_number_extraction_iraqi_and_intl() -> None:
    """Verify phone normalization for Iraqi standard, spaced, dashed, and foreign international numbers."""
    # 1. Iraqi standard
    p1, intl1 = normalize_phone_number("07801234567")
    assert p1 == "07801234567"
    assert intl1 is False

    # 2. Iraqi dashed
    p2, intl2 = normalize_phone_number("0770-987-6543")
    assert p2 == "07709876543"
    assert intl2 is False

    # 3. Iraqi international prefix (+964)
    p3, intl3 = normalize_phone_number("+9647501234567")
    assert p3 == "07501234567"
    assert intl3 is False

    # 4. Foreign international (UAE +971)
    p4, intl4 = normalize_phone_number("+971501234567")
    assert p4 == "+971501234567"
    assert intl4 is True

    # 5. Foreign international (0090 Turkey)
    p5, intl5 = normalize_phone_number("00905321234567")
    assert p5 == "+905321234567"
    assert intl5 is True


def test_phone_masking_privacy() -> None:
    """Verify PII masking conceals central digits of both Iraqi and international numbers."""
    assert mask_phone_number("07801234567") == "0780****567"
    assert mask_phone_number("+971501234567") == "+971****567"
    assert mask_phone_number(None) is None


def test_entity_extraction_prevents_phone_ref_collision() -> None:
    """Verify extracting a phone number does not mistakenly classify it as a transaction reference."""
    raw = "غلطت برقم المحفظة وحولت 50 الف للرقم 07801234567 بدال اخوي وما اعرف شلون ارجعها"
    ext = extract_entities_offline(raw, "2026-09-22T10:00:00Z", "wrong_recipient")

    assert ext.phone_number == "07801234567"
    assert ext.is_international_phone is False
    assert ext.amount_iqd == 50_000
    assert ext.transaction_ref is None  # Phone must NOT collide with ref
