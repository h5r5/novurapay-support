"""Tests for DiscrepancyStore isolation, safe file locations, and missing file/dir tolerance (Task 2.8)."""

from __future__ import annotations

from pathlib import Path

import pytest

from supportpipe.config import settings
from supportpipe.learning_store import DiscrepancyStore, discrepancy_store


def is_path_inside_repo(path: Path) -> bool:
    """Check if a path resolves inside the project repository root."""
    try:
        path.resolve().relative_to(settings.project_root.resolve())
        return True
    except ValueError:
        return False


def test_discrepancy_store_path_does_not_resolve_inside_repo_during_tests() -> None:
    """Verify that in test runs, the discrepancy store file path is strictly isolated outside the repo."""
    active_path = discrepancy_store.file_path
    assert not is_path_inside_repo(active_path), (
        f"Security violation: discrepancy store path {active_path} resolves inside repository root {settings.project_root}"
    )


def test_store_path_safety_check_fails_when_path_resolves_inside_repo() -> None:
    """Demonstrate that an assertion fails when the store path resolves inside the repository."""
    inside_repo_path = settings.project_root / "data" / "audit_learning" / "discrepancies.jsonl"
    assert is_path_inside_repo(inside_repo_path) is True

    # This test proves that any guard or assertion asserting isolation fails when pointing inside the repo
    with pytest.raises(AssertionError, match="resolves inside repository"):
        assert not is_path_inside_repo(inside_repo_path), (
            f"Expected failure: store path {inside_repo_path} resolves inside repository"
        )


def test_discrepancy_store_tolerates_missing_file_and_directory(tmp_path: Path) -> None:
    """Verify that DiscrepancyStore gracefully tolerates missing files and directories."""
    missing_dir = tmp_path / "deep" / "non_existent_folder"
    missing_file = missing_dir / "audit_discrepancies.jsonl"

    assert not missing_dir.exists()
    assert not missing_file.exists()

    # Initialization auto-creates parent directory
    store = DiscrepancyStore(store_path=missing_file)
    assert missing_dir.exists()
    assert not missing_file.exists()

    # Loading from non-existent file returns empty list without error
    records = store.load_discrepancies()
    assert records == []

    # Getting summary stats from non-existent file returns default empty stats without error
    stats = store.get_summary_stats()
    assert stats["total_discrepancies"] == 0
    assert stats["by_type"] == {}
    assert stats["by_resolution"] == {}
    assert stats["top_suggestions"] == []

    # Recording a discrepancy creates the file and persists the record
    rec = store.record_discrepancy(
        ticket_id="TKT-MISSING-TEST",
        channel="app",
        raw_text="تحويل بمبلغ 50000 معلق",
        discrepancy_type="amount",
        field_name="amount_iqd",
        offline_value=50000,
        llm_value=50000,
        resolution_applied="cloud_consensus_boost",
        confidence_delta=0.05,
    )
    assert missing_file.exists()
    assert rec.ticket_id == "TKT-MISSING-TEST"

    # Re-loading confirms record is persisted and loadable
    loaded = store.load_discrepancies()
    assert len(loaded) == 1
    assert loaded[0].ticket_id == "TKT-MISSING-TEST"
