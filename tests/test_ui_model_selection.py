"""Tests for Dynamic Model Selection, Runtime API Overrides, and Connection Testing."""

from unittest.mock import MagicMock, patch

import streamlit as st

from supportpipe.classify.classify import get_classifier_provider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.pipeline import run_batch
from supportpipe.schemas import Ticket
from supportpipe.ui.engine_settings import (
    ENGINE_OPTIONS,
    INITIAL_ENV_KEYS,
    get_key_status,
    ping_engine_connection,
    resolve_engine_choice,
    sync_runtime_settings,
)


def test_engine_options_contains_all_required_engines() -> None:
    """Verify ENGINE_OPTIONS contains all 7 specified engines."""
    options_text = " ".join(ENGINE_OPTIONS)
    assert "Groq Llama 3.3 70B" in options_text
    assert "Groq Llama 3.1 8B" in options_text
    assert "Gemini 2.5 Flash" in options_text
    assert "TypeSafe Jev 1.13" in options_text
    assert "Hybrid" in options_text
    assert "Mock" in options_text
    assert "Dual" in options_text or "مبارزة" in options_text


def test_resolve_engine_choice_mapping() -> None:
    """Verify resolve_engine_choice correctly resolves each engine option."""
    # 1. Groq 70B
    res_70b = resolve_engine_choice("⚡ Groq Llama 3.3 70B Versatile (سحابي عالي الدقة)")
    assert res_70b["provider"] == "groq"
    assert res_70b["model"] == "llama-3.3-70b-versatile"

    # 2. Groq 8B
    res_8b = resolve_engine_choice("⚡ Groq Llama 3.1 8B Instant (فائق السرعة)")
    assert res_8b["provider"] == "groq"
    assert res_8b["model"] == "llama-3.1-8b-instant"

    # 3. Gemini 2.5 Flash
    res_gem = resolve_engine_choice("🌐 Google Gemini 2.5 Flash (سحابي وتدقيق)")
    assert res_gem["provider"] == "gemini"
    assert res_gem["model"] == "gemini-2.5-flash"

    # 4. TypeSafe Jev 1.13 API
    res_jev = resolve_engine_choice("🧠 TypeSafe Jev 1.13 API (نموذج معاير عراقي)")
    assert res_jev["provider"] == "jev"
    assert res_jev["model"] == "jev-latest"

    # 5. Tiered Hybrid Waterfall
    res_hyb = resolve_engine_choice("🔄 Tiered Hybrid Waterfall (الهجين المتسلسل)")
    assert res_hyb["provider"] == "hybrid"

    # 6. Local Fast Heuristic / Mock
    res_mock = resolve_engine_choice("💻 Local Fast Heuristic / Mock (محلي 0.5ms)")
    assert res_mock["provider"] == "mock"

    # 7. Side-by-Side Dual Engine Match
    res_duel = resolve_engine_choice("⚔️ Side-by-Side Dual Engine Match (مبارزة ثنائية)")
    assert res_duel["provider"] == "duel"


def test_sync_runtime_settings_overrides() -> None:
    """Verify sync_runtime_settings dynamically copies session state overrides to settings."""
    orig_groq = settings.groq_api_key
    orig_gemini = settings.gemini_api_key
    orig_jev = settings.jev_api_key
    orig_th = settings.category_confidence_threshold

    try:
        st.session_state["groq_key_input"] = "gsk_test_override_key_123"
        st.session_state["gemini_key_input"] = "AIzaSy_test_override_key_456"
        st.session_state["jev_key_input"] = "jev_sec_test_override_key_789"
        st.session_state["conf_threshold_input"] = 0.85

        sync_runtime_settings()

        assert settings.groq_api_key == "gsk_test_override_key_123"
        assert settings.gemini_api_key == "AIzaSy_test_override_key_456"
        assert settings.jev_api_key == "jev_sec_test_override_key_789"
        assert settings.typesafe_api_key == "jev_sec_test_override_key_789"
        assert settings.category_confidence_threshold == 0.85
    finally:
        settings.groq_api_key = orig_groq
        settings.gemini_api_key = orig_gemini
        settings.jev_api_key = orig_jev
        settings.typesafe_api_key = orig_jev
        settings.category_confidence_threshold = orig_th
        st.session_state.pop("groq_key_input", None)
        st.session_state.pop("gemini_key_input", None)
        st.session_state.pop("jev_key_input", None)
        st.session_state.pop("conf_threshold_input", None)


