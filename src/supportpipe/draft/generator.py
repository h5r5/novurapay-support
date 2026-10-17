"""Contextual response drafting generator using LLM with grounding constraints."""

import logging
from typing import Any

import httpx

from supportpipe.config import settings
from supportpipe.logging_store import scrub_outbound_text
from supportpipe.schemas import ExtractedFields
from supportpipe.taxonomy.loader import taxonomy

logger = logging.getLogger(__name__)

DRAFT_SYSTEM_PROMPT = """أنت موظف خدمة عملاء في محفظة دفع إلكتروني عراقية.
مهمتك كتابة رد أولي مهني ومتعاطف باللهجة العراقية المهذبة (2 إلى 3 جمل كحد أقصى) لتأكيد استلام الطلب وطمأنة العميل وتوجيهه للخطوة التالية.

تعليمات الأمان والتأريض الصارمة:
1. استخدم فقط الأرقام والمبالغ المذكورة في نص التذكرة أو البيانات المستخرجة بدقة. لا تخترع أو تخمن أي رقم عملية أو مبلغ على الإطلاق.
2. لا تقدم أي وعود قاطعة أو غير مصرح بها (مثل: "نضمن لك استرجاع المبلغ 100%" أو "خلال ساعة ترجع فلوسك").
3. اكتب باللغة العربية حصراً مع عبارات الاحترام العراقية (أهلاً بك، تدلل، عاشت ايدك، نعتذر عن الإزعاج).
4. اكتب نص الرد المباشر فقط بدون أي مقدمات أو تعليقات توضيحية.
"""


def generate_candidate_draft(
    ticket_raw_text: str,
    category: str,
    priority: str,
    extracted: ExtractedFields,
) -> str | None:
    """Generate a contextual customer response candidate via LLM."""
    if settings.llm_mode != "live" or not settings.gemini_api_key:
        return None

    from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider

    if GeminiClassifierProvider._circuit_open:
        return None

    cat_name = taxonomy.categories.get(category, {}).get("name_ar", category)
    if extracted.currency == "USD" and extracted.amount_usd is not None:
        amount_str = f"{extracted.amount_usd:,} دولار"
    elif extracted.amount_iqd is not None:
        amount_str = f"{extracted.amount_iqd:,} دينار"
    else:
        amount_str = "غير محدد"
    ref_str = extracted.transaction_ref or "غير مذكور"
    model = settings.gemini_model or "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    outbound_ticket_text = scrub_outbound_text(ticket_raw_text, endpoint=url)

    prompt_context = (
        f"فئة المشكلة: {cat_name}\n"
        f"مستوى الأولوية: {priority}\n"
        f"المبلغ المستخرج: {amount_str}\n"
        f"رقم العملية: {ref_str}\n"
        f"نص رسالة العميل: {outbound_ticket_text}\n\n"
        f"اكتب الرد المقترح:"
    )

    headers = {"x-goog-api-key": settings.gemini_api_key}
    payload: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{DRAFT_SYSTEM_PROMPT}\n\n{prompt_context}"}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 180,
        },
    }

    try:
        timeout = httpx.Timeout(10.0, connect=4.0)
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 429:
                GeminiClassifierProvider._circuit_open = True
                if not GeminiClassifierProvider._circuit_warned:
                    logger.warning(
                        "[CIRCUIT_BREAKER] Cloud provider quota exceeded (HTTP 429). "
                        "Tripping circuit breaker and falling back to Jev/Mock for remaining tickets."
                    )
                    GeminiClassifierProvider._circuit_warned = True
                return None
            resp.raise_for_status()
            data = resp.json()
            candidate: str = str(data["candidates"][0]["content"]["parts"][0]["text"]).strip()
            return candidate
    except Exception as exc:
        logger.warning("LLM candidate drafting failed: %s; falling back to template", exc)
        return None
