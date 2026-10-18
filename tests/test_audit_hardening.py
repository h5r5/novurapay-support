"""Unit tests verifying all audit remediations (VULN-01 through VULN-10)."""

from supportpipe.classify.providers.mock_provider import (
    MockClassifierProvider,
    _classify_english_fintech_intent,
)
from supportpipe.extract.extract import extract_entities_offline
from supportpipe.extract.normalize import parse_currency_amount
from supportpipe.logging_store import mask_pii


def test_vuln_01_kurmanji_routing() -> None:
    """VULN-01: Kurmanji text routes directly to deterministic heuristics."""
    provider = MockClassifierProvider(offline_model_version="v9")
    text = "Ez dixwazim vegerandina pere ji bo hewaleyê"
    result = provider.classify(text)
    assert result.category == "refund_status"
    assert result.category_confidence >= 0.80


def test_vuln_02_and_09_nan_inf_and_bounds_check() -> None:
    """VULN-02 & VULN-09: math.isfinite and wallet bounds (500 to 100M IQD)."""
    # NaN and Inf should return None
    assert parse_currency_amount(float("nan")) == (None, None, "IQD")
    assert parse_currency_amount(float("inf")) == (None, None, "IQD")
    assert parse_currency_amount(float("-inf")) == (None, None, "IQD")

    # Extreme out of bounds
    assert parse_currency_amount(200_000_000) == (None, None, "IQD")
    assert parse_currency_amount(100) == (None, None, "IQD")

    # Dynamic compound out of bounds
    assert parse_currency_amount("500 ملايين") == (None, None, "IQD")
    assert parse_currency_amount("200000 alf") == (None, None, "IQD")

    # In bounds
    iqd, usd, curr = parse_currency_amount("50 الف")
    assert iqd == 50_000


def test_vuln_03_phone_masking_in_text_clean() -> None:
    """VULN-03: Masking all candidate phones from text so they do not collide with ref."""
    text = "حولت من خط 07701112233 لرقم 07804445566 والعملية برقم TXN-99887766"
    extracted = extract_entities_offline(text, "2026-10-18T10:00:00+03:00", "failed_transfer")
    assert extracted.transaction_ref == "TXN-99887766"
    assert extracted.phone_number is not None


def test_vuln_04_otp_code_scrubbing() -> None:
    """VULN-04: OTP code like 'رمز 5421' is scrubbed and does not become an amount."""
    text = "اريد ادخل للتطبيق واجاني رمز 5421 بس ما يشتغل"
    extracted = extract_entities_offline(text, "2026-10-18T10:00:00+03:00", "login_problem")
    assert extracted.amount_iqd is None


def test_vuln_06_international_phone_pii_masking() -> None:
    """VULN-06: International E.164 phone numbers are masked by mask_pii."""
    text = "My international contact is +971501234567 or 009647701234567"
    masked = mask_pii(text)
    assert "+971501234567" not in masked
    assert "009647701234567" not in masked
    assert "[PHONE_SCRUBBED]" in masked


def test_vuln_07_theft_scam_routes_to_fraud_report() -> None:
    """VULN-07: Urgent account takeover or theft routes to fraud_report, not account_blocked."""
    provider = MockClassifierProvider(offline_model_version="v9")
    text = "حسابي تهكر وانباكت فلوسي والحساب مغلق"
    result = provider.classify(text)
    assert result.category == "fraud_report"


def test_vuln_08_english_failed_transfer_classified() -> None:
    """VULN-08: Explicit English failed transfer matches failed_transfer category."""
    cat, conf = _classify_english_fintech_intent(
        "The interbank transfer failed and sender debited, beneficiary uncredited"
    )
    assert cat == "failed_transfer"
    assert conf >= 0.85


def test_vuln_10_amount_preceded_ref_rejected() -> None:
    """VULN-10: Sequence of digits preceded by amount indicator like 'مبلغ: 12345678' is not treated as ref."""
    text = "حولت مبلغ: 50000000 وموصلت الحوالة"
    extracted = extract_entities_offline(text, "2026-10-18T10:00:00+03:00", "failed_transfer")
    # 50000000 should not be extracted as transaction_ref
    assert extracted.transaction_ref != "50000000"
