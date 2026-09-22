"""Drafting module generating Iraqi Arabic first responses with fallback templates."""

from pathlib import Path

import yaml

from supportpipe.config import settings
from supportpipe.draft.validate import validate_draft_response
from supportpipe.schemas import ExtractedFields


class DraftManager:
    def __init__(self, templates_path: Path | None = None) -> None:
        self.templates_path = templates_path or (Path(__file__).parent / "templates_ar.yaml")
        self.templates: dict[str, str] = {}
        self.load_templates()

    def load_templates(self) -> None:
        """Load reviewed Iraqi Arabic fallback templates from YAML."""
        if self.templates_path.exists():
            with open(self.templates_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.templates = data.get("templates", {})

    def render_template(self, category: str, extracted: ExtractedFields) -> str:
        """Render a deterministic fallback template for a category."""
        raw_tmpl = self.templates.get(
            category,
            self.templates.get(
                "general_inquiry", "أهلاً بك، تم استلام طلبك وسيقوم فريق الدعم بمتابعته بأقرب وقت."
            ),
        )
        amt_str = f"{extracted.amount_iqd:,}" if extracted.amount_iqd is not None else "المحدد"
        ref_str = extracted.transaction_ref or "المذكور"

        rendered = raw_tmpl.replace("{amount_iqd}", amt_str).replace("{transaction_ref}", ref_str)
        return rendered.strip()

    def generate_draft(
        self,
        ticket_raw_text: str,
        category: str,
        priority: str,
        extracted: ExtractedFields,
        llm_draft_candidate: str | None = None,
    ) -> tuple[str, bool, list[str], str]:
        """Produce the final draft response.

        Validates LLM candidate against grounding and safety gates;
        falls back to reviewed template if candidate fails or is missing.

        Returns:
            (draft_reply, safety_passed, failure_reasons, provider_source)
        """
        # If a candidate draft was provided (from LLM or test input), validate against safety gates
        if llm_draft_candidate:
            passed, reasons = validate_draft_response(
                draft_text=llm_draft_candidate,
                ticket_raw_text=ticket_raw_text,
                extracted_ref=extracted.transaction_ref,
                extracted_amount=extracted.amount_iqd,
            )
            if passed:
                return llm_draft_candidate, True, [], "llm"
            # Candidate failed validation, fall back to reviewed template with warning note
            fallback = self.render_template(category, extracted)
            return fallback, False, reasons, "template_fallback"

        # Default / Offline / Template path
        rendered = self.render_template(category, extracted)
        return rendered, True, [], "template"


draft_manager = DraftManager()
