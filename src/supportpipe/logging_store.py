"""Logging store with PII scrubbing and local review queue persistence."""

import json
import re
from pathlib import Path

from supportpipe.config import settings
from supportpipe.schemas import BatchSummary, PipelineResult

# Regex for Iraqi mobile phones (07XX-XXX-XXXX, +9647XXXXXXXX)
PHONE_REGEX = re.compile(r"(\+?964\s?|0)?7[3-9]\d{8}\b")
# Regex for National ID / Card numbers (12-16 digits)
CARD_ID_REGEX = re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b|\b\d{10,12}\b")


def mask_pii(text: str) -> str:
    """Scrub potential PII (phone numbers, national IDs) before writing to logs/store."""
    masked = PHONE_REGEX.sub("[PHONE_SCRUBBED]", text)
    masked = CARD_ID_REGEX.sub("[ID_SCRUBBED]", masked)
    return masked


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
                # Apply PII hygiene to any free text
                if raw_dict.get("draft_reply"):
                    raw_dict["draft_reply"] = mask_pii(raw_dict["draft_reply"])
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

