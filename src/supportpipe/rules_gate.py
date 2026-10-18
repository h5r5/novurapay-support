"""Change gate validation for remediation rules under Stress Batch Protocol (Rule b).

Enforces:
(b) add no rule embedding literal phrase from batch; pattern must be supported
    by >= 3 tickets from >= 2 batch-tag clusters.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger("supportpipe.rules_gate")


def extract_ticket_text(ticket_item: dict[str, Any]) -> str:
    """Extract raw customer text from nested or flat ticket dict."""
    if "ticket" in ticket_item and isinstance(ticket_item["ticket"], dict):
        return str(
            ticket_item["ticket"].get("raw_text")
            or ticket_item["ticket"].get("text")
            or ""
        )
    return str(ticket_item.get("raw_text") or ticket_item.get("text") or "")


def extract_cluster_id(ticket_item: dict[str, Any]) -> str:
    """Determine the tag cluster identifier for a ticket.

    Uses (dialect, attack_type) tag tuple, or template_id, or cluster_id.
    """
    tags: dict[str, Any] = {}
    template_id = ""

    if "label" in ticket_item and isinstance(ticket_item["label"], dict):
        lbl = ticket_item["label"]
        tags = lbl.get("tags") or {}
        template_id = str(lbl.get("template_id") or "")
    else:
        tags = ticket_item.get("tags") or {}
        template_id = str(ticket_item.get("template_id") or "")

    dialect = str(tags.get("dialect") or "").strip()
    attack = str(tags.get("attack_type") or "").strip()
    cluster = str(tags.get("cluster_id") or "").strip()

    if cluster:
        return cluster
    if dialect and attack:
        return f"{dialect}:{attack}"
    if dialect:
        return f"dialect:{dialect}"
    if template_id:
        return f"template:{template_id}"
    return "default_cluster"


def validate_rule_candidate(
    pattern: str,
    batch_tickets: list[dict[str, Any]],
    min_support: int = 3,
    min_clusters: int = 2,
) -> tuple[bool, str]:
    """Validate a candidate rule against Change Gate Rule (b).

    Requirements:
    1. Pattern must compile as valid regex or string.
    2. Pattern must match at least `min_support` tickets (default: >= 3).
    3. Matched tickets must span at least `min_clusters` distinct batch-tag clusters (default: >= 2).
    4. Must not be a verbatim literal phrase copied from a single ticket.

    Returns:
        (is_valid, reason_message)
    """
    if not pattern or not pattern.strip():
        return False, "Candidate pattern cannot be empty."

    clean_pattern = pattern.strip()

    try:
        compiled = re.compile(clean_pattern, re.IGNORECASE)
    except re.error as e:
        return False, f"Invalid regex pattern '{clean_pattern}': {e}"

    matched_tickets: list[dict[str, Any]] = []
    matched_clusters: set[str] = set()

    for item in batch_tickets:
        text = extract_ticket_text(item)
        if not text:
            continue
        if compiled.search(text):
            matched_tickets.append(item)
            c_id = extract_cluster_id(item)
            matched_clusters.add(c_id)

    # 1. Support check: >= min_support
    if len(matched_tickets) < min_support:
        return (
            False,
            f"Rule rejected by Gate (b): insufficient ticket support. "
            f"Matched {len(matched_tickets)} tickets (required >= {min_support}).",
        )

    # 2. Cluster diversity check: >= min_clusters
    if len(matched_clusters) < min_clusters:
        return (
            False,
            f"Rule rejected by Gate (b): insufficient cluster diversity. "
            f"Matched {len(matched_clusters)} cluster(s) {matched_clusters} (required >= {min_clusters}).",
        )

    # 3. Verbatim literal extraction check:
    # If the pattern is an un-generalized literal sentence/phrase (> 25 chars or > 4 words without regex operators)
    # that happens to match only trivially identical text, verify it is truly generalized.
    is_plain_literal = not any(c in clean_pattern for c in r".*+?[]{}()^$|\d\w\s")
    if is_plain_literal and len(clean_pattern.split()) >= 4:
        # Check if it was copied verbatim from a single ticket
        occurrences = [
            t for t in batch_tickets if clean_pattern in extract_ticket_text(t)
        ]
        if len(occurrences) < min_support:
            return (
                False,
                "Rule rejected by Gate (b): literal phrase copied from single batch ticket without generalization.",
            )

    return (
        True,
        f"Rule approved: supported by {len(matched_tickets)} tickets across {len(matched_clusters)} clusters ({matched_clusters}).",
    )
