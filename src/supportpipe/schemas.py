"""Pydantic data schemas for SupportPipe entities, labels, results, and manifests."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

ChannelType = Literal["app", "whatsapp", "sms"]
PriorityType = Literal["high", "medium", "low"]


class Ticket(BaseModel):
    """Input support ticket submitted by a customer."""

    ticket_id: str = Field(..., description="Unique ticket identifier (e.g., TKT-2026-0001)")
    channel: ChannelType = Field(default="app", description="Submission channel")
    raw_text: str = Field(..., description="Raw message in Iraqi Arabic dialect")
    submitted_at: str = Field(
        ..., description="ISO 8601 timestamp with Asia/Baghdad timezone (+03:00)"
    )
    synthetic_user_id: str = Field(..., description="Anonymized synthetic customer identifier")

    @field_validator("raw_text")
    @classmethod
    def validate_non_empty_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ticket raw_text cannot be completely empty")
        return v

    @field_validator("submitted_at")
    @classmethod
    def validate_timestamp_format(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
        except Exception as e:
            raise ValueError(f"Invalid ISO 8601 timestamp '{v}': {e}") from e
        return v


class ExpectedFields(BaseModel):
    """Ground truth expected structured fields for a ticket."""

    transaction_ref: str | None = None
    amount_iqd: int | None = None
    event_date: str | None = None  # Expected resolved ISO date YYYY-MM-DD


class TicketLabel(BaseModel):
    """Ground-truth evaluation label (strictly held out during inference)."""

    category: str
    priority: PriorityType
    expected_team: str
    expected_fields: ExpectedFields = Field(default_factory=ExpectedFields)
    edge_case: str | None = (
        None  # e.g., dual_problem, missing_ref, prompt_injection, vague_one_liner
    )
    notes: str | None = None


class LabeledTicket(BaseModel):
    """Synthetic dataset record pairing ticket with held-out label."""

    ticket: Ticket
    label: TicketLabel


class ClassificationResult(BaseModel):
    """Output from the classification stage (Section 7.1)."""

    category: str
    category_confidence: float = Field(..., ge=0.0, le=1.0)
    priority: PriorityType
    priority_confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning_summary: str = Field(..., max_length=300)


class ExtractedFields(BaseModel):
    """Output from the structured extraction stage (Section 7.2)."""

    transaction_ref: str | None = None
    amount_iqd: int | None = None
    event_date_text: str | None = None  # Original phrase (e.g., 'امس العصر')
    event_date_resolved: str | None = None  # ISO date (e.g., '2026-09-21') computed by code
    extraction_confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class PipelineResult(BaseModel):
    """Complete result of running a single ticket through the pipeline."""

    ticket_id: str
    category: str
    category_confidence: float
    priority: PriorityType
    priority_confidence: float
    extracted_fields: ExtractedFields
    team: str
    escalated: bool
    escalation_reason: str | None = None
    draft_reply: str | None = None
    provider_path: str  # e.g., 'jev', 'gemini', 'groq', 'template', 'offline_mock'
    reasoning_summary: str = ""
    latency_ms: float = 0.0


class BatchSummary(BaseModel):
    """Run summary generated after batch processing (Must-Have 01 & 02)."""

    total_tickets: int
    processed_at: str
    category_counts: dict[str, int]
    priority_counts: dict[str, int]
    team_counts: dict[str, int]
    escalated_count: int
    escalation_rate_pct: float
    escalation_reasons: dict[str, int]
    avg_latency_ms: float
    total_wall_clock_ms: float


class RunManifest(BaseModel):
    """Reproducibility manifest recorded for every run (Section 5 & 10)."""

    run_id: str
    created_at: str
    git_commit: str
    split: str
    dataset_hash: str
    model_id: str
    provider: str
    config_hash: str
    additional_metadata: dict[str, Any] = Field(default_factory=dict)
