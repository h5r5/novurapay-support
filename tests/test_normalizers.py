"""Unit tests for Iraqi date resolution and IQD amount normalizers."""

from supportpipe.extract.normalize import (
    normalize_digits,
    parse_iqd_amount,
    resolve_event_date,
)
from supportpipe.extract.validate import (
    is_valid_transaction_ref,
    validate_extraction_for_category,
)


def test_normalize_digits() -> None:
    """Verify conversion of Eastern Arabic numerals to Western digits."""
    assert normalize_digits("١٢٣٤٥٦٧٨٩٠") == "1234567890"
    assert normalize_digits("الرصيد ٥٠٠٠ دينار") == "الرصيد 5000 دينار"


def test_parse_iqd_amount_formats() -> None:
    """Verify various ways amounts are written in Iraqi Arabic."""
    # Standard numbers and formatting
    assert parse_iqd_amount(50000) == 50000
    assert parse_iqd_amount("50,000") == 50000
    assert parse_iqd_amount("25000 دينار") == 25000
    assert parse_iqd_amount("٥٠٠٠٠ دينار") == 50000

    # Dialect text phrases
    assert parse_iqd_amount("نص مليون") == 500000
    assert parse_iqd_amount("ربع مليون") == 250000
    assert parse_iqd_amount("مليون") == 1000000
    assert parse_iqd_amount("100 الف") == 100000
    assert parse_iqd_amount("75 ألف") == 75000

    # Plural and English notation (الاف, آلاف, k, m)
    assert parse_iqd_amount("10 الاف") == 10000
    assert parse_iqd_amount("5 آلاف دينار") == 5000
    assert parse_iqd_amount("50k") == 50000
    assert parse_iqd_amount("1.5m") == 1500000

    # Invalid / out of bounds
    assert parse_iqd_amount("مبلغ غير معروف") is None
    assert parse_iqd_amount(100) is None  # below 500 IQD min
    assert parse_iqd_amount(200_000_000) is None  # above 100m IQD max


def test_arabizi_and_slang_normalization() -> None:
    """Verify Arabized English, transliteration, and Iraqi chat slang normalization."""
    from supportpipe.extract.normalize import normalize_arabizi_and_slang

    # Politeness & gratitude
    res1 = normalize_arabizi_and_slang("ثانكيو برو تسلم اوك تمام")
    assert "شكرا" in res1
    assert "اخي" in res1
    assert "حسنا" in res1

    # Fintech terms with Arabic prefixes
    res2 = normalize_arabizi_and_slang("عندي مشكلة بالترانسفير وكراش بالاب")
    assert "تحويل" in res2
    assert "عطل مفاجئ" in res2

    # Account block slang
    res3 = normalize_arabizi_and_slang("محفظتي انطوها بلوك وباند وما اكدر ادخل")
    assert "حظر" in res3


def test_resolve_relative_dates() -> None:
    """Verify date resolution against Asia/Baghdad ticket timestamp."""
    # Base timestamp: Tuesday 2026-09-22
    submitted_at = "2026-09-22T14:30:00+03:00"

    # Today
    assert resolve_event_date("اليوم الصبح", submitted_at) == "2026-09-22"

    # Yesterday
    assert resolve_event_date("امس بالليل", submitted_at) == "2026-09-21"
    assert resolve_event_date("البارحة", submitted_at) == "2026-09-21"

    # Two days ago
    assert resolve_event_date("قبل يومين", submitted_at) == "2026-09-20"

    # Dynamic N days ago
    assert resolve_event_date("قبل 5 ايام", submitted_at) == "2026-09-17"

    # One week ago
    assert resolve_event_date("قبل اسبوع", submitted_at) == "2026-09-15"

    # Specific weekday: Friday before Tuesday Sep 22 is Sep 18
    assert resolve_event_date("يوم الجمعة الفاتت", submitted_at) == "2026-09-18"

    # Explicit ISO date
    assert resolve_event_date("2026-09-10", submitted_at) == "2026-09-10"


def test_transaction_ref_validation() -> None:
    """Verify transaction reference pattern checks."""
    assert is_valid_transaction_ref("TXN-10293847") is True
    assert is_valid_transaction_ref("NOVURA_982173") is True
    assert is_valid_transaction_ref("9812746198") is True
    assert is_valid_transaction_ref("") is False
    assert is_valid_transaction_ref("   ") is False
    assert is_valid_transaction_ref("AB") is False  # too short


def test_category_extraction_rules() -> None:
    """Verify extraction validation enforces category-specific required fields."""
    # failed_transfer requires ref and amount
    valid, reasons = validate_extraction_for_category(
        "failed_transfer",
        transaction_ref=None,
        amount_iqd=50000,
        event_date_resolved="2026-09-21",
    )
    assert valid is False
    assert any("transaction reference required" in r for r in reasons)

    # Valid failed_transfer
    valid, reasons = validate_extraction_for_category(
        "failed_transfer",
        transaction_ref="TXN-998877",
        amount_iqd=50000,
        event_date_resolved="2026-09-21",
    )
    assert valid is True
    assert len(reasons) == 0

    # login_problem does not require ref or amount
    valid, reasons = validate_extraction_for_category(
        "login_problem",
        transaction_ref=None,
        amount_iqd=None,
        event_date_resolved=None,
    )
    assert valid is True
    assert len(reasons) == 0


def test_resolve_mesopotamian_month_dates() -> None:
    """Verify Mesopotamian (Iraqi) calendar month parsing and extraction."""
    from supportpipe.extract.extract import extract_entities_offline

    submitted_at = "2026-09-22T14:30:00+03:00"

    # Explicit day + month + year
    assert resolve_event_date("15 نيسان 2026", submitted_at) == "2026-04-15"
    assert resolve_event_date("بتاريخ 20 تشرين الأول 2025", submitted_at) == "2025-10-20"
    assert resolve_event_date("يوم 5 كانون الثاني 2026", submitted_at) == "2026-01-05"
    assert resolve_event_date("10 شباط 2026", submitted_at) == "2026-02-10"
    assert resolve_event_date("1 اذار 2026", submitted_at) == "2026-03-01"
    assert resolve_event_date("25 ايار 2026", submitted_at) == "2026-05-25"
    assert resolve_event_date("30 حزيران 2026", submitted_at) == "2026-06-30"
    assert resolve_event_date("7 تموز 2026", submitted_at) == "2026-07-07"
    assert resolve_event_date("14 اب 2026", submitted_at) == "2026-08-14"
    assert resolve_event_date("2 أيلول 2026", submitted_at) == "2026-09-02"

    # Month without explicit year: past month relative to Sep 2026 stays 2026
    assert resolve_event_date("15 نيسان", submitted_at) == "2026-04-15"
    # Month without explicit year: future month relative to Sep 2026 (e.g. Nov) rolls back to 2025
    assert resolve_event_date("10 تشرين الثاني", submitted_at) == "2025-11-10"

    # End-to-end extraction from ticket text
    ticket = "السلام عليكم، حولت 75 الف يوم 15 نيسان 2026 وما وصلت للمستلم ورقم الحوالة TXN-12345678"
    extracted = extract_entities_offline(ticket, submitted_at, "failed_transfer")
    assert extracted.event_date_resolved == "2026-04-15"
    assert extracted.amount_iqd == 75000
    assert extracted.transaction_ref == "TXN-12345678"
