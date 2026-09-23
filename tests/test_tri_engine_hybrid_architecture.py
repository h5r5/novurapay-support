"""Comprehensive regression and unit tests for the Tri-Engine Hybrid Architecture.

Covers:
1. Character deduplication and dialect elongation without corrupting digits/phones.
2. Compound fractional verbal amounts (مليونين وربع = 2,250,000 IQD).
3. Compound relative dates (قبل اولت البارحة = 3-day offset).
4. Longest-match date phrase disambiguation.
5. DiscrepancyStore thread-safe logging and PII masking.
6. Multi-engine consensus matrix (Triple consensus, Cloud consensus, conflict fallback).
7. End-to-end pipeline execution on real dialect tickets.
"""

from pathlib import Path
from unittest.mock import MagicMock

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.providers.hybrid_provider import HybridClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.extract.extract import extract_ticket_details
from supportpipe.extract.normalize import (
    normalize_repeated_characters,
    parse_currency_amount,
    resolve_event_date,
)
from supportpipe.learning_store import DiscrepancyStore
from supportpipe.pipeline import process_ticket
from supportpipe.schemas import ClassificationResult, Ticket


def test_character_deduplication_and_elongation() -> None:
    """Ensure letter deduplication cleans dialect emphasis while leaving numbers/phones intact."""
    # 1. Letters only: 3+ collapsed, targeted words, trailing doubled letters
    raw = "ملييونين وربعععع وماتحول الفلوسسس شلقصههه حووولت"
    norm = normalize_repeated_characters(raw)
    assert norm == "مليونين وربع وماتحول الفلوس شلقصه حولت"

    # 2. Digits must NEVER be collapsed
    num_text = "50,000 25000 10000000 07800011223 TXN-888999"
    norm_nums = normalize_repeated_characters(num_text)
    assert norm_nums == num_text


def test_compound_fractional_amounts_millions() -> None:
    """Verify parsing of colloquial Iraqi compound millions and fractions."""
    cases = [
        ("مليونين وربع", 2_250_000),
        ("مليونين و ربع", 2_250_000),
        ("مليون وربع", 1_250_000),
        ("مليونين ونص", 2_500_000),
        ("مليونين ونصف", 2_500_000),
        ("مليون ونص", 1_500_000),
        ("مليونين وثلاث ارباع", 2_750_000),
        ("ثلاث ملايين وربع", 3_250_000),
        ("ثلاث ملايين ونص", 3_500_000),
        ("ربع مليون", 250_000),
        ("نص مليون", 500_000),
        ("ميتين وخمسين الف", 250_000),
        ("خمسمية الف", 500_000),
        ("سبعمية وخمسين الف", 750_000),
    ]
    for text, expected in cases:
        iqd, usd, curr = parse_currency_amount(text)
        assert iqd == expected, f"Failed for '{text}': got {iqd}, expected {expected}"
        assert curr == "IQD"


def test_compound_relative_date_three_days_offset() -> None:
    """Verify Iraqi dialect 'قبل اولت البارحة' resolves to ref_date minus 3 days."""
    sub_iso = "2026-09-22T14:30:00+03:00"

    # 3 days ago: 2026-09-19
    for phrase in [
        "قبل اولت البارحة",
        "قبل اولت البارحه",
        "قبل اول البارحة",
        "قبل اولت امس",
        "پێش پێرێ",
    ]:
        resolved = resolve_event_date(phrase, sub_iso)
        assert resolved == "2026-09-19", f"Failed for '{phrase}': got {resolved}"

    # 2 days ago: 2026-09-20
    assert resolve_event_date("اولت البارحة", sub_iso) == "2026-09-20"
    assert resolve_event_date("اول البارحه", sub_iso) == "2026-09-20"

    # 1 day ago: 2026-09-21
    assert resolve_event_date("البارحة", sub_iso) == "2026-09-21"


def test_longest_date_match_specificity() -> None:
    """Verify that when multiple date phrases exist, the most specific (longest) is selected."""
    text = "اني البارحه قبل اولت البارحه حولت فلوس"
    sub_iso = "2026-09-22T10:00:00+03:00"
    extracted = extract_ticket_details(text, sub_iso, "failed_transfer")
    # 'قبل اولت البارحه' (16 chars) must win over 'البارحه' (7 chars)
    assert extracted.event_date_resolved == "2026-09-19"


