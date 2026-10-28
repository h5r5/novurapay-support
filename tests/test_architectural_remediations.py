"""Comprehensive architectural remediation regression tests.

Verifies:
1. Zero data leakage between dev and test splits.
2. Gemini header authentication (no sensitive keys exposed in request URLs).
3. 429 Circuit breaker fast-failure without slow sleep loops.
4. Groq provider classification and error handling.
5. Pydantic accepts LLM_MODE=hybrid.
6. PII masking of phone numbers and escalation reasons in results.jsonl.
7. Scoped transaction reference deduplication (distinct users sharing transaction ref are not duplicates).
8. Drafting quota preservation in hybrid mode.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from supportpipe.classify.classify import get_classifier_provider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import (
    GroqClassifierProvider,
    generate_groq_draft,
)
from supportpipe.classify.providers.hybrid_provider import HybridClassifierProvider
from supportpipe.config import Settings, settings
from supportpipe.datagen.splits import compute_sha256
from supportpipe.draft.generator import generate_candidate_draft
from supportpipe.logging_store import ReviewQueueStore
from supportpipe.pipeline import process_ticket, run_batch
from supportpipe.schemas import (
    BatchSummary,
    ClassificationResult,
    ExtractedFields,
    LabeledTicket,
    PipelineResult,
    Ticket,
)


def test_zero_data_leakage_between_splits() -> None:
    """Verify strictly 0% data leakage between dev.jsonl and test.jsonl."""
    dev_path = settings.data_dir / "splits" / "dev.jsonl"
    test_path = settings.data_dir / "splits" / "test.jsonl"
    manifest_path = settings.data_dir / "manifest.json"

    assert dev_path.exists(), f"Dev split missing at {dev_path}"
    assert test_path.exists(), f"Test split missing at {test_path}"
    assert manifest_path.exists(), f"Manifest missing at {manifest_path}"

    dev_texts: set[str] = set()
    with open(dev_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = LabeledTicket.model_validate_json(line)
                dev_texts.add(item.ticket.raw_text.strip())

    test_texts: set[str] = set()
    with open(test_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                item = LabeledTicket.model_validate_json(line)
                test_texts.add(item.ticket.raw_text.strip())

    overlap = dev_texts.intersection(test_texts)
    assert len(overlap) == 0, f"Data leakage detected! {len(overlap)} overlapping tickets: {overlap}"

    # Verify manifest integrity
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    assert compute_sha256(dev_path) == manifest["splits"]["dev"]["sha256"]
    assert compute_sha256(test_path) == manifest["splits"]["test"]["sha256"]
    assert "handwritten" in manifest["splits"]
    assert manifest["splits"]["handwritten"]["count"] == 20


def test_gemini_header_auth_no_url_key() -> None:
    """Verify Gemini provider and draft generator pass API key in header, not in URL."""
    provider = GeminiClassifierProvider(api_key="test_secret_gemini_key_12345")
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
                                "reasoning_summary": "Test classified",
                            })
                        }
                    ]
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        res = provider.classify("حولت فلوس وما وصلت", channel="app")
        assert res.category == "failed_transfer"

        # Verify request parameters
        called_args, called_kwargs = mock_post.call_args
        called_url = called_args[0]
        called_headers = called_kwargs.get("headers", {})

        assert "key=" not in called_url, f"API key leaked in URL: {called_url}"
        assert called_headers.get("x-goog-api-key") == "test_secret_gemini_key_12345"

    # Test candidate drafting does not leak in URL
    with patch.object(settings, "gemini_api_key", "test_secret_draft_key"):
        with patch.object(settings, "llm_mode", "live"):
            with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
                GeminiClassifierProvider.reset_circuit_breaker()
                generate_candidate_draft(
                    ticket_raw_text="حولت 50 الف وما وصلت",
                    category="failed_transfer",
                    priority="high",
                    extracted=ExtractedFields(amount_iqd=50000),
                )
                called_args, called_kwargs = mock_post.call_args
                called_url = called_args[0]
                called_headers = called_kwargs.get("headers", {})
                assert "key=" not in called_url
                assert called_headers.get("x-goog-api-key") == "test_secret_draft_key"


def test_gemini_429_circuit_breaker_tripping() -> None:
    """Verify 429 response trips circuit breaker and triggers fast-fail on subsequent calls."""
    GeminiClassifierProvider.reset_circuit_breaker()
    assert GeminiClassifierProvider._circuit_open is False

    provider = GeminiClassifierProvider(api_key="mock_key")
    req = httpx.Request("POST", "https://generativelanguage.googleapis.com")
    resp_429 = httpx.Response(429, request=req, content=b'{"error": "Resource exhausted"}')

    with patch("httpx.Client.post", return_value=resp_429):
        with pytest.raises(httpx.HTTPStatusError):
            provider.classify("حولت فلوس وما وصلت", channel="app")

    # Circuit breaker must now be open
    assert GeminiClassifierProvider._circuit_open is True

    # Subsequent call must fast-fail with RuntimeError immediately without HTTP call
    with patch("httpx.Client.post") as mock_post:
        with pytest.raises(RuntimeError, match="CIRCUIT_BREAKER"):
            provider.classify("حولت فلوس وما وصلت", channel="app")
        mock_post.assert_not_called()

    # Draft candidate generator must also fast-fail (return None) immediately
    with patch.object(settings, "llm_mode", "live"):
        with patch.object(settings, "gemini_api_key", "mock_key"):
            draft = generate_candidate_draft(
                ticket_raw_text="حولت 50 الف",
                category="failed_transfer",
                priority="high",
                extracted=ExtractedFields(),
            )
            assert draft is None

    # Reset circuit breaker
    GeminiClassifierProvider.reset_circuit_breaker()
    assert GeminiClassifierProvider._circuit_open is False


def test_groq_provider_classification_and_circuit_breaker() -> None:
    """Verify GroqClassifierProvider handles requests, JSON responses, and 429 circuit breaker."""
    GroqClassifierProvider.reset_circuit_breaker()
    provider = GroqClassifierProvider(api_key="test_groq_key_999")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "category": "card_issue",
                        "category_confidence": 0.94,
                        "priority": "high",
                        "priority_confidence": 0.91,
                        "reasoning_summary": "ATM swallowed physical card",
                        "sentiment_tags": ["urgent"],
                    })
                }
            }
        ]
    }

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        res = provider.classify("الصراف الآلي بلع الكارت مالتي", channel="app")
        assert res.category == "card_issue"
        assert res.category_confidence == 0.94
        assert res.priority == "high"

        called_args, called_kwargs = mock_post.call_args
        assert called_args[0] == "https://api.groq.com/openai/v1/chat/completions"
        assert called_kwargs["headers"]["Authorization"] == "Bearer test_groq_key_999"

    # Test Groq draft generation
    with patch.object(settings, "groq_api_key", "test_groq_key_999"):
        mock_draft_resp = MagicMock()
        mock_draft_resp.status_code = 200
        mock_draft_resp.json.return_value = {
            "choices": [{"message": {"content": "أهلاً بك، تم استلام طلبك وبخصوص الكارت سيتم إيقافه فوراً."}}]
        }
        with patch("httpx.Client.post", return_value=mock_draft_resp):
            draft = generate_groq_draft(
                ticket_raw_text="الصراف بلع الكارت",
                category="card_issue",
                priority="high",
                extracted=ExtractedFields(),
            )
            assert draft is not None
            assert "الكارت" in draft

    # Test Groq 429 circuit breaker
    req = httpx.Request("POST", "https://api.groq.com/openai/v1/chat/completions")
    resp_429 = httpx.Response(429, request=req, content=b'{"error": "rate limit"}')

    with patch("httpx.Client.post", return_value=resp_429):
        with pytest.raises(httpx.HTTPStatusError):
            provider.classify("الصراف بلع الكارت", channel="app")

    assert GroqClassifierProvider._circuit_open is True

    # Fast-fail check
    with patch("httpx.Client.post") as mock_post:
        with pytest.raises(RuntimeError, match="CIRCUIT_BREAKER"):
            provider.classify("الصراف بلع الكارت", channel="app")
        mock_post.assert_not_called()

    GroqClassifierProvider.reset_circuit_breaker()


def test_config_accepts_hybrid_mode() -> None:
    """Verify Settings accepts LLM_MODE=hybrid without Pydantic validation error."""
    conf = Settings(llm_mode="hybrid")
    assert conf.llm_mode == "hybrid"

    # Verify get_classifier_provider returns HybridClassifierProvider
    with patch.object(settings, "llm_mode", "hybrid"):
        prov = get_classifier_provider("hybrid")
        assert isinstance(prov, HybridClassifierProvider)


def test_pii_masking_in_persisted_results_jsonl(tmp_path: Path) -> None:
    """Verify phone numbers and escalation reasons are strictly masked when saved to results.jsonl."""
    store = ReviewQueueStore(storage_dir=tmp_path)
    result = PipelineResult(
        ticket_id="TKT-PII-01",
        category="wrong_recipient",
        category_confidence=0.9,
        priority="high",
        priority_confidence=0.88,
        extracted_fields=ExtractedFields(
            phone_number="07801122334",
            transaction_ref="TXN-12345678",
            amount_iqd=50000,
        ),
        team="Payments & Transfers",
        escalated=True,
        escalation_reason="Customer transferred 50,000 to wrong phone 07801122334 by mistake",
        draft_reply="يرجى مراجعة رقمك 07801122334 مع الدعم",
        provider_path="mock",
        reasoning_summary="Classified via mock",
        latency_ms=1.2,
        urgency_level="high",
    )
    summary = BatchSummary(
        run_id="run_test_pii",
        processed_at="2026-10-16T19:00:00+03:00",
        total_tickets=1,
        escalated_count=1,
        escalation_rate_pct=100.0,
        category_counts={"wrong_recipient": 1},
        priority_counts={"high": 1},
        team_counts={"Payments & Transfers": 1},
        escalation_reasons={"test": 1},
        avg_latency_ms=1.2,
        total_wall_clock_ms=1.2,
    )

    saved_dir = store.save_run(run_id="run_test_pii", results=[result], summary=summary)
    results_file = saved_dir / "results.jsonl"
    assert results_file.exists()

    with open(results_file, encoding="utf-8") as f:
        content = f.read()

    # Raw phone number MUST NOT be present in plain text anywhere in the persisted record
    assert "07801122334" not in content, "Raw phone number leaked into persisted results.jsonl!"
    assert "[PHONE_SCRUBBED]" in content


def test_scoped_deduplication_two_users_same_ref() -> None:
    """Verify two distinct users referencing the same transaction reference are NOT falsely marked as duplicates."""
    # User A (Sender) and User B (Recipient) both open tickets regarding TXN-99881122
    t1 = Ticket(
        ticket_id="TKT-SENDER-01",
        channel="app",
        raw_text="حولت 50 الف وما وصلت لصاحبي ورقم العملية TXN-99881122 البارحة",
        submitted_at="2026-09-22T10:00:00+03:00",
        synthetic_user_id="USR-SENDER",
    )
    t2 = Ticket(
        ticket_id="TKT-RECIPIENT-01",
        channel="app",
        raw_text="صديقي حوللي 50 الف برقم مرجع TXN-99881122 ولهسة ما استلمت شي بالحساب",
        submitted_at="2026-09-22T10:05:00+03:00",
        synthetic_user_id="USR-RECIPIENT",
    )

    results, summary = run_batch([t1, t2])
    assert len(results) == 2
    # Neither should be marked as duplicate
    assert not any("duplicate" in (r.escalation_reason or "").lower() for r in results)

    # Now User A sends another duplicate ticket with the same reference
    t3 = Ticket(
        ticket_id="TKT-SENDER-02",
        channel="app",
        raw_text="وين وصلت الحوالة رقم TXN-99881122 شوكت ترجع؟",
        submitted_at="2026-09-22T10:15:00+03:00",
        synthetic_user_id="USR-SENDER",
    )
    results_with_dup, _ = run_batch([t1, t2, t3])
    assert len(results_with_dup) == 3
    # t3 from USR-SENDER must be flagged as duplicate
    assert results_with_dup[2].escalated is True
    assert "duplicate" in (results_with_dup[2].escalation_reason or "").lower()


def test_drafting_quota_preservation_in_hybrid_mode() -> None:
    """Verify that in hybrid mode with local consensus, Gemini is NOT invoked for drafting."""
    t = Ticket(
        ticket_id="TKT-HYBRID-DRAFT",
        channel="app",
        raw_text="حولت مبلغ 50,000 دينار لصديقي وما وصل ورقم العملية TXN-12345678 امس بالليل",
        submitted_at="2026-09-22T12:00:00+03:00",
        synthetic_user_id="USR-DRAFT-01",
    )

    with patch.object(settings, "llm_mode", "hybrid"):
        with patch.object(settings, "gemini_api_key", "mock_gemini_key"):
            with patch.object(settings, "jev_api_key", "mock_jev_key"):
                with patch.object(settings, "typesafe_api_key", ""):
                    with patch(
                        "supportpipe.classify.providers.jev_provider.JevClassifierProvider.classify"
                    ) as mock_jev_classify:
                        mock_jev_classify.return_value = ClassificationResult(
                            category="failed_transfer",
                            category_confidence=0.92,
                            priority="high",
                            priority_confidence=0.90,
                            reasoning_summary="Waterfall Consensus (System 1 + Jev 1.13) on 'failed_transfer'",
                        )
                        with patch("supportpipe.draft.generator.generate_candidate_draft") as mock_gemini_draft:
                            res = process_ticket(t)
                            # In hybrid mode without groq or audit draft, candidate drafting should bypass Gemini
                            mock_gemini_draft.assert_not_called()
                            assert res.draft_reply is not None
                            assert "فريق التحويلات" in res.draft_reply
