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


def test_compute_bootstrap_confidence_intervals() -> None:
    """Verify bootstrap confidence interval calculation on sample predictions."""
    from supportpipe.evaluation.metrics import compute_bootstrap_confidence_intervals

    y_true = ["failed_transfer", "card_issue", "failed_transfer", "fraud_report"]
    y_pred = ["failed_transfer", "failed_transfer", "failed_transfer", "fraud_report"]
    escalated = [False, True, False, False]
    labels = ["failed_transfer", "card_issue", "fraud_report"]

    ci = compute_bootstrap_confidence_intervals(
        y_true=y_true,
        y_pred=y_pred,
        escalated_flags=escalated,
        labels=labels,
        n_resamples=50,
        confidence_level=0.95,
        random_seed=42,
    )

    assert "overall_accuracy" in ci
    assert "macro_f1" in ci
    assert "auto_handled_accuracy" in ci
    assert ci["overall_accuracy"]["point_estimate"] == 0.75
    assert ci["auto_handled_accuracy"]["point_estimate"] == 1.0
    assert 0.0 <= ci["overall_accuracy"]["lower_ci"] <= ci["overall_accuracy"]["upper_ci"] <= 1.0

