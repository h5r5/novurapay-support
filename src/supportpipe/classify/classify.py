"""Classification entrypoint with provider fallback, hybrid routing, and caching."""

from __future__ import annotations

import logging
from typing import Any

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
from supportpipe.classify.providers.hybrid_provider import HybridClassifierProvider
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.local_llm_provider import LocalLLMClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.schemas import ClassificationResult, ExtractedFields

logger = logging.getLogger(__name__)


def get_classifier_provider(
    provider_name: str | None = None,
    offline_model_version: str | None = None,
) -> BaseClassifierProvider:
    """Instantiate classifier provider based on settings and availability."""
    if provider_name is None and settings.llm_mode == "offline":
        return MockClassifierProvider(offline_model_version=offline_model_version)

    has_jev = bool(settings.jev_api_key or settings.typesafe_api_key)
    has_gemini = bool(settings.gemini_api_key)
    has_groq = bool(settings.groq_api_key)

    # Determine default provider
    default_name = "mock"
    if settings.llm_mode == "hybrid" or (has_jev and has_gemini):
        default_name = "hybrid"
    elif has_groq:
        default_name = "groq"
    elif has_gemini:
        default_name = "gemini"
    elif has_jev:
        default_name = "jev"

    name = (provider_name or default_name).lower()

    if name in ["hybrid", "tri_engine", "tri"]:
        return HybridClassifierProvider()
    elif name == "groq" and has_groq:
        return GroqClassifierProvider()
    elif name == "jev" and has_jev:
        return JevClassifierProvider()
    elif name == "gemini" and has_gemini:
        return GeminiClassifierProvider()
    elif name in ["local", "local_llm"]:
        return LocalLLMClassifierProvider()
    elif name == "mock":
        return MockClassifierProvider(offline_model_version=offline_model_version)

    # Fallback to deterministic mock
    logger.warning(
        "Requested provider '%s' not fully configured or offline mode active; falling back to MockClassifierProvider",
        name,
    )
    return MockClassifierProvider(offline_model_version=offline_model_version)


def classify_ticket(
    ticket_text: str,
    channel: str = "app",
    provider_name: str | None = None,
    fast_extracted: ExtractedFields | dict[str, Any] | None = None,
    ticket_id: str = "TKT-LIVE",
) -> tuple[ClassificationResult, str]:
    """Classify a support ticket into category, priority, and confidences.

    Returns:
        (ClassificationResult, provider_path_name)
    """
    provider = get_classifier_provider(provider_name)
    provider_name_tag = provider.__class__.__name__.replace("ClassifierProvider", "").lower()

    try:
        result = provider.classify(
            ticket_text=ticket_text,
            channel=channel,
            fast_extracted=fast_extracted,
            ticket_id=ticket_id,
        )
        return result, provider_name_tag
    except Exception as e:
        logger.error("Classification failed via %s: %s. Falling back to Mock.", provider_name_tag, e)
        fallback = MockClassifierProvider().classify(ticket_text=ticket_text, channel=channel)
        fallback.degraded = True
        return fallback, f"{provider_name_tag}_fallback_mock"
