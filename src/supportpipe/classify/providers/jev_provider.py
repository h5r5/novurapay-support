"""Jev 1.13 specialized decision model classifier provider."""

import httpx

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.config import settings
from supportpipe.schemas import ClassificationResult
from supportpipe.taxonomy.loader import taxonomy


class JevClassifierProvider(BaseClassifierProvider):
    """Client for Jev 1.13 decision model (typed choice, priority, and calibrated confidence)."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or settings.jev_api_key
        self.base_url = base_url or settings.jev_base_url
        self.timeout = httpx.Timeout(10.0, connect=5.0)

    def classify(self, ticket_text: str, channel: str = "app") -> ClassificationResult:
        if not self.api_key:
            raise ValueError("JEV_API_KEY is not configured; cannot invoke Jev 1.13 provider")

        url = f"{self.base_url.rstrip('/')}/classify"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "jev-1.13",
            "text": ticket_text,
            "channel": channel,
            "choices": taxonomy.get_valid_category_ids(),
            "priority_options": ["high", "medium", "low"],
        }

        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()

            return ClassificationResult(
                category=data.get("category", "unclear_or_incomplete"),
                category_confidence=float(data.get("category_confidence", 0.5)),
                priority=data.get("priority", "medium"),
                priority_confidence=float(data.get("priority_confidence", 0.5)),
                reasoning_summary=data.get(
                    "reasoning_summary", "Classified via Jev 1.13 decision model"
                ),
            )
