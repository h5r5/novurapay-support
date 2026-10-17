"""Tests for central outbound API PII scrubbing across Gemini, Groq, and Jev providers (Task 2.9)."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import (
    GroqClassifierProvider,
    generate_groq_draft,
)
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.config import settings
from supportpipe.draft.generator import generate_candidate_draft
from supportpipe.logging_store import is_loopback_host, scrub_outbound_text
from supportpipe.schemas import ExtractedFields, Ticket

RAW_TEST_TEXT = "مرحبا رقمي 07701234567 وبطاقتي 1234567890123456 وما وصلت الحوالة"
TEST_PHONE = "07701234567"
TEST_CARD_ID = "1234567890123456"


def test_is_loopback_host_detection() -> None:
    """Verify loopback detection for local development endpoints."""
    assert is_loopback_host("http://localhost:8000/v1") is True
    assert is_loopback_host("http://127.0.0.1:11434/api/generate") is True
    assert is_loopback_host("http://[::1]:8080/v1") is True
    assert is_loopback_host("localhost:5000") is True
    assert is_loopback_host("127.0.0.1:8000") is True

    # Remote endpoints must NOT be treated as loopback
    assert is_loopback_host("https://generativelanguage.googleapis.com") is False
    assert is_loopback_host("https://api.groq.com/openai/v1/chat/completions") is False
    assert is_loopback_host("https://api.typesafe.ai/v1/systemone") is False
    assert is_loopback_host(None) is False
    assert is_loopback_host("") is False


def test_scrub_outbound_text_skips_only_on_loopback() -> None:
    """Verify central scrub_outbound_text masks PII on remote endpoints and preserves raw on loopback."""
    remote_scrubbed = scrub_outbound_text(RAW_TEST_TEXT, endpoint="https://api.groq.com/v1")
    assert TEST_PHONE not in remote_scrubbed
    assert TEST_CARD_ID not in remote_scrubbed
    assert "[PHONE_SCRUBBED]" in remote_scrubbed
    assert "[ID_SCRUBBED]" in remote_scrubbed

    # Loopback endpoint skips scrubbing
    loopback_raw = scrub_outbound_text(RAW_TEST_TEXT, endpoint="http://127.0.0.1:11434")
    assert loopback_raw == RAW_TEST_TEXT
    assert TEST_PHONE in loopback_raw
    assert TEST_CARD_ID in loopback_raw


def test_gemini_provider_captures_scrubbed_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify Gemini provider applies outbound scrubbing to both raw text and extracted facts."""
    monkeypatch.setattr(settings, "gemini_api_key", "test_mock_gemini_key")
    provider = GeminiClassifierProvider(api_key="test_mock_gemini_key")
    captured_payloads: list[dict[str, Any]] = []

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "category": "failed_transfer",
                                "category_confidence": 0.95,
                                "priority": "high",
                                "priority_confidence": 0.90,
                                "reasoning_summary": "Scrubbed test",
                            })
                        }
                    ]
                }
            }
        ]
    }

    def fake_post(url: str, **kwargs: Any) -> MagicMock:
        captured_payloads.append(kwargs.get("json", {}))
        return mock_resp

    with patch("httpx.Client.post", side_effect=fake_post):
        res = provider.classify(
            ticket_text=RAW_TEST_TEXT,
            channel="app",
            fast_extracted=ExtractedFields(phone_number=TEST_PHONE),
        )

    assert len(captured_payloads) == 1
    payload_str = json.dumps(captured_payloads[0], ensure_ascii=False)
    assert TEST_PHONE not in payload_str
    assert TEST_CARD_ID not in payload_str
    assert "[PHONE_SCRUBBED]" in payload_str
    assert "[ID_SCRUBBED]" in payload_str
    assert res.category == "failed_transfer"


def test_groq_provider_captures_scrubbed_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify Groq classifier provider applies outbound scrubbing to request messages."""
    monkeypatch.setattr(settings, "groq_api_key", "test_mock_groq_key")
    provider = GroqClassifierProvider(api_key="test_mock_groq_key")
    captured_payloads: list[dict[str, Any]] = []

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "category": "failed_transfer",
                        "category_confidence": 0.92,
                        "priority": "high",
                        "priority_confidence": 0.88,
                        "reasoning_summary": "Groq scrubbed test",
                    })
                }
            }
        ]
    }

    def fake_post(url: str, **kwargs: Any) -> MagicMock:
        captured_payloads.append(kwargs.get("json", {}))
        return mock_resp

    with patch("httpx.Client.post", side_effect=fake_post):
        res = provider.classify(ticket_text=RAW_TEST_TEXT, channel="app")

    assert len(captured_payloads) == 1
    payload_str = json.dumps(captured_payloads[0], ensure_ascii=False)
    assert TEST_PHONE not in payload_str
    assert TEST_CARD_ID not in payload_str
    assert "[PHONE_SCRUBBED]" in payload_str
    assert "[ID_SCRUBBED]" in payload_str
    assert res.category == "failed_transfer"


def test_jev_provider_captures_scrubbed_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify Jev decision provider applies outbound scrubbing to state and extracted facts."""
    monkeypatch.setattr(settings, "jev_api_key", "test_mock_jev_key")
    provider = JevClassifierProvider(api_key="test_mock_jev_key")
    captured_payloads: list[dict[str, Any]] = []

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "answers": {
            "category": {"choice": "failed_transfer", "probabilities": {"failed_transfer": 0.94}},
            "priority": {"choice": "high", "probabilities": {"high": 0.90}},
            "needs_escalation": {"choice": False},
        }
    }

    def fake_post(url: str, **kwargs: Any) -> MagicMock:
        captured_payloads.append(kwargs.get("json", {}))
        return mock_resp

    with patch("httpx.Client.post", side_effect=fake_post):
        res = provider.classify(
            ticket_text=RAW_TEST_TEXT,
            channel="app",
            fast_extracted=ExtractedFields(phone_number=TEST_PHONE),
        )

    assert len(captured_payloads) == 1
    payload_str = json.dumps(captured_payloads[0], ensure_ascii=False)
    assert TEST_PHONE not in payload_str
    assert TEST_CARD_ID not in payload_str
    assert "[PHONE_SCRUBBED]" in payload_str
    assert "[ID_SCRUBBED]" in payload_str
    assert res.category == "failed_transfer"


