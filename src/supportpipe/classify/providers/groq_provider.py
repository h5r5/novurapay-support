"""Groq Cloud LLM Classifier and Drafter Provider with Circuit Breaker and 429 Fast-Fail."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.config import ConfigError, settings
from supportpipe.logging_store import scrub_outbound_text
from supportpipe.schemas import ClassificationResult, ExtractedFields, PriorityType
from supportpipe.taxonomy.loader import taxonomy

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """أنت محرك تصنيف ذكي لدعم العملاء في محفظة NovuraPay الإلكترونية في العراق.
مهمتك تحليل رسالة العميل المكتوبة باللهجة العراقية وتصنيفها بدقة تامة.

الفئات المعتمدة رسمياً:
{categories_text}

المطلوب إخراج كائن JSON فقط بالصيغة التالية تماماً:
{{
  "category": "معرف الفئة الإنجليزية بالضبط",
  "category_confidence": 0.95,
  "priority": "high أو medium أو low",
  "priority_confidence": 0.90,
  "reasoning_summary": "سبب التصنيف باختصار شديد بأقل من 300 حرف",
  "sentiment_tags": ["urgent", "angry", "polite"]
}}
"""

DRAFT_SYSTEM_PROMPT = """أنت موظف خدمة عملاء في محفظة دفع إلكتروني عراقية.
مهمتك كتابة رد أولي مهني ومتعاطف باللهجة العراقية المهذبة (2 إلى 3 جمل كحد أقصى) لتأكيد استلام الطلب وطمأنة العميل وتوجيهه للخطوة التالية.

تعليمات الأمان والتأريض الصارمة:
1. استخدم فقط الأرقام والمبالغ المذكورة في نص التذكرة أو البيانات المستخرجة بدقة. لا تخترع أو تخمن أي رقم عملية أو مبلغ على الإطلاق.
2. لا تقدم أي وعود قاطعة أو غير مصرح بها.
3. اكتب باللغة العربية حصراً مع عبارات الاحترام العراقية (أهلاً بك، تدلل، عاشت ايدك، نعتذر عن الإزعاج).
4. اكتب نص الرد المباشر فقط بدون أي مقدمات أو تعليقات توضيحية.
"""


class GroqClassifierProvider(BaseClassifierProvider):
    """Classifier and Drafter using Groq high-capacity LLM API (Llama 3.3 70B / 3.1 8B)."""

    _circuit_open: bool = False
    _circuit_warned: bool = False

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.model = model or settings.groq_model or "llama-3.3-70b-versatile"
        self.timeout = httpx.Timeout(20.0, connect=8.0)

    @classmethod
    def reset_circuit_breaker(cls) -> None:
        """Reset the circuit breaker state."""
        cls._circuit_open = False
        cls._circuit_warned = False

    def classify(
        self,
        ticket_text: str,
        channel: str = "app",
        fast_extracted: ExtractedFields | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> ClassificationResult:
        """Classify ticket text using Groq's high-speed inference endpoint."""
        if self._circuit_open:
            raise RuntimeError(
                "[CIRCUIT_BREAKER] Cloud provider quota exceeded (HTTP 429). Fast-failing Groq request."
            )

        if not self.model or str(self.model).strip().upper() == "OWNER_CONFIRM":
            raise ConfigError(f"Model ID for {self.__class__.__name__} is OWNER_CONFIRM or unconfigured")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured")

        if settings.llm_mode == "live":
            from supportpipe.budget import budget_limiter

            if not budget_limiter.acquire("groq"):
                raise RuntimeError("[BUDGET_EXHAUSTED] Tier 'groq' reached call budget limit.")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        sys_prompt = SYSTEM_PROMPT.format(
            categories_text=taxonomy.format_categories_for_prompt()
        )
        outbound_text = scrub_outbound_text(ticket_text, endpoint=url)
        user_content = f"Channel: {channel}\n<<<TICKET_TEXT>>>\n{outbound_text}\n<<<END_TICKET_TEXT>>>"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=self.timeout) as client:
            try:
                resp = client.post(url, headers=headers, json=payload)
                if resp.status_code == 429:
                    GroqClassifierProvider._circuit_open = True
                    if not GroqClassifierProvider._circuit_warned:
                        logger.warning(
                            "[CIRCUIT_BREAKER] Cloud provider quota exceeded (HTTP 429). "
                            "Tripping circuit breaker and falling back to Jev/Mock for remaining tickets."
                        )
                        GroqClassifierProvider._circuit_warned = True
                    raise httpx.HTTPStatusError(
                        "HTTP 429 Too Many Requests: Groq Quota Exceeded",
                        request=resp.request,
                        response=resp,
                    )
                resp.raise_for_status()
            except httpx.HTTPStatusError as status_err:
                if status_err.response.status_code == 429:
                    GroqClassifierProvider._circuit_open = True
                    if not GroqClassifierProvider._circuit_warned:
                        logger.warning(
                            "[CIRCUIT_BREAKER] Cloud provider quota exceeded (HTTP 429). "
                            "Tripping circuit breaker and falling back to Jev/Mock for remaining tickets."
                        )
                        GroqClassifierProvider._circuit_warned = True
                raise status_err from None

            data = resp.json()
            content_str = data["choices"][0]["message"]["content"]

            # Parse JSON safely
            match = re.search(r"\{.*\}", content_str, re.DOTALL)
            parsed = json.loads(match.group(0)) if match else json.loads(content_str)

            cat = parsed.get("category", "unclear_or_incomplete")
            if cat not in taxonomy.get_valid_category_ids():
                cat = "unclear_or_incomplete"

            raw_prio = str(parsed.get("priority", "medium")).strip().lower()
            prio: PriorityType = (
                raw_prio if raw_prio in ["high", "medium", "low"] else "medium"  # type: ignore[assignment]
            )
            reasoning = str(parsed.get("reasoning_summary", "Classified via Groq"))[:300]
            sentiment_tags = parsed.get("sentiment_tags", [])
            if not isinstance(sentiment_tags, list):
                sentiment_tags = []

            return ClassificationResult(
                category=cat,
                category_confidence=min(
                    1.0, max(0.0, float(parsed.get("category_confidence", 0.85)))
                ),
                priority=prio,
                priority_confidence=min(
                    1.0, max(0.0, float(parsed.get("priority_confidence", 0.85)))
                ),
                reasoning_summary=reasoning,
                sentiment_tags=sentiment_tags,
                audit_details={"provider": "groq", "model": self.model},
            )