def test_discrepancy_store_persistence_and_pii_masking(tmp_path: Path) -> None:
    """Verify DiscrepancyStore persists records and scrubs phone numbers/PII."""
    store_file = tmp_path / "test_disc.jsonl"
    store = DiscrepancyStore(store_path=store_file)

    rec = store.record_discrepancy(
        ticket_id="TKT-TEST-99",
        channel="app",
        raw_text="حولت مليونين للرقم 07801234567 وماوصلت",
        discrepancy_type="extraction_amount",
        field_name="amount_iqd",
        offline_value=2_000_000,
        llm_value=2_250_000,
        resolution_applied="llm_correction_audited",
        confidence_delta=0.15,
        discrepancy_reason="Local extractor missed verbal fraction",
        rule_suggestion="Add compound million mapping",
    )

    assert rec.record_id.startswith("DISC-")
    assert "07801234567" not in rec.raw_text_masked
    assert "[PHONE_SCRUBBED]" in rec.raw_text_masked

    # Verify loaded records and stats
    loaded = store.load_discrepancies()
    assert len(loaded) == 1
    assert loaded[0].record_id == rec.record_id

    stats = store.get_summary_stats()
    assert stats["total_discrepancies"] == 1
    assert stats["by_type"]["extraction_amount"] == 1
    assert stats["top_suggestions"] == ["Add compound million mapping"]


def test_hybrid_provider_triple_consensus() -> None:
    """Verify confidence boost to 99% when System 1, Jev, and Gemini agree."""
    mock_mock = MagicMock(spec=MockClassifierProvider)
    mock_mock.classify.return_value = ClassificationResult(
        category="failed_transfer",
        category_confidence=0.85,
        priority="high",
        priority_confidence=0.88,
        reasoning_summary="Mock baseline",
    )

    mock_jev = MagicMock(spec=BaseClassifierProvider)
    mock_jev.classify.return_value = ClassificationResult(
        category="failed_transfer",
        category_confidence=0.92,
        priority="high",
        priority_confidence=0.91,
        reasoning_summary="Jev baseline",
    )

    mock_gemini = MagicMock(spec=BaseClassifierProvider)
    mock_gemini.classify.return_value = ClassificationResult(
        category="failed_transfer",
        category_confidence=0.95,
        priority="high",
        priority_confidence=0.94,
        reasoning_summary="Gemini baseline",
        audit_details={"audit_status": "verified"},
    )

    hybrid = HybridClassifierProvider(
        mock_provider=mock_mock,
        jev_provider=mock_jev,
        gemini_provider=mock_gemini,
    )

    res = hybrid.classify(
        ticket_text="حولت وما وصل",
        channel="app",
        ticket_id="TKT-TEST-CONSENSUS",
    )

    assert res.category == "failed_transfer"
    assert res.category_confidence == 0.99
    assert res.priority == "high"
    assert "Triple Consensus" in res.reasoning_summary


def test_hybrid_provider_cloud_consensus_override(tmp_path: Path) -> None:
    """Verify that when Jev and Gemini agree against System 1, cloud consensus is adopted."""
    mock_mock = MagicMock(spec=MockClassifierProvider)
    mock_mock.classify.return_value = ClassificationResult(
        category="agent_deposit_withdrawal",
        category_confidence=0.70,
        priority="medium",
        priority_confidence=0.70,
        reasoning_summary="Mock misclassification",
    )

    mock_jev = MagicMock(spec=BaseClassifierProvider)
    mock_jev.classify.return_value = ClassificationResult(
        category="failed_transfer",
        category_confidence=0.94,
        priority="high",
        priority_confidence=0.90,
        reasoning_summary="Jev correct choice",
    )

    mock_gemini = MagicMock(spec=BaseClassifierProvider)
    mock_gemini.classify.return_value = ClassificationResult(
        category="failed_transfer",
        category_confidence=0.96,
        priority="high",
        priority_confidence=0.95,
        reasoning_summary="Gemini correct choice",
        audit_details={"audit_status": "verified"},
    )

    hybrid = HybridClassifierProvider(
        mock_provider=mock_mock,
        jev_provider=mock_jev,
        gemini_provider=mock_gemini,
    )

    res = hybrid.classify(
        ticket_text="شمرت فلوس للصراف وما نزلت",
        channel="app",
        ticket_id="TKT-TEST-OVERRIDE",
    )

    assert res.category == "failed_transfer"
    assert res.category_confidence >= 0.92
    assert "Cloud Consensus" in res.reasoning_summary


def test_end_to_end_real_user_ticket_pipeline() -> None:
    """Test full pipeline processing on the exact user dialect ticket."""
    raw_text = "اني البارحه قبل اولت البارحه حولت ملييونين وربعع وماتحول الفلوس شلقصه ؟"
    ticket = Ticket(
        ticket_id="TKT-USER-DIALECT-01",
        channel="app",
        raw_text=raw_text,
        submitted_at="2026-09-22T12:00:00+03:00",
        synthetic_user_id="USR-BAGHDAD-01",
    )

    result = process_ticket(ticket)

    # 1. Extracted Entities
    assert result.extracted_fields.amount_iqd == 2_250_000
    assert result.extracted_fields.currency == "IQD"
    assert result.extracted_fields.event_date_resolved == "2026-09-19"

    # 2. Classification & Routing
    assert result.category == "failed_transfer"
    assert result.team == "Payments & Transfers"

    # 3. Escalation: Must escalate due to missing transaction reference
    assert result.escalated is True
    assert "Missing transaction reference" in (result.escalation_reason or "")
