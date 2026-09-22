"""Pytest test configuration and fixtures."""

import pytest

from supportpipe.config import Settings


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
