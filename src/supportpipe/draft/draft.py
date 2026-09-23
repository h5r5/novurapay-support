"""Drafting module generating Iraqi Arabic first responses with fallback templates."""

from pathlib import Path

import yaml

from supportpipe.draft.validate import validate_draft_response
from supportpipe.extract.language import detect_ticket_language
from supportpipe.schemas import ExtractedFields


class DraftManager:
    def __init__(
        self,
        templates_path: Path | None = None,
        templates_ku_path: Path | None = None,
    ) -> None:
        self.templates_path = templates_path or (Path(__file__).parent / "templates_ar.yaml")
        self.templates_ku_path = templates_ku_path or (Path(__file__).parent / "templates_ku.yaml")
        self.templates_ar: dict[str, str] = {}
        self.templates_ku: dict[str, str] = {}
        self.load_templates()

    def load_templates(self) -> None:
        """Load reviewed Arabic and Kurdish fallback templates from YAML."""
        if self.templates_path.exists():
            with open(self.templates_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.templates_ar = data.get("templates", {})

        if self.templates_ku_path.exists():
            with open(self.templates_ku_path, encoding="utf-8") as f:
                ku_data = yaml.safe_load(f)
                self.templates_ku = ku_data.get("templates", {})

    @property
    def templates(self) -> dict[str, str]:
        """Backward compatibility property returning Arabic templates."""
        return self.templates_ar

    def render_template(
        self,
        category: str,
        extracted: ExtractedFields,
        language: str = "ar",
    ) -> str:
        """Render a deterministic fallback template for a category in Arabic or Kurdish."""
        tmpl_dict = self.templates_ku if language.startswith("ku") else self.templates_ar
        default_msg = (
            "سڵاو، داواکارییەکەت گەیشت و تیمی پشتگیری بەدواداچوونی بۆ دەکات."
            if language.startswith("ku")
            else "أهلاً بك، تم استلام طلبك وسيقوم فريق الدعم بمتابعته بأقرب وقت."
        )

        raw_tmpl = tmpl_dict.get(category, tmpl_dict.get("general_inquiry", default_msg))

        if extracted.currency == "USD" and extracted.amount_usd is not None:
            usd_label = "دۆلار" if language.startswith("ku") else "دولار"
            raw_tmpl = raw_tmpl.replace("{amount_iqd} دينار", f"{extracted.amount_usd:,} {usd_label}")
            raw_tmpl = raw_tmpl.replace("{amount_iqd} دینار", f"{extracted.amount_usd:,} {usd_label}")
            raw_tmpl = raw_tmpl.replace("{amount_iqd}", f"{extracted.amount_usd:,} {usd_label}")
            amt_str = f"{extracted.amount_usd:,}"
        else:
            default_amt = "دیاریکراو" if language.startswith("ku") else "المحدد"
            amt_str = f"{extracted.amount_iqd:,}" if extracted.amount_iqd is not None else default_amt

        ref_str = extracted.transaction_ref or ("المذكور" if not language.startswith("ku") else "دیاریکراو")
        phone_str = extracted.phone_number or ("المذكور" if not language.startswith("ku") else "دیاریکراو")

        rendered = (
            raw_tmpl.replace("{amount_iqd}", amt_str)
            .replace("{transaction_ref}", ref_str)
            .replace("{phone_number}", phone_str)
        )
        return rendered.strip()

    def generate_draft(
        self,
        ticket_raw_text: str,
        category: str,
        priority: str,
        extracted: ExtractedFields,
        llm_draft_candidate: str | None = None,
        language: str | None = None,
    ) -> tuple[str, bool, list[str], str]:
        """Produce the final draft response.

        Validates candidate against grounding and safety gates;
        falls back to reviewed template if candidate fails or is missing.

        Returns:
            (draft_reply, safety_passed, failure_reasons, provider_source)
        """
        lang = language or detect_ticket_language(ticket_raw_text)

        # If a candidate draft was provided (from LLM or test input), validate against safety gates
        if llm_draft_candidate:
            passed, reasons = validate_draft_response(
                draft_text=llm_draft_candidate,
                ticket_raw_text=ticket_raw_text,
                extracted_ref=extracted.transaction_ref,
                extracted_amount=extracted.amount_iqd,
                extracted_phone=extracted.phone_number,
                extracted_amount_usd=extracted.amount_usd,
                language=lang,
            )
            if passed:
                return llm_draft_candidate, True, [], "llm"
            # Candidate failed validation, fall back to reviewed template with warning note
            fallback = self.render_template(category, extracted, language=lang)
            return fallback, False, reasons, "template_fallback"

        # Default / Offline / Template path
        rendered = self.render_template(category, extracted, language=lang)
        return rendered, True, [], "template"


draft_manager = DraftManager()