def test_ping_engine_connection_mock_and_hybrid() -> None:
    """Verify ping_engine_connection works for local mock and hybrid."""
    ok_mock, lat_mock, msg_mock = ping_engine_connection("mock")
    assert ok_mock is True
    assert lat_mock >= 0.0
    assert "المحرك المحلي" in msg_mock

    ok_hyb, lat_hyb, msg_hyb = ping_engine_connection("hybrid")
    assert ok_hyb is True
    assert lat_hyb >= 0.0


def test_ping_engine_connection_missing_keys_handled_gracefully() -> None:
    """Verify ping_engine_connection returns False with helpful message when keys are missing."""
    with patch.object(settings, "groq_api_key", ""):
        ok, lat, msg = ping_engine_connection("groq", api_key="")
        assert ok is False
        assert "GROQ_API_KEY غير متوفر" in msg

    with patch.object(settings, "gemini_api_key", ""):
        ok, lat, msg = ping_engine_connection("gemini", api_key="")
        assert ok is False
        assert "GEMINI_API_KEY غير متوفر" in msg

    with patch.object(settings, "jev_api_key", ""):
        with patch.object(settings, "typesafe_api_key", ""):
            ok, lat, msg = ping_engine_connection("jev", api_key="")
            assert ok is False
            assert "JEV_API_KEY غير متوفر" in msg


def test_ping_engine_connection_with_mocked_groq_success() -> None:
    """Verify ping_engine_connection handles Groq response properly."""
    mock_provider = MagicMock()
    mock_res = MagicMock()
    mock_res.category = "failed_transfer"
    mock_provider.classify.return_value = mock_res

    with patch("supportpipe.ui.engine_settings.GroqClassifierProvider", return_value=mock_provider):
        ok, lat, msg = ping_engine_connection("groq", api_key="test_key", model="llama-3.3-70b-versatile")
        assert ok is True
        assert lat >= 0.0
        assert "تم الاتصال بنجاح بمزود Groq" in msg
        assert "failed_transfer" in msg


def test_ping_engine_connection_with_mocked_gemini_success() -> None:
    """Verify ping_engine_connection handles Gemini response properly."""
    mock_provider = MagicMock()
    mock_res = MagicMock()
    mock_res.category = "app_login_issue"
    mock_provider.classify.return_value = mock_res

    with patch("supportpipe.ui.engine_settings.GeminiClassifierProvider", return_value=mock_provider):
        ok, lat, msg = ping_engine_connection("gemini", api_key="test_gemini_key", model="gemini-2.5-flash")
        assert ok is True
        assert lat >= 0.0
        assert "تم الاتصال بنجاح بمزود Gemini" in msg
        assert "app_login_issue" in msg


def test_batch_execution_with_dynamic_provider() -> None:
    """Verify run_batch works with dynamic provider_override."""
    sample_tickets = [
        Ticket(
            ticket_id="TKT-DYN-01",
            raw_text="حولت 50 الف وما وصلت امس برقم TXN-12345678",
            channel="app",
            submitted_at="2026-09-22T14:30:00+03:00",
            synthetic_user_id="USR-DYN-01",
        ),
        Ticket(
            ticket_id="TKT-DYN-02",
            raw_text="البصمة ما تشتغل والمحفظة قافلة",
            channel="sms",
            submitted_at="2026-09-22T14:32:00+03:00",
            synthetic_user_id="USR-DYN-02",
        ),
    ]

    # Test with mock override
    results, summary = run_batch(sample_tickets, provider_override="mock")
    assert len(results) == 2
    assert summary.total_tickets == 2
    assert results[0].ticket_id == "TKT-DYN-01"
    assert "mock" in results[0].provider_path

    # Test with hybrid override
    results_hyb, summary_hyb = run_batch(sample_tickets, provider_override="hybrid")
    assert len(results_hyb) == 2
    assert summary_hyb.total_tickets == 2


