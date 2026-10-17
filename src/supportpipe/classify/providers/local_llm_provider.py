"""Local LLM classification provider via OpenAI-compatible endpoint with strict schema validation."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import httpx

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.config import ConfigError, settings
from supportpipe.logging_store import scrub_outbound_text
from supportpipe.schemas import ClassificationResult, PriorityType
from supportpipe.taxonomy.loader import taxonomy

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an automated support ticket classifier for NovuraPay electronic wallet in Iraq.
Analyze the customer's inquiry in Iraqi Arabic or Kurdish and output ONLY valid JSON matching the exact schema:
{{
  "category": "valid_category_id",
  "category_confidence": 0.95,
  "priority": "high" | "medium" | "low",
  "priority_confidence": 0.90,
  "reasoning_summary": "Short explanation under 300 characters",
  "sentiment_tags": ["urgent", "angry"]
}}

Allowed Categories:
{categories_text}
"""


class LocalLLMClassifierProvider(BaseClassifierProvider):
    """Generic OpenAI-compatible local LLM provider.

    Does not contain any model-specific logic or branding.
    Strictly validates JSON responses against the classification schema.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        api_key: str | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.base_url = (base_url or settings.local_llm_base_url).rstrip("/")
        self.model = model or settings.local_llm_model
        timeout_val = timeout if timeout is not None else settings.local_llm_timeout
        self.timeout = httpx.Timeout(timeout_val, connect=5.0)
        self.api_key = api_key or settings.local_llm_api_key or "local"
        self.enabled = settings.local_llm_enabled if enabled is None else enabled

    def classify(
        self,
        ticket_text: str,
        channel: str = "app",
        **kwargs: Any,
    ) -> ClassificationResult:
        """Classify ticket via local OpenAI-compatible /chat/completions endpoint."""
        if not self.enabled:
            raise RuntimeError(
                "Local LLM provider is disabled by default. Enable via settings.local_llm_enabled = True."
            )

        if not self.model or str(self.model).strip().upper() == "OWNER_CONFIRM":
            raise ConfigError("Local LLM model ID is OWNER_CONFIRM or unconfigured.")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        outbound_text = scrub_outbound_text(ticket_text, endpoint=url)
        categories_text = taxonomy.format_categories_for_prompt()

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT.format(categories_text=categories_text)},
                {"role": "user", "content": f"Channel: {channel}\nMessage: {outbound_text}"},
            ],
            "temperature": 0.0,
        }

        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # Extract content from OpenAI response structure
        try:
            raw_content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Invalid OpenAI-compatible completion response format: {data}") from exc

        return self._parse_and_validate_json(raw_content)

    def _parse_and_validate_json(self, raw_content: str) -> ClassificationResult:
        """Strict JSON parsing and schema validation."""
        text = raw_content.strip()

        # Strip optional markdown code fences ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Local LLM returned non-JSON text: '{text[:150]}'") from exc

        if not isinstance(parsed, dict):
            raise ValueError(f"Local LLM output must be a JSON object, got {type(parsed).__name__}")

        # Strict field validation
        for required_field in ["category", "category_confidence", "priority", "priority_confidence"]:
            if required_field not in parsed:
                raise ValueError(f"Local LLM response missing required field '{required_field}': {parsed}")

        category = str(parsed["category"]).strip()
        valid_cats = taxonomy.get_valid_category_ids()
        if category not in valid_cats:
            # Fall back to unclear_or_incomplete if returned category is unrecognized
            category = "unclear_or_incomplete"

        try:
            cat_conf = float(parsed["category_confidence"])
            if not (0.0 <= cat_conf <= 1.0):
                raise ValueError(f"category_confidence must be between 0.0 and 1.0, got {cat_conf}")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid category_confidence: {parsed.get('category_confidence')}") from exc

        priority_raw = str(parsed["priority"]).strip().lower()
        if priority_raw not in ["high", "medium", "low"]:
            raise ValueError(f"Invalid priority '{priority_raw}', must be 'high', 'medium', or 'low'")
        priority: PriorityType = priority_raw  # type: ignore[assignment]

        try:
            prio_conf = float(parsed["priority_confidence"])
            if not (0.0 <= prio_conf <= 1.0):
                raise ValueError(f"priority_confidence must be between 0.0 and 1.0, got {prio_conf}")
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid priority_confidence: {parsed.get('priority_confidence')}") from exc

        reasoning = str(parsed.get("reasoning_summary", ""))[:300]
        sentiment_tags = parsed.get("sentiment_tags", [])
        if not isinstance(sentiment_tags, list):
            sentiment_tags = []
        tags = [str(t) for t in sentiment_tags]

        return ClassificationResult(
            category=category,
            category_confidence=round(cat_conf, 4),
            priority=priority,
            priority_confidence=round(prio_conf, 4),
            reasoning_summary=reasoning,
            sentiment_tags=tags,
            degraded=False,
        )
