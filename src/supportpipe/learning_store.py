"""Active learning store for recording and analyzing discrepancies between local heuristics and cloud models.

Enables continuous improvement of the offline fast extractor and classifier without exposing PII.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from supportpipe.config import settings
from supportpipe.logging_store import mask_pii

logger = logging.getLogger(__name__)


class DiscrepancyRecord(BaseModel):
    """Structured record of a disagreement or correction detected by cloud models."""

    record_id: str = Field(default_factory=lambda: f"DISC-{uuid4().hex[:8].upper()}")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    ticket_id: str
    channel: str = "app"
    raw_text_masked: str
    discrepancy_type: str  # 'amount', 'date', 'phone', 'reference', 'category', 'priority'
    field_name: str
    offline_value: Any
    llm_value: Any
    resolution_applied: str  # 'llm_override_applied', 'cloud_consensus_boost', 'escalated_for_review'
    confidence_delta: float = 0.0
    discrepancy_reason: str | None = None
    rule_suggestion: str | None = None


class DiscrepancyStore:
    """Thread-safe persistent JSONL store for audit discrepancy logs."""

    def __init__(self, store_path: Path | None = None) -> None:
        self.file_path = store_path or settings.discrepancy_store_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def record_discrepancy(
        self,
        ticket_id: str,
        channel: str,
        raw_text: str,
        discrepancy_type: str,
        field_name: str,
        offline_value: Any,
        llm_value: Any,
        resolution_applied: str,
        confidence_delta: float = 0.0,
        discrepancy_reason: str | None = None,
        rule_suggestion: str | None = None,
    ) -> DiscrepancyRecord:
        """Create, mask, and append a discrepancy record to JSONL."""
        masked_text = mask_pii(raw_text)
        safe_offline = (
            mask_pii(str(offline_value))
            if (field_name == "phone" or isinstance(offline_value, str))
            else offline_value
        )
        safe_llm = (
            mask_pii(str(llm_value))
            if (field_name == "phone" or isinstance(llm_value, str))
            else llm_value
        )
        safe_reason = mask_pii(discrepancy_reason) if discrepancy_reason else None

        record = DiscrepancyRecord(
            ticket_id=ticket_id,
            channel=channel,
            raw_text_masked=masked_text,
            discrepancy_type=discrepancy_type,
            field_name=field_name,
            offline_value=safe_offline,
            llm_value=safe_llm,
            resolution_applied=resolution_applied,
            confidence_delta=round(confidence_delta, 4),
            discrepancy_reason=safe_reason,
            rule_suggestion=rule_suggestion,
        )

        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.model_dump(), ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error("Failed persisting discrepancy record %s: %s", record.record_id, e)

        return record

    def load_discrepancies(self, limit: int = 100) -> list[DiscrepancyRecord]:
        """Load the most recent discrepancy records."""
        if not self.file_path.exists():
            return []

        records: list[DiscrepancyRecord] = []
        try:
            with open(self.file_path, encoding="utf-8") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        records.append(DiscrepancyRecord.model_validate_json(line_str))
                        if len(records) >= limit:
                            break
                    except Exception as err:
                        logger.warning("Failed parsing line in discrepancy store: %s", err)
        except Exception as e:
            logger.error("Error reading discrepancy store %s: %s", self.file_path, e)

        return records

    def get_summary_stats(self) -> dict[str, Any]:
        """Compute aggregate statistics of all recorded discrepancies."""
        if not self.file_path.exists():
            return {
                "total_discrepancies": 0,
                "by_type": {},
                "by_resolution": {},
                "top_suggestions": [],
            }

        records = self.load_discrepancies(limit=1000)
        by_type: dict[str, int] = {}
        by_res: dict[str, int] = {}
        suggestions: list[str] = []

        for r in records:
            by_type[r.discrepancy_type] = by_type.get(r.discrepancy_type, 0) + 1
            by_res[r.resolution_applied] = by_res.get(r.resolution_applied, 0) + 1
            if r.rule_suggestion and r.rule_suggestion not in suggestions:
                suggestions.append(r.rule_suggestion)

        return {
            "total_discrepancies": len(records),
            "by_type": by_type,
            "by_resolution": by_res,
            "top_suggestions": suggestions[:10],
        }


# Singleton instance
discrepancy_store = DiscrepancyStore()