def test_get_key_status_env_vs_session_vs_unspecified() -> None:
    """Verify get_key_status correctly distinguishes session overrides, env keys, and unspecified keys."""
    # 1. Unspecified
    with patch.dict(INITIAL_ENV_KEYS, {"groq": ""}, clear=False):
        with patch.object(settings, "groq_api_key", ""):
            st.session_state.pop("groq_key_input", None)
            key, label, cls = get_key_status("groq")
            assert key == ""
            assert label == "⚪ غير محدد"
            assert cls == "tag-escalate"

    # 2. .env configured
    with patch.dict(INITIAL_ENV_KEYS, {"groq": "gsk_env_configured_key"}, clear=False):
        with patch.object(settings, "groq_api_key", "gsk_env_configured_key"):
            st.session_state.pop("groq_key_input", None)
            key, label, cls = get_key_status("groq")
            assert key == "gsk_env_configured_key"
            assert label == "🔵 .env"
            assert cls == "tag-review"

    # 3. Session override
    with patch.dict(INITIAL_ENV_KEYS, {"groq": "gsk_env_configured_key"}, clear=False):
        st.session_state["groq_key_input"] = "gsk_session_override_new"
        try:
            key, label, cls = get_key_status("groq")
            assert key == "gsk_session_override_new"
            assert label == "🟢 جلسة"
            assert cls == "tag-auto"
        finally:
            st.session_state.pop("groq_key_input", None)


def test_get_classifier_provider_respects_explicit_provider_even_in_offline_mode() -> None:
    """Verify get_classifier_provider does NOT force Mock when provider is explicitly requested."""
    orig_mode = settings.llm_mode
    orig_gem = settings.gemini_api_key
    orig_jev = settings.jev_api_key
    orig_groq = settings.groq_api_key

    try:
        settings.llm_mode = "offline"
        settings.gemini_api_key = "AIzaSy_test_key"
        settings.jev_api_key = "jev_test_key"
        settings.groq_api_key = "gsk_test_key"

        # Explicit gemini
        p_gem = get_classifier_provider("gemini")
        assert isinstance(p_gem, GeminiClassifierProvider)

        # Explicit jev
        p_jev = get_classifier_provider("jev")
        assert isinstance(p_jev, JevClassifierProvider)

        # Explicit groq
        p_groq = get_classifier_provider("groq")
        assert isinstance(p_groq, GroqClassifierProvider)

        # Explicit mock
        p_mock = get_classifier_provider("mock")
        assert isinstance(p_mock, MockClassifierProvider)

        # Implicit (None) -> Respects offline mode
        p_default = get_classifier_provider(None)
        assert isinstance(p_default, MockClassifierProvider)
    finally:
        settings.llm_mode = orig_mode
        settings.gemini_api_key = orig_gem
        settings.jev_api_key = orig_jev
        settings.groq_api_key = orig_groq


def test_batch_execution_with_gemini_and_groq_providers() -> None:
    """Verify run_batch dispatches to Groq and Gemini when provider_override is specified."""
    sample_tickets = [
        Ticket(
            ticket_id="TKT-DYN-03",
            raw_text="حولت 100 الف برقم TXN-55443322",
            channel="app",
            submitted_at="2026-09-22T14:30:00+03:00",
            synthetic_user_id="USR-DYN-03",
        ),
    ]

    mock_gemini = MagicMock()
    mock_res_gem = MagicMock()
    mock_res_gem.category = "failed_transfer"
    mock_res_gem.category_confidence = 0.98
    mock_res_gem.priority = "high"
    mock_res_gem.priority_confidence = 0.95
    mock_res_gem.reasoning_summary = "Mock Gemini Classification"
    mock_res_gem.audit_details = None
    mock_res_gem.sentiment_tags = ["urgent"]
    mock_gemini.classify.return_value = mock_res_gem

    with patch.object(settings, "gemini_api_key", "test_gemini_key"):
        with patch.object(GeminiClassifierProvider, "classify", return_value=mock_res_gem):
            results, summary = run_batch(sample_tickets, provider_override="gemini")
            assert len(results) == 1
            assert summary.total_tickets == 1
            assert "gemini" in results[0].provider_path


def test_safe_html_escapes_xss_vectors() -> None:
    """Verify safe_html neutralizes script injection, tags, and handles None."""
    from supportpipe.ui.app import safe_html

    assert safe_html("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert safe_html("Hello & World <foo>") == "Hello &amp; World &lt;foo&gt;"
    assert safe_html(None) == ""
    assert safe_html(12345) == "12345"


