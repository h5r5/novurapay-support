"""Core batch pipeline orchestrator for SupportPipe."""

import time
from datetime import UTC, datetime

from supportpipe.classify.classify import classify_ticket
from supportpipe.draft.draft import draft_manager
from supportpipe.extract.extract import extract_ticket_details
from supportpipe.extract.validate import validate_extraction_for_category
from supportpipe.routing.escalation import should_escalate
from supportpipe.routing.route import resolve_team
from supportpipe.schemas import (
    BatchSummary,
    PipelineResult,
    Ticket,
)


def process_ticket(ticket: Ticket, provider_override: str | None = None) -> PipelineResult:
    """Process a single ticket through the complete typed pipeline."""
    start_time = time.perf_counter()

    # 1. Classification
    classification, provider_tag = classify_ticket(
        ticket_text=ticket.raw_text,
        channel=ticket.channel,
        provider_name=provider_override,
    )

    # 2. Structured Extraction & Code Normalization
    extracted = extract_ticket_details(
        ticket_raw_text=ticket.raw_text,
        submitted_at_iso=ticket.submitted_at,
        category=classification.category,
    )

    # 3. Extraction Validation against Business Rules
    ext_valid, ext_reasons = validate_extraction_for_category(
        category_id=classification.category,
        transaction_ref=extracted.transaction_ref,
        amount_iqd=extracted.amount_iqd,
        event_date_resolved=extracted.event_date_resolved,
    )

    # 4. Deterministic Routing (Rule 3)
    team = resolve_team(classification.category)

    # 5. Deterministic Escalation Evaluation
    escalated, escalation_reason = should_escalate(
        category=classification.category,
        category_confidence=classification.category_confidence,
        priority=classification.priority,
        priority_confidence=classification.priority_confidence,
        extraction_valid=ext_valid,
        extraction_reasons=ext_reasons,
    )

    # 6. Response Drafting (Only for non-escalated tickets; human approves before send)
    draft_reply: str | None = None
    if not escalated:
        draft_reply, _, _, draft_source = draft_manager.generate_draft(
            ticket_raw_text=ticket.raw_text,
            category=classification.category,
            priority=classification.priority,
            extracted=extracted,
        )
    else:
        draft_reply = f"[تذكرة مصعدة للمراجعة اليدوية]: {escalation_reason}"
        draft_source = "escalation_notice"

    total_latency_ms = (time.perf_counter() - start_time) * 1000.0

    urgency = "normal"
    if (
        "urgent_emergency" in classification.sentiment_tags
        or "theft_scam" in classification.sentiment_tags
        or "hostile_vulgar" in classification.sentiment_tags
    ):
        urgency = "critical"
    elif (
        "polite_urgency" in classification.sentiment_tags
        or "angry" in classification.sentiment_tags
        or classification.priority == "high"
    ):
        urgency = "high"
    elif "pure_gratitude" in classification.sentiment_tags:
        urgency = "low"

    return PipelineResult(
        ticket_id=ticket.ticket_id,
        category=classification.category,
        category_confidence=classification.category_confidence,
        priority=classification.priority,
        priority_confidence=classification.priority_confidence,
        extracted_fields=extracted,
        team=team,
        escalated=escalated,
        escalation_reason=escalation_reason,
        draft_reply=draft_reply,
        provider_path=f"{provider_tag}+{draft_source}",
        reasoning_summary=classification.reasoning_summary,
        latency_ms=round(total_latency_ms, 2),
        sentiment_tags=classification.sentiment_tags,
        urgency_level=urgency,
    )


def run_batch(
    tickets: list[Ticket],
    provider_override: str | None = None,
) -> tuple[list[PipelineResult], BatchSummary]:
    """Execute pipeline over a batch of tickets and compute aggregate summary."""
    batch_start = time.perf_counter()
    results: list[PipelineResult] = []

    category_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}
    team_counts: dict[str, int] = {}
    escalation_reasons: dict[str, int] = {}
    escalated_count = 0
    total_latency = 0.0

    for ticket in tickets:
        res = process_ticket(ticket, provider_override=provider_override)
        results.append(res)

        total_latency += res.latency_ms
        category_counts[res.category] = category_counts.get(res.category, 0) + 1
        priority_counts[res.priority] = priority_counts.get(res.priority, 0) + 1
        team_counts[res.team] = team_counts.get(res.team, 0) + 1

        if res.escalated:
            escalated_count += 1
            reason_key = res.escalation_reason or "Unknown"
            escalation_reasons[reason_key] = escalation_reasons.get(reason_key, 0) + 1

    total_wall_clock_ms = (time.perf_counter() - batch_start) * 1000.0
    total_tickets = len(tickets)
    avg_latency = (total_latency / total_tickets) if total_tickets > 0 else 0.0
    esc_rate = (escalated_count / total_tickets * 100.0) if total_tickets > 0 else 0.0

    summary = BatchSummary(
        total_tickets=total_tickets,
        processed_at=datetime.now(UTC).isoformat(),
        category_counts=category_counts,
        priority_counts=priority_counts,
        team_counts=team_counts,
        escalated_count=escalated_count,
        escalation_rate_pct=round(esc_rate, 2),
        escalation_reasons=escalation_reasons,
        avg_latency_ms=round(avg_latency, 2),
        total_wall_clock_ms=round(total_wall_clock_ms, 2),
    )

    return results, summary