def generate_groq_draft(
    ticket_raw_text: str,
    category: str,
    priority: str,
    extracted: ExtractedFields,
) -> str | None:
    """Generate candidate customer response via Groq high-capacity LLM."""
    if not settings.groq_api_key or GroqClassifierProvider._circuit_open:
        return None

    cat_name = taxonomy.categories.get(category, {}).get("name_ar", category)
    if extracted.currency == "USD" and extracted.amount_usd is not None:
        amount_str = f"{extracted.amount_usd:,} دولار"
    elif extracted.amount_iqd is not None:
        amount_str = f"{extracted.amount_iqd:,} دينار"
    else:
        amount_str = "غير محدد"
    ref_str = extracted.transaction_ref or "غير مذكور"
    url = "https://api.groq.com/openai/v1/chat/completions"
    outbound_ticket_text = scrub_outbound_text(ticket_raw_text, endpoint=url)

    prompt_context = (
        f"فئة المشكلة: {cat_name}\n"
        f"مستوى الأولوية: {priority}\n"
        f"المبلغ المستخرج: {amount_str}\n"
        f"رقم العملية: {ref_str}\n"
        f"نص رسالة العميل: {outbound_ticket_text}\n\n"
        f"اكتب الرد المقترح:"
    )

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    model = settings.groq_model or "llama-3.3-70b-versatile"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": DRAFT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_context},
        ],
        "temperature": 0.2,
        "max_tokens": 180,
    }

    try:
        timeout = httpx.Timeout(10.0, connect=4.0)
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 429:
                GroqClassifierProvider._circuit_open = True
                if not GroqClassifierProvider._circuit_warned:
                    logger.warning(
                        "[CIRCUIT_BREAKER] Cloud provider quota exceeded (HTTP 429). "
                        "Tripping circuit breaker and falling back to Jev/Mock for remaining tickets."
                    )
                    GroqClassifierProvider._circuit_warned = True
                return None
            resp.raise_for_status()
            data = resp.json()
            return str(data["choices"][0]["message"]["content"]).strip()
    except Exception as exc:
        logger.warning("Groq candidate drafting failed: %s; falling back to template", exc)
        return None
