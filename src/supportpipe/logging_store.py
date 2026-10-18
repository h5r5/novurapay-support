"""Logging store with PII scrubbing and local review queue persistence."""

import json
import re
from pathlib import Path

from supportpipe.config import settings
from supportpipe.extract.normalize import normalize_digits
from supportpipe.schemas import BatchSummary, PipelineResult

# Regex for Iraqi mobile phones (07XX-XXX-XXXX, +964 7XX XXX XXXX, 07XXXXXXXX) and international E.164 phones
PHONE_REGEX = re.compile(
    r"(?<!\d)(?:(?:\+?964[\s\-]?|00964[\s\-]?|0)?7[3-9](?:[\s\-]?\d){8}|\+\d{1,3}[\s\-]?\d{6,14})\b",
    re.IGNORECASE,
)
# Regex for National ID / Card numbers (12-16 digits)
CARD_ID_REGEX = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b|\b\d{10,12}\b")


def mask_pii(text: str) -> str:
    """Scrub potential PII (phone numbers, national IDs) before writing to logs/store."""
    norm_text = normalize_digits(text)
    masked = PHONE_REGEX.sub("[PHONE_SCRUBBED]", norm_text)
    masked = CARD_ID_REGEX.sub("[ID_SCRUBBED]", masked)
    return masked


LOOPBACK_HOSTS: frozenset[str] = frozenset({"localhost", "127.0.0.1", "::1", "0.0.0.0"})


def is_loopback_host(url_or_host: str | None) -> bool:
    """Check if the given URL or hostname resolves to a local loopback interface."""
    if not url_or_host:
        return False
    target = url_or_host.strip()
    if "://" in target:
        try:
            from urllib.parse import urlparse

            parsed = urlparse(target)
            target = parsed.hostname or ""
        except Exception:
            return False
    elif ":" in target:
        target = target.split(":")[0]
    return target.strip().lower() in LOOPBACK_HOSTS


def scrub_outbound_text(text: str, endpoint: str | None = None) -> str:
    """Central scrubber applying phone and card/national ID masking to outbound text.

    Skips scrubbing ONLY when the destination endpoint host is a loopback address.
    """
    if is_loopback_host(endpoint):
        return text
    return mask_pii(text)



class ReviewQueueStore:
    """Storage for pipeline results awaiting human review."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self.storage_dir = storage_dir or settings.results_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_run(
        self,
        run_id: str,
        results: list[PipelineResult],
        summary: BatchSummary,
    ) -> Path:
        """Persist processed batch results and summary to disk."""
        run_folder = self.storage_dir / run_id
        run_folder.mkdir(parents=True, exist_ok=True)

        results_file = run_folder / "results.jsonl"
        with open(results_file, "w", encoding="utf-8") as f:
            for item in results:
                raw_dict = item.model_dump()
                # Apply PII hygiene to any free text and extracted sensitive fields
                if raw_dict.get("draft_reply"):
                    raw_dict["draft_reply"] = mask_pii(raw_dict["draft_reply"])
                if raw_dict.get("escalation_reason"):
                    raw_dict["escalation_reason"] = mask_pii(raw_dict["escalation_reason"])
                if raw_dict.get("reasoning_summary"):
                    raw_dict["reasoning_summary"] = mask_pii(raw_dict["reasoning_summary"])
                if raw_dict.get("extracted_fields") and isinstance(raw_dict["extracted_fields"], dict):
                    phone = raw_dict["extracted_fields"].get("phone_number")
                    if phone:
                        raw_dict["extracted_fields"]["phone_number"] = mask_pii(str(phone))
                f.write(json.dumps(raw_dict, ensure_ascii=False) + "\n")

        summary_file = run_folder / "summary.json"
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(), f, ensure_ascii=False, indent=2)

        return run_folder

    def record_human_action(
        self,
        ticket_id: str,
        action: str,
        agent_id: str = "AGENT-QA-01",
        notes: str | None = None,
        final_reply: str | None = None,
    ) -> dict[str, str]:
        """Record an immutable audit log entry for human-in-the-loop review actions."""
        from datetime import datetime

        audit_file = self.storage_dir / "human_audit_log.jsonl"
        entry = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "ticket_id": ticket_id,
            "agent_id": agent_id,
            "action": action,  # APPROVED | EDITED | ESCALATED
            "notes": mask_pii(notes) if notes else "",
            "final_reply": mask_pii(final_reply) if final_reply else "",
        }
        with open(audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

