"""Classification entrypoint with provider fallback and caching."""

import logging

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.schemas import ClassificationResult

logger = logging.getLogger(__name__)


def get_classifier_provider(provider_name: str | None = None) -> BaseClassifierProvider:
    """Instantiate classifier provider based on settings and availability."""
    if settings.llm_mode == "offline":
        return MockClassifierProvider()

    has_jev = bool(settings.jev_api_key or settings.typesafe_api_key)
    name = (provider_name or ("jev" if has_jev else "gemini")).lower()

    if name == "jev" and has_jev:
        return JevClassifierProvider()
    elif name == "gemini" and settings.gemini_api_key:
        return GeminiClassifierProvider()

    # Fallback to deterministic mock
    logger.warning(
        "No live API keys configured or offline mode active; using MockClassifierProvider"
    )
    return MockClassifierProvider()


def classify_ticket(
    ticket_text: str,
    channel: str = "app",
    provider_name: str | None = None,
) -> tuple[ClassificationResult, str]:
    """Classify a support ticket into category, priority, and confidences.

    Returns:
        (ClassificationResult, provider_path_name)
    """
    provider = get_classifier_provider(provider_name)
    provider_name_tag = provider.__class__.__name__.replace("ClassifierProvider", "").lower()

    try:
        result = provider.classify(ticket_text=ticket_text, channel=channel)
        return result, provider_name_tag
    except Exception as e:
        logger.error(f"Classification failed via {provider_name_tag}: {e}. Falling back to Mock.")
        fallback = MockClassifierProvider().classify(ticket_text=ticket_text, channel=channel)
        return fallback, f"{provider_name_tag}_fallback_mock"
