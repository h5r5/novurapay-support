"""Unit tests for Local LLM Adapter with stdlib fake HTTP server on 127.0.0.1 (Task C3).

Verifies OpenAI-compatible /chat/completions interaction, strict JSON parsing and schema validation,
OWNER_CONFIRM enforcement, and disabled-by-default behavior.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest

from supportpipe.classify.providers.local_llm_provider import LocalLLMClassifierProvider
from supportpipe.config import ConfigError


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    """Stdlib HTTP handler serving OpenAI-compatible /chat/completions responses."""

    response_payload: dict[str, Any] = {}
    response_status: int = 200
    captured_requests: list[dict[str, Any]] = []

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            parsed_req = json.loads(body)
            self.__class__.captured_requests.append(parsed_req)
        except Exception:
            pass

        self.send_response(self.__class__.response_status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.__class__.response_payload).encode("utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        # Silence stdlib HTTP server request logging during tests
        pass


@pytest.fixture
def fake_openai_server() -> tuple[str, type[FakeOpenAIHandler]]:
    """Spins up a lightweight stdlib HTTPServer on 127.0.0.1 with an ephemeral port."""
    FakeOpenAIHandler.response_payload = {}
    FakeOpenAIHandler.response_status = 200
    FakeOpenAIHandler.captured_requests = []

    server = HTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
    host, port = server.server_address
    base_url = f"http://{host}:{port}/v1"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    yield base_url, FakeOpenAIHandler

    server.shutdown()
    server.server_close()


def test_local_llm_disabled_by_default_raises() -> None:
    """Local LLM adapter must be disabled by default and raise RuntimeError on call."""
    provider = LocalLLMClassifierProvider(enabled=False)
    with pytest.raises(RuntimeError) as exc:
        provider.classify("حولت فلوس وما وصلت")
    assert "disabled by default" in str(exc.value)


def test_local_llm_owner_confirm_model_raises_config_error() -> None:
    """Local LLM adapter must raise ConfigError if model is OWNER_CONFIRM."""
    provider = LocalLLMClassifierProvider(enabled=True, model="OWNER_CONFIRM")
    with pytest.raises(ConfigError) as exc:
        provider.classify("حولت فلوس وما وصلت")
    assert "OWNER_CONFIRM" in str(exc.value)


def test_local_llm_successful_classification(fake_openai_server: tuple[str, type[FakeOpenAIHandler]]) -> None:
    """Test full successful classification flow against stdlib HTTP server on 127.0.0.1."""
    base_url, handler = fake_openai_server
    handler.response_payload = {
        "id": "chatcmpl-test-01",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "category": "failed_transfer",
                        "category_confidence": 0.96,
                        "priority": "high",
                        "priority_confidence": 0.92,
                        "reasoning_summary": "Customer reported uncredited money transfer",
                        "sentiment_tags": ["urgent", "polite"],
                    }),
                },
            }
        ],
    }

    provider = LocalLLMClassifierProvider(
        base_url=base_url,
        model="custom-local-model",
        enabled=True,
    )

    res = provider.classify("حولت رصيد وما وصل للمستلم", channel="app")
    assert res.category == "failed_transfer"
    assert res.category_confidence == 0.96
    assert res.priority == "high"
    assert res.priority_confidence == 0.92
    assert "Customer reported" in res.reasoning_summary
    assert "urgent" in res.sentiment_tags
    assert res.degraded is False

    # Verify request payload sent to /chat/completions
    assert len(handler.captured_requests) == 1
    req = handler.captured_requests[0]
    assert req["model"] == "custom-local-model"
    assert req["temperature"] == 0.0


def test_local_llm_strips_markdown_code_fences(fake_openai_server: tuple[str, type[FakeOpenAIHandler]]) -> None:
    """Verifies that markdown code blocks (```json ... ```) are cleanly parsed."""
    base_url, handler = fake_openai_server
    fenced_json = "```json\n" + json.dumps({
        "category": "kyc_document_issue",
        "category_confidence": 0.88,
        "priority": "medium",
        "priority_confidence": 0.85,
        "reasoning_summary": "KYC document issue",
        "sentiment_tags": [],
    }) + "\n```"

    handler.response_payload = {
        "choices": [{"message": {"role": "assistant", "content": fenced_json}}]
    }

    provider = LocalLLMClassifierProvider(
        base_url=base_url,
        model="custom-local-model",
        enabled=True,
    )
    res = provider.classify("رفضوا هويتي بتوثيق الحساب", channel="app")
    assert res.category == "kyc_document_issue"
    assert res.priority == "medium"


def test_local_llm_strict_json_rejection_on_invalid_syntax(
    fake_openai_server: tuple[str, type[FakeOpenAIHandler]],
) -> None:
    """Non-JSON response text must raise ValueError."""
    base_url, handler = fake_openai_server
    handler.response_payload = {
        "choices": [{"message": {"role": "assistant", "content": "I apologize, but I am unable to help."}}]
    }

    provider = LocalLLMClassifierProvider(
        base_url=base_url,
        model="custom-local-model",
        enabled=True,
    )
    with pytest.raises(ValueError) as exc:
        provider.classify("عندي مشكلة بالبطاقة")
    assert "non-JSON" in str(exc.value)


def test_local_llm_missing_fields_rejection(fake_openai_server: tuple[str, type[FakeOpenAIHandler]]) -> None:
    """Missing required schema fields must raise ValueError."""
    base_url, handler = fake_openai_server
    handler.response_payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    # Missing category_confidence
                    "content": json.dumps({"category": "failed_transfer", "priority": "high"}),
                }
            }
        ]
    }

    provider = LocalLLMClassifierProvider(
        base_url=base_url,
        model="custom-local-model",
        enabled=True,
    )
    with pytest.raises(ValueError) as exc:
        provider.classify("مشكلة بالرصيد")
    assert "missing required field" in str(exc.value)


def test_local_llm_invalid_priority_rejection(fake_openai_server: tuple[str, type[FakeOpenAIHandler]]) -> None:
    """Invalid priority value outside ('high', 'medium', 'low') must raise ValueError."""
    base_url, handler = fake_openai_server
    handler.response_payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "category": "failed_transfer",
                        "category_confidence": 0.90,
                        "priority": "catastrophic",
                        "priority_confidence": 0.80,
                    }),
                }
            }
        ]
    }

    provider = LocalLLMClassifierProvider(
        base_url=base_url,
        model="custom-local-model",
        enabled=True,
    )
    with pytest.raises(ValueError) as exc:
        provider.classify("مشكلة بالرصيد")
    assert "Invalid priority" in str(exc.value)


def test_local_llm_unknown_category_falls_back_to_unclear(
    fake_openai_server: tuple[str, type[FakeOpenAIHandler]],
) -> None:
    """Unrecognized category ID safely falls back to 'unclear_or_incomplete'."""
    base_url, handler = fake_openai_server
    handler.response_payload = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "category": "completely_invented_category_xyz",
                        "category_confidence": 0.90,
                        "priority": "low",
                        "priority_confidence": 0.80,
                    }),
                }
            }
        ]
    }

    provider = LocalLLMClassifierProvider(
        base_url=base_url,
        model="custom-local-model",
        enabled=True,
    )
    res = provider.classify("رسالة مبهمة")
    assert res.category == "unclear_or_incomplete"
