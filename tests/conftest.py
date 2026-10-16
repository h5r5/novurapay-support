"""Pytest test configuration and fixtures."""

from collections.abc import Generator

import pytest

from supportpipe.config import Settings


@pytest.fixture(autouse=True)
def force_offline_mode_for_unit_tests(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[None, None, None]:
    """Force offline mock mode during unit testing to prevent API quota consumption."""
    from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
    from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
    from supportpipe.config import settings

    GeminiClassifierProvider.reset_circuit_breaker()
    GroqClassifierProvider.reset_circuit_breaker()
    monkeypatch.setattr(settings, "llm_mode", "offline")
    yield
    GeminiClassifierProvider.reset_circuit_breaker()
    GroqClassifierProvider.reset_circuit_breaker()


@pytest.fixture
def mock_settings(tmp_path: pytest.TempPathFactory) -> Settings:
    """Fixture returning settings with temporary directory paths."""
    base_dir = tmp_path.mktemp("supportpipe_test")
    return Settings(
        llm_mode="offline",
        project_root=base_dir,
        data_dir=base_dir / "data",
        results_dir=base_dir / "results",
    )
