"""Core batch pipeline orchestrator for SupportPipe."""

import logging
import re
import time
from datetime import UTC, datetime

from supportpipe.classify.classify import classify_ticket
from supportpipe.config import settings
from supportpipe.draft.draft import draft_manager
from supportpipe.extract.extract import extract_ticket_details
from supportpipe.extract.validate import validate_extraction_for_category
from supportpipe.routing.escalation import should_escalate
from supportpipe.routing.multi_issue import detect_multi_issue
from supportpipe.routing.route import resolve_team
from supportpipe.schemas import (
    BatchSummary,
    ExtractedFields,
    PipelineResult,
    Ticket,
)

logger = logging.getLogger(__name__)


def process_ticket(
    ticket: Ticket,
    provider_override: str | None = None,
    is_duplicate: bool = False,
) -> PipelineResult:
    """Process a single ticket through the complete typed pipeline."""
    start_time = time.perf_counter()

    # 1. Structured Fast Extraction (System 1 Local Extractor)
    extracted = extract_ticket_details(
        ticket_raw_text=ticket.raw_text,
        submitted_at_iso=ticket.submitted_at,
        category="unknown",
    )

    # 2. Multi-Engine Consensus Classification & Entity Auditing
    classification, provider_tag = classify_ticket(
        ticket_text=ticket.raw_text,
        channel=ticket.channel,
        provider_name=provider_override,
        fast_extracted=extracted,
        ticket_id=ticket.ticket_id,
    )

    # 2.5 Process Cloud Auditor Corrections if Discrepancy Detected
    audit_status = None
    audit_discrepancy = None
    if classification.audit_details:
        audit_status = classification.audit_details.get("audit_status")
        audit_discrepancy = classification.audit_details.get("discrepancy_details")
        if audit_status == "discrepancy_detected" and isinstance(audit_discrepancy, dict):
            field_name = audit_discrepancy.get("field")
            corrected_val = audit_discrepancy.get("corrected_value")
            if field_name == "amount" and corrected_val is not None:
                try:
                    c_amt = int(corrected_val)
                    if c_amt > 0:
                        extracted.amount_iqd = c_amt
                except (ValueError, TypeError):
                    pass
            elif field_name == "event_date" and corrected_val:
                extracted.event_date_resolved = str(corrected_val)
            elif field_name == "reference" and corrected_val:
                extracted.transaction_ref = str(corrected_val)
            elif field_name == "phone" and corrected_val:
                extracted.phone_number = str(corrected_val)

    # 3. Extraction Validation against Business Rules
    ext_valid, ext_reasons = validate_extraction_for_category(
        category_id=classification.category,
        transaction_ref=extracted.transaction_ref,
        amount_iqd=extracted.amount_iqd,
        event_date_resolved=extracted.event_date_resolved,
        amount_usd=extracted.amount_usd,
        currency=extracted.currency,
    )

    # 4. Deterministic Routing (Rule 3)
    team = resolve_team(classification.category)

    # 4.5 Multi-Issue Detection (Rule 03 / MS-02)
    is_multi, multi_reason = detect_multi_issue(ticket.raw_text)

    # 5. Deterministic Escalation Evaluation
    escalated, escalation_reason = should_escalate(
        category=classification.category,
        category_confidence=classification.category_confidence,
        priority=classification.priority,
        priority_confidence=classification.priority_confidence,
        extraction_valid=ext_valid,
        extraction_reasons=ext_reasons,
        is_multi_issue=is_multi,
        is_duplicate=is_duplicate,
    )

    # 6. Response Drafting (Only for non-escalated tickets; human approves before send)
    draft_reply: str | None = None
    if not escalated:
        candidate_draft = None
        if classification.audit_details and classification.audit_details.get("draft_reply"):
            candidate_draft = classification.audit_details.get("draft_reply")
        elif settings.llm_mode != "offline":
            if settings.groq_api_key:
                try:
                    from supportpipe.classify.providers.groq_provider import generate_groq_draft

                    candidate_draft = generate_groq_draft(
                        ticket_raw_text=ticket.raw_text,
                        category=classification.category,
                        priority=classification.priority,
                        extracted=extracted,
                    )
                except Exception as groq_err:
                    logger.warning("Failed generating Groq candidate draft: %s", groq_err)
                    candidate_draft = None
            elif settings.llm_mode == "live" and settings.gemini_api_key:
                try:
                    from supportpipe.classify.providers.gemini_provider import (
                        GeminiClassifierProvider,
                    )

                    if not GeminiClassifierProvider._circuit_open:
                        from supportpipe.draft.generator import generate_candidate_draft

                        candidate_draft = generate_candidate_draft(
                            ticket_raw_text=ticket.raw_text,
                            category=classification.category,
                            priority=classification.priority,
                            extracted=extracted,
                        )
                except Exception as draft_err:
                    logger.warning("Failed generating candidate LLM draft: %s", draft_err)
                    candidate_draft = None

        draft_reply, _, _, draft_source = draft_manager.generate_draft(
            ticket_raw_text=ticket.raw_text,
            category=classification.category,
            priority=classification.priority,
            extracted=extracted,
            llm_draft_candidate=candidate_draft,
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

    is_degraded = bool(getattr(classification, "degraded", False)) or ("fallback" in provider_tag)

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
        audit_status=audit_status,
        audit_discrepancy_details=audit_discrepancy,
        degraded=is_degraded,
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

    seen_user_requests: set[tuple[str, str]] = set()
    seen_user_refs: set[tuple[str, str]] = set()

    for ticket in tickets:
        clean_text_key = " ".join(ticket.raw_text.strip().split())
        u_id = ticket.synthetic_user_id or "anonymous"
        user_req_key = (u_id, clean_text_key)

        ref_match = re.search(
            r"\b(TXN-[A-Z0-9_-]{5,20}|REF-[A-Z0-9_-]{5,20}|(WALLET|NOVURA|REF|TXN)-[0-9]{5,15})\b",
            ticket.raw_text,
            re.IGNORECASE,
        )
        cand_ref = ref_match.group(1).upper() if ref_match else None
        user_ref_key = (u_id, cand_ref) if cand_ref else None

        is_dup = False
        if clean_text_key and user_req_key in seen_user_requests:
            is_dup = True
        elif user_ref_key and user_ref_key in seen_user_refs:
            is_dup = True

        if clean_text_key:
            seen_user_requests.add(user_req_key)
        if user_ref_key:
            seen_user_refs.add(user_ref_key)

        try:
            res = process_ticket(
                ticket,
                provider_override=provider_override,
                is_duplicate=is_dup,
            )
        except Exception as exc:
            logger.exception("Fault isolation: Ticket %s crashed pipeline: %s", ticket.ticket_id, exc)
            res = PipelineResult(
                ticket_id=ticket.ticket_id,
                category="unclear_or_incomplete",
                category_confidence=0.0,
                priority="high",
                priority_confidence=0.0,
                extracted_fields=ExtractedFields(),
                team="General Customer Care",
                escalated=True,
                escalation_reason=f"Pipeline execution error: {exc}",
                draft_reply="[تذكرة مصعدة للمراجعة اليدوية]: خطأ في المعالجة الآلية للبيانات",
                provider_path="fault_fallback",
                reasoning_summary=f"Unhandled exception during pipeline execution: {exc}",
                latency_ms=0.0,
                urgency_level="critical",
                degraded=True,
            )

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
