"""Tri-Engine Hybrid Architecture Provider (System 1 Local + System 1.5 Jev + System 2 Gemini).

Combines fast offline heuristics, calibrated choice probabilities, and deep LLM auditing with
an active learning discrepancy feedback loop.
"""

from __future__ import annotations

import logging
from typing import Any

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.learning_store import discrepancy_store
from supportpipe.schemas import ClassificationResult, ExtractedFields, PriorityType
from supportpipe.taxonomy.loader import taxonomy

logger = logging.getLogger(__name__)


class HybridClassifierProvider(BaseClassifierProvider):
    """Tri-Engine Hybrid Classifier combining Local Offline Heuristics, Jev Choice Engine, and Gemini Auditor."""

    def __init__(
        self,
        mock_provider: MockClassifierProvider | None = None,
        jev_provider: JevClassifierProvider | None = None,
        gemini_provider: GeminiClassifierProvider | None = None,
    ) -> None:
        self.mock_provider = mock_provider or MockClassifierProvider()

        has_jev = bool(settings.jev_api_key or settings.typesafe_api_key)
        self.jev_provider = (
            jev_provider
            or (JevClassifierProvider() if (has_jev and settings.llm_mode != "offline") else None)
        )

        has_gemini = bool(settings.gemini_api_key)
        self.gemini_provider = (
            gemini_provider
            or (GeminiClassifierProvider() if (has_gemini and settings.llm_mode != "offline") else None)
        )

    def classify(
        self,
        ticket_text: str,
        channel: str = "app",
        fast_extracted: ExtractedFields | dict[str, Any] | None = None,
        ticket_id: str = "TKT-LIVE",
        **kwargs: Any,
    ) -> ClassificationResult:
        """Execute consensus classification and entity auditing across the three engines."""
        # 1. System 1: Fast local baseline heuristic (always runs, ~0.5ms)
        res_mock = self.mock_provider.classify(ticket_text=ticket_text, channel=channel)

        # If neither cloud engine is available, return local heuristic directly
        if not self.jev_provider and not self.gemini_provider:
            return res_mock

        res_jev: ClassificationResult | None = None
        res_gemini: ClassificationResult | None = None

        # 2. System 1.5: TypeSafe AI Jev Choice Engine
        if self.jev_provider:
            try:
                res_jev = self.jev_provider.classify(
                    ticket_text=ticket_text,
                    channel=channel,
                    fast_extracted=fast_extracted,
                )
            except Exception as jev_err:
                logger.warning("Jev engine failed in hybrid pass: %s", jev_err)
                res_jev = None

        # 3. System 2: Google Gemini Auditor and Drafter
        if self.gemini_provider:
            try:
                res_gemini = self.gemini_provider.classify(
                    ticket_text=ticket_text,
                    channel=channel,
                    fast_extracted=fast_extracted,
                )
            except Exception as gem_err:
                logger.warning("Gemini engine failed in hybrid pass: %s", gem_err)
                res_gemini = None

        # If both cloud engines failed or unavailable, fallback safely to System 1
        if not res_jev and not res_gemini:
            return res_mock

        # 4. Process Gemini Audit Discrepancies (Active Learning Loop)
        gemini_audit = res_gemini.audit_details if res_gemini else None
        if gemini_audit and gemini_audit.get("audit_status") == "discrepancy_detected":
            disc = gemini_audit.get("discrepancy_details")
            if isinstance(disc, dict):
                disc_field = disc.get("field", "unknown")
                disc_val = disc.get("corrected_value")
                disc_reason = disc.get("reason", "Auditor identified discrepancy")
                disc_rule = disc.get("rule_suggestion", "")

                offline_val = None
                if fast_extracted:
                    if hasattr(fast_extracted, "model_dump"):
                        offline_val = fast_extracted.model_dump().get(disc_field)
                    elif isinstance(fast_extracted, dict):
                        offline_val = fast_extracted.get(disc_field)

                discrepancy_store.record_discrepancy(
                    ticket_id=ticket_id,
                    channel=channel,
                    raw_text=ticket_text,
                    discrepancy_type=f"extraction_{disc_field}",
                    field_name=disc_field,
                    offline_value=offline_val,
                    llm_value=disc_val,
                    resolution_applied="llm_correction_audited",
                    confidence_delta=0.15,
                    discrepancy_reason=disc_reason,
                    rule_suggestion=disc_rule,
                )

        # 5. Multi-Engine Consensus Matrix
        final_cat = res_mock.category
        final_cat_conf = res_mock.category_confidence
        final_prio: PriorityType = res_mock.priority
        final_prio_conf = res_mock.priority_confidence
        reasoning = res_mock.reasoning_summary

        if res_jev and res_gemini:
            # All three engines available: check triple consensus
            if res_mock.category == res_jev.category == res_gemini.category:
                # TRIPLE CONSENSUS
                final_cat = res_mock.category
                final_cat_conf = 0.99
                final_prio = res_gemini.priority if res_gemini.priority == res_jev.priority else res_mock.priority
                final_prio_conf = max(res_jev.priority_confidence, res_gemini.priority_confidence)
                reasoning = (
                    f"Triple Consensus (System 1 + Jev 1.13 + Gemini 3.6 Flash) on '{final_cat}' "
                    f"[conf: 99%]"
                )
            elif res_jev.category == res_gemini.category and res_jev.category != res_mock.category:
                # CLOUD CONSENSUS OVERRULE LOCAL HEURISTIC
                final_cat = res_jev.category
                final_cat_conf = round(max(0.92, (res_jev.category_confidence + res_gemini.category_confidence) / 2), 4)
                final_prio = res_gemini.priority
                final_prio_conf = res_gemini.priority_confidence
                reasoning = (
                    f"Cloud Consensus (Jev + Gemini: '{final_cat}') overrules local heuristic ('{res_mock.category}')"
                )
                discrepancy_store.record_discrepancy(
                    ticket_id=ticket_id,
                    channel=channel,
                    raw_text=ticket_text,
                    discrepancy_type="classification_conflict",
                    field_name="category",
                    offline_value=res_mock.category,
                    llm_value=final_cat,
                    resolution_applied="cloud_consensus_override",
                    confidence_delta=final_cat_conf - res_mock.category_confidence,
                    discrepancy_reason="Jev and Gemini agreed against offline heuristic",
                )
            elif res_mock.category in [res_jev.category, res_gemini.category]:
                # 2-out-of-3 MAJORITY
                aligned = res_jev.category if res_mock.category == res_jev.category else res_gemini.category
                aligned_engine = "Jev" if res_mock.category == res_jev.category else "Gemini"
                final_cat = aligned
                final_cat_conf = 0.94
                final_prio = res_gemini.priority
                final_prio_conf = 0.90
                reasoning = f"Majority Consensus (System 1 + {aligned_engine}) on '{final_cat}'"
            else:
                # THREE-WAY CONFLICT: escalate for safety
                final_cat = "unclear_or_incomplete"
                final_cat_conf = 0.45
                final_prio = "high"
                final_prio_conf = 0.90
                reasoning = (
                    f"Consensus Conflict: System 1={res_mock.category}, "
                    f"Jev={res_jev.category}, Gemini={res_gemini.category}. Flagged for review."
                )

        elif res_gemini:
            # System 1 + Gemini available
            if res_mock.category == res_gemini.category:
                final_cat = res_mock.category
                final_cat_conf = round(min(0.98, max(res_mock.category_confidence, res_gemini.category_confidence) + 0.08), 4)
                final_prio = res_gemini.priority
                final_prio_conf = res_gemini.priority_confidence
                reasoning = f"Consensus (System 1 + Gemini 3.6 Flash) on '{final_cat}'"
            else:
                # Adopt Gemini if confident, otherwise flag conflict
                if res_gemini.category_confidence >= 0.85:
                    final_cat = res_gemini.category
                    final_cat_conf = res_gemini.category_confidence
                    reasoning = f"Gemini 3.6 Flash ({final_cat}) corrected System 1 ({res_mock.category})"
                else:
                    final_cat = res_mock.category
                    final_cat_conf = min(res_mock.category_confidence, 0.65)
                    reasoning = f"Ambiguous conflict: System 1 ({res_mock.category}) vs Gemini ({res_gemini.category})"

        elif res_jev:
            # System 1 + Jev available
            if res_mock.category == res_jev.category:
                final_cat = res_mock.category
                final_cat_conf = round(min(0.98, max(res_mock.category_confidence, res_jev.category_confidence) + 0.08), 4)
                final_prio = res_jev.priority
                final_prio_conf = res_jev.priority_confidence
                reasoning = f"Consensus (System 1 + Jev 1.13) on '{final_cat}'"
            else:
                final_cat = res_jev.category if res_jev.category_confidence > 0.80 else res_mock.category
                final_cat_conf = max(res_jev.category_confidence, res_mock.category_confidence)
                reasoning = f"Jev 1.13 ({res_jev.category}) vs System 1 ({res_mock.category})"

        # Attach sentiment tags from local deep sentiment engine
        sentiment_tags = list(res_mock.sentiment_tags)

        # Merge audit details (e.g. LLM draft candidate)
        audit_details = None
        if res_gemini and res_gemini.audit_details:
            audit_details = dict(res_gemini.audit_details)
            audit_details["consensus_engine"] = "tri_engine_hybrid"

        return ClassificationResult(
            category=final_cat if final_cat in taxonomy.get_valid_category_ids() else "unclear_or_incomplete",
            category_confidence=final_cat_conf,
            priority=final_prio,
            priority_confidence=final_prio_conf,
            reasoning_summary=reasoning[:300],
            sentiment_tags=sentiment_tags,
            audit_details=audit_details,
        )
