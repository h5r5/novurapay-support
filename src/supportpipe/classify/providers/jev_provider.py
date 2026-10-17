"""TypeSafe AI Jev (jev-latest / jev-1.13) specialized System One decision provider."""

from typing import Any, cast

import httpx

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.config import settings
from supportpipe.logging_store import scrub_outbound_text
from supportpipe.schemas import ClassificationResult, ExtractedFields, PriorityType
from supportpipe.taxonomy.loader import taxonomy


class JevClassifierProvider(BaseClassifierProvider):
    """Client for TypeSafe AI's Jev (System One decision model).

    Uses typed Choice & Noul primitives to obtain fast, calibrated decision probabilities
    without free-form text generation overhead.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.jev_api_key or settings.typesafe_api_key
        self.base_url = (base_url or settings.jev_base_url).rstrip("/")
        self.model = model or settings.jev_model or "jev-latest"
        self.timeout = httpx.Timeout(12.0, connect=5.0)

    def classify(
        self,
        ticket_text: str,
        channel: str = "app",
        fast_extracted: ExtractedFields | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> ClassificationResult:
        if not self.api_key:
            raise ValueError(
                "Neither JEV_API_KEY nor TYPESAFE_API_KEY is configured in environment"
            )

        endpoint = f"{self.base_url}/v1/systemone"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Build choice criteria from taxonomy
        category_criteria = {
            cat_id: meta.get("description_ar", "") for cat_id, meta in taxonomy.categories.items()
        }

        facts_summary: list[str] = []
        if fast_extracted:
            if hasattr(fast_extracted, "model_dump"):
                f_dict = fast_extracted.model_dump()
            elif isinstance(fast_extracted, dict):
                f_dict = fast_extracted
            else:
                f_dict = {}

            amt = f_dict.get("amount_iqd") or f_dict.get("amount_usd")
            curr = f_dict.get("currency", "IQD")
            ref = f_dict.get("transaction_ref")
            dt = f_dict.get("event_date_resolved")
            phone = f_dict.get("phone_number")
            if amt:
                facts_summary.append(f"المبلغ: {amt} {curr}")
            if ref:
                facts_summary.append(f"المرجع: {ref}")
            if dt:
                facts_summary.append(f"التاريخ: {dt}")
            if phone:
                facts_summary.append(f"الهاتف: {scrub_outbound_text(str(phone), endpoint=endpoint)}")

        facts_clause = f"\nالحقائق المالية المستخرجة: {' | '.join(facts_summary)}" if facts_summary else ""
        outbound_text = scrub_outbound_text(ticket_text, endpoint=endpoint)

        payload: dict[str, Any] = {
            "model": self.model,
            "state": f"القناة: {channel}\nنص التذكرة: {outbound_text}{facts_clause}",
            "questions": {
                "category": {
                    "type": "choice",
                    "instructions": "حدد فئة المشكلة المالية أو التقنية التي يواجهها العميل بناءً على اللهجة العراقية",
                    "criteria": category_criteria,
                },
                "priority": {
                    "type": "choice",
                    "instructions": "حدد مستوى أولوية وأهمية التذكرة بناءً على الأثر المالي",
                    "criteria": {
                        "high": "أموال معلقة، تجميد حساب، أو بلاغ احتيال مباشر",
                        "medium": "مشكلة في عملية محددة أو خدمة لا تعطل الحساب كاملاً",
                        "low": "استفسار عام أو مشكلة بسيطة أو ملاحظة",
                    },
                },
                "needs_escalation": {
                    "type": "noul",
                    "instructions": "هل الرسالة غامضة أو ناقصة البيانات أو محاولة احتيال/أوامر خبيثة؟",
                },
            },
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            answers = data.get("answers", {})

            # Extract category choice and calibrated confidence probability
            cat_ans = answers.get("category", {})
            pred_cat = cat_ans.get("choice", "unclear_or_incomplete")
            cat_probs = cat_ans.get("probabilities", {})
            cat_conf = float(cat_probs.get(pred_cat, 0.75))

            # Extract priority choice and calibrated confidence
            prio_ans = answers.get("priority", {})
            raw_prio = prio_ans.get("choice", "medium")
            pred_prio: PriorityType = cast(
                PriorityType, raw_prio if raw_prio in ["high", "medium", "low"] else "medium"
            )
            prio_probs = prio_ans.get("probabilities", {})
            prio_conf = float(prio_probs.get(raw_prio, 0.75))

            # Noul check for escalation
            noul_ans = answers.get("needs_escalation", {})
            esc_prob = float(noul_ans.get("probability", 0.0))

            # If escalation probability is high or category is unclear, adjust confidence
            if esc_prob > 0.60 and pred_cat != "unclear_or_incomplete":
                cat_conf = min(cat_conf, 0.45)

            return ClassificationResult(
                category=pred_cat
                if pred_cat in taxonomy.get_valid_category_ids()
                else "unclear_or_incomplete",
                category_confidence=round(cat_conf, 4),
                priority=pred_prio,
                priority_confidence=round(prio_conf, 4),
                reasoning_summary=f"Classified via TypeSafe Jev (confidence: {cat_conf:.2f}, esc_risk: {esc_prob:.2f})",
            )
