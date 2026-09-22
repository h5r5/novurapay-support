"""Unit tests for confidence-based and rule-based escalation logic."""

from supportpipe.routing.escalation import should_escalate


def test_clean_ticket_no_escalation() -> None:
    """Verify clean, high-confidence ticket with valid extraction is not escalated."""
    escalated, reason = should_escalate(
        category="failed_transfer",
        category_confidence=0.95,
        priority="high",
        priority_confidence=0.90,
        extraction_valid=True,
        extraction_reasons=[],
        category_threshold=0.65,
        priority_threshold=0.60,
    )
    assert escalated is False
    assert reason is None


def test_unclear_category_always_escalates() -> None:
    """Verify 'unclear_or_incomplete' category always escalates regardless of confidence."""
    escalated, reason = should_escalate(
        category="unclear_or_incomplete",
        category_confidence=0.99,
        priority="low",
        priority_confidence=0.99,
        extraction_valid=True,
        extraction_reasons=[],
    )
    assert escalated is True
    assert "Ticket is ambiguous" in (reason or "")


def test_low_category_confidence_escalation() -> None:
    """Verify low category confidence triggers escalation with clear explanation."""
    escalated, reason = should_escalate(
        category="login_problem",
        category_confidence=0.45,
        priority="medium",
        priority_confidence=0.85,
        extraction_valid=True,
        extraction_reasons=[],
        category_threshold=0.65,
    )
    assert escalated is True
    assert "Low category confidence (0.45 < threshold 0.65)" in (reason or "")


def test_missing_required_field_escalation() -> None:
    """Verify extraction failure triggers escalation even with 100% classification confidence."""
    escalated, reason = should_escalate(
        category="failed_transfer",
        category_confidence=0.98,
        priority="high",
        priority_confidence=0.95,
        extraction_valid=False,
        extraction_reasons=[
            "Missing transaction reference required for category 'failed_transfer'"
        ],
    )
    assert escalated is True
    assert "Extraction incomplete: Missing transaction reference" in (reason or "")


def test_multi_issue_escalation() -> None:
    """Verify multi-issue ticket flags escalate with note."""
    escalated, reason = should_escalate(
        category="failed_transfer",
        category_confidence=0.90,
        priority="high",
        priority_confidence=0.90,
        extraction_valid=True,
        extraction_reasons=[],
        is_multi_issue=True,
    )
    assert escalated is True
    assert "Multiple distinct customer issues detected" in (reason or "")
