"""Pytest test configuration and fixtures."""

from collections.abc import Generator

import pytest

from supportpipe.config import Settings


@pytest.fixture(autouse=True)
def force_offline_mode_for_unit_tests(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[None, None, None]:
    """Force offline mock mode during unit testing to prevent API quota consumption."""
    from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
    from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
    from supportpipe.config import settings
    from supportpipe.learning_store import discrepancy_store

    test_disc = tmp_path_factory.mktemp("audit_store") / "discrepancies.jsonl"
    monkeypatch.setattr(settings, "discrepancy_store_path", test_disc)
    monkeypatch.setattr(discrepancy_store, "file_path", test_disc)

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