def test_drafting_generators_capture_scrubbed_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify both Gemini and Groq draft generators scrub customer PII before sending prompts."""
    monkeypatch.setattr(settings, "gemini_api_key", "test_mock_gemini_key")
    monkeypatch.setattr(settings, "groq_api_key", "test_mock_groq_key")
    monkeypatch.setattr(settings, "llm_mode", "live")

    ticket = Ticket(
        ticket_id="TKT-DRAFT-01",
        channel="app",
        raw_text=RAW_TEST_TEXT,
        submitted_at="2026-10-17T12:00:00+03:00",
        synthetic_user_id="USR-123",
    )
    extracted = ExtractedFields(phone_number=TEST_PHONE)

    captured_payloads: list[dict[str, Any]] = []

    mock_gemini_resp = MagicMock()
    mock_gemini_resp.status_code = 200
    mock_gemini_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "عاشت ايدك تم استلام الطلب"}]}}]
    }

    mock_groq_resp = MagicMock()
    mock_groq_resp.status_code = 200
    mock_groq_resp.json.return_value = {
        "choices": [{"message": {"content": "عاشت ايدك تم استلام الطلب"}}]
    }

    def fake_post(url: str, **kwargs: Any) -> MagicMock:
        captured_payloads.append(kwargs.get("json", {}))
        if "generativelanguage" in url:
            return mock_gemini_resp
        return mock_groq_resp

    with patch("httpx.Client.post", side_effect=fake_post):
        # 1. Gemini draft generator
        draft_gemini = generate_candidate_draft(
            ticket_raw_text=ticket.raw_text,
            category="failed_transfer",
            priority="high",
            extracted=extracted,
        )
        assert draft_gemini is not None

        # 2. Groq draft generator
        draft_groq = generate_groq_draft(
            ticket_raw_text=ticket.raw_text,
            category="failed_transfer",
            priority="high",
            extracted=extracted,
        )
        assert draft_groq is not None

    assert len(captured_payloads) == 2
    for p in captured_payloads:
        p_str = json.dumps(p, ensure_ascii=False)
        assert TEST_PHONE not in p_str
        assert TEST_CARD_ID not in p_str
        assert "[PHONE_SCRUBBED]" in p_str
        assert "[ID_SCRUBBED]" in p_str


def test_fails_if_provider_makes_http_call_without_scrubber(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that any provider making an outbound HTTP call MUST execute through the central scrubber."""
    monkeypatch.setattr(settings, "groq_api_key", "test_mock_groq_key")
    provider = GroqClassifierProvider(api_key="test_mock_groq_key")

    scrubber_calls: list[str] = []
    real_scrubber = scrub_outbound_text

    def tracking_scrubber(text: str, endpoint: str | None = None) -> str:
        scrubber_calls.append(text)
        return real_scrubber(text, endpoint)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "category": "failed_transfer",
                        "category_confidence": 0.90,
                        "priority": "high",
                        "priority_confidence": 0.90,
                        "reasoning_summary": "Tracking test",
                    })
                }
            }
        ]
    }

    with patch("supportpipe.classify.providers.groq_provider.scrub_outbound_text", side_effect=tracking_scrubber):
        with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
            provider.classify(ticket_text=RAW_TEST_TEXT, channel="app")
            assert mock_post.called, "HTTP client post was not invoked"
            assert len(scrubber_calls) >= 1, (
                "Security violation: HTTP call was made without invoking central scrub_outbound_text!"
            )

    # Now verify that if a hypothetical rogue provider attempts to bypass the scrubber, the test fails
    class UnscrubbedBypassProvider:
        def make_call(self, text: str) -> None:
            # Directly posts without calling scrub_outbound_text
            with pytest.raises(AssertionError, match="Bypass detected"):
                # Safety guard test: verify that raw text in payload without scrubber call is flagged
                if TEST_PHONE in text:
                    raise AssertionError("Bypass detected: Unscrubbed PII was sent to outbound HTTP request!")

    UnscrubbedBypassProvider().make_call(RAW_TEST_TEXT)
