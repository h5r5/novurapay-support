"""Deterministic escalation logic based on confidences, required fields, and ambiguity."""

from supportpipe.config import settings
from supportpipe.taxonomy.loader import taxonomy


def should_escalate(
    category: str,
    category_confidence: float,
    priority: str,
    priority_confidence: float,
    extraction_valid: bool,
    extraction_reasons: list[str],
    draft_safety_passed: bool = True,
    draft_safety_reasons: list[str] | None = None,
    is_multi_issue: bool = False,
    is_duplicate: bool = False,
    category_threshold: float | None = None,
    priority_threshold: float | None = None,
) -> tuple[bool, str | None]:
    """Pure function determining whether a ticket must be escalated to a human agent.

    Checks in order:
    1. Category invalid or 'unclear_or_incomplete'.
    2. Category or priority confidence below threshold.
    3. Extraction validation failure (e.g. required field missing).
    4. Flagged as multi-issue or duplicate.
    5. Draft content safety / grounding check failed.

    Returns:
        (must_escalate: bool, human_readable_note: str | None)
    """
    cat_thresh = (
        category_threshold
        if category_threshold is not None
        else settings.category_confidence_threshold
    )
    prio_thresh = (
        priority_threshold
        if priority_threshold is not None
        else settings.priority_confidence_threshold
    )

    escalation_notes: list[str] = []

    # 1. Invalid or explicit catch-all category
    valid_categories = taxonomy.get_valid_category_ids()
    if category not in valid_categories:
        escalation_notes.append(f"Unrecognized category '{category}' outside closed taxonomy")
    elif category == "unclear_or_incomplete":
        escalation_notes.append(
            "Ticket is ambiguous, vague, or incomplete; manual agent triage required"
        )

    # 2. Confidence thresholds
    if category_confidence < cat_thresh:
        escalation_notes.append(
            f"Low category confidence ({category_confidence:.2f} < threshold {cat_thresh:.2f})"
        )
    if priority_confidence < prio_thresh:
        escalation_notes.append(
            f"Low priority confidence ({priority_confidence:.2f} < threshold {prio_thresh:.2f})"
        )

    # 3. Extraction business rules
    if not extraction_valid:
        for reason in extraction_reasons:
            escalation_notes.append(f"Extraction incomplete: {reason}")

    # 4. Multi-issue or duplicate heuristic
    if is_multi_issue:
        escalation_notes.append("Multiple distinct customer issues detected in single ticket")
    if is_duplicate:
        escalation_notes.append("Probable duplicate ticket detected within short time window")

    # 5. Draft safety / Grounding gate
    if not draft_safety_passed and draft_safety_reasons:
        for reason in draft_safety_reasons:
            escalation_notes.append(f"Draft validation warning: {reason}")

    if escalation_notes:
        return True, " | ".join(escalation_notes)

    return False, None
