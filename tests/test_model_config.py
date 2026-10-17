"""Unit tests for Model ID configuration and OWNER_CONFIRM sentinel enforcement (Task C2).

Verifies that one model id per role is loaded from config, the OWNER_CONFIRM sentinel
raises ConfigError at call time, and the legacy hardcoded default at draft/generator.py is removed.
"""

from __future__ import annotations

import inspect

import pytest

from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
from supportpipe.config import ConfigError, settings
from supportpipe.draft.generator import generate_candidate_draft
from supportpipe.schemas import ExtractedFields


def test_model_id_per_role_defaults() -> None:
    """Verify that roles have distinct model IDs and classification/local LLM wait for owner confirmation."""
    assert settings.gemini_flash_model == "gemini-2.5-flash"
    assert settings.gemini_flash_lite_model == "OWNER_CONFIRM"
    assert settings.groq_model == "llama-3.3-70b-versatile"
    assert settings.local_llm_model == "OWNER_CONFIRM"


def test_gemini_owner_confirm_raises_config_error() -> None:
    """GeminiClassifierProvider must raise ConfigError at call time if model is OWNER_CONFIRM."""
    provider = GeminiClassifierProvider(api_key="mock_key", model="OWNER_CONFIRM")
    with pytest.raises(ConfigError) as exc:
        provider.classify("حولت فلوس وما وصلت")
    assert "OWNER_CONFIRM" in str(exc.value)


def test_groq_owner_confirm_raises_config_error() -> None:
    """GroqClassifierProvider must raise ConfigError at call time if model is OWNER_CONFIRM."""
    provider = GroqClassifierProvider(api_key="mock_key", model="OWNER_CONFIRM")
    with pytest.raises(ConfigError) as exc:
        provider.classify("حولت فلوس وما وصلت")
    assert "OWNER_CONFIRM" in str(exc.value)


def test_draft_generator_owner_confirm_raises_config_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Draft generator must raise ConfigError at call time if gemini_flash_model is OWNER_CONFIRM."""
    monkeypatch.setattr(settings, "llm_mode", "live")
    monkeypatch.setattr(settings, "gemini_api_key", "test_key")
    monkeypatch.setattr(settings, "gemini_flash_model", "OWNER_CONFIRM")
    monkeypatch.setattr(settings, "gemini_model", "OWNER_CONFIRM")

    extracted = ExtractedFields(amount_iqd=50000)
    with pytest.raises(ConfigError) as exc:
        generate_candidate_draft(
            ticket_raw_text="حولت 50000 وماراحت",
            category="failed_transfer",
            priority="high",
            extracted=extracted,
        )
    assert "OWNER_CONFIRM" in str(exc.value)


def test_draft_generator_has_no_hardcoded_gemini_1_5_fallback() -> None:
    """Verify that the legacy default at draft/generator.py has been completely removed."""
    import supportpipe.draft.generator as gen_mod

    source = inspect.getsource(gen_mod.generate_candidate_draft)
    assert "gemini-1.5-flash" not in source, "Legacy hardcoded 'gemini-1.5-flash' default must not exist in generator"
