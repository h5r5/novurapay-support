"""Tests for base project scaffolding, configuration, and health checks."""

from click.testing import CliRunner

from supportpipe import __version__
from supportpipe.cli import main
from supportpipe.config import settings


def test_version_exists() -> None:
    """Verify package exposes a semver version string."""
    assert __version__ == "0.1.0"


def test_default_settings() -> None:
    """Verify default configuration values."""
    assert settings.llm_mode in ["live", "cached", "offline"]
    assert 0.0 < settings.category_confidence_threshold < 1.0
    assert 0.0 < settings.priority_confidence_threshold < 1.0


def test_cli_health_check() -> None:
    """Verify CLI health command runs successfully."""
    runner = CliRunner()
    result = runner.invoke(main, ["health"])
    assert result.exit_code == 0
    assert "Health check status: OK" in result.output
    assert "Execution Mode:" in result.output
