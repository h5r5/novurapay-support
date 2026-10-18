"""Unit tests for Sealed-Test Guard (Task C5).

Verifies sha256 checksum matching, clean git tree enforcement, freeze-* tag requirement,
EVAL_SEALED_CONFIRM environment check, and lock file single-run enforcement with override logging.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from supportpipe.evaluation.sealed_guard import SealedGuardError, check_sealed_test_guard


def test_sealed_guard_bypasses_non_sealed_splits(tmp_path: Path) -> None:
    """Non-sealed splits (e.g., dev.jsonl, train.jsonl) must bypass sealed guard."""
    dev_split = tmp_path / "dev.jsonl"
    dev_split.write_text("{}", encoding="utf-8")

    res = check_sealed_test_guard(split_path=dev_split, config_id="cfg_1")
    assert res["sealed"] is False
    assert res["status"] == "bypassed"


def test_sealed_guard_missing_reference_sha_file(tmp_path: Path) -> None:
    """If data/test_v2.sha256 does not exist, execution must be refused."""
    test_v2 = tmp_path / "test_v2.jsonl"
    test_v2.write_text("{}", encoding="utf-8")

    missing_sha_file = tmp_path / "nonexistent.sha256"

    with pytest.raises(SealedGuardError) as exc:
        check_sealed_test_guard(
            split_path=test_v2,
            config_id="cfg_1",
            expected_sha_path=missing_sha_file,
        )
    assert "reference sha256 file not found" in str(exc.value)


def test_sealed_guard_sha_mismatch(tmp_path: Path) -> None:
    """If sha256 of test_v2 does not match reference file, execution must be refused."""
    test_v2 = tmp_path / "test_v2.jsonl"
    test_v2.write_text('{"ticket": {"ticket_id": "T1"}}', encoding="utf-8")

    sha_file = tmp_path / "test_v2.sha256"
    sha_file.write_text("0000000000000000000000000000000000000000000000000000000000000000", encoding="utf-8")

    with pytest.raises(SealedGuardError) as exc:
        check_sealed_test_guard(
            split_path=test_v2,
            config_id="cfg_1",
            expected_sha_path=sha_file,
        )
    assert "SHA256 mismatch" in str(exc.value)


def test_sealed_guard_dirty_git_tree_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If git working tree has uncommitted changes, execution must be refused."""
    test_v2 = tmp_path / "test_v2.jsonl"
    content = '{"ticket": {"ticket_id": "T1"}}'
    test_v2.write_text(content, encoding="utf-8")
    actual_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()

    sha_file = tmp_path / "test_v2.sha256"
    sha_file.write_text(f"{actual_sha}  test_v2.jsonl", encoding="utf-8")

    with patch("supportpipe.evaluation.sealed_guard._get_git_output") as mock_git:
        mock_git.side_effect = lambda args, cwd=None: " M src/supportpipe/budget.py" if "status" in args else ""
        with pytest.raises(SealedGuardError) as exc:
            check_sealed_test_guard(
                split_path=test_v2,
                config_id="cfg_1",
                expected_sha_path=sha_file,
            )
        assert "Git tree is dirty" in str(exc.value)


def test_sealed_guard_missing_freeze_tag_refused(tmp_path: Path) -> None:
    """If HEAD is not tagged with freeze-*, execution must be refused."""
    test_v2 = tmp_path / "test_v2.jsonl"
    content = '{"ticket": {"ticket_id": "T1"}}'
    test_v2.write_text(content, encoding="utf-8")
    actual_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()

    sha_file = tmp_path / "test_v2.sha256"
    sha_file.write_text(actual_sha, encoding="utf-8")

    with patch("supportpipe.evaluation.sealed_guard._get_git_output") as mock_git:
        # status clean, but tags only has v1.0, not freeze-*
        def fake_git(args: list[str], cwd: Path | None = None) -> str:
            if "status" in args:
                return ""
            if "tag" in args:
                return "v1.0.0\nrelease-alpha"
            return "commit_123"

        mock_git.side_effect = fake_git

        with pytest.raises(SealedGuardError) as exc:
            check_sealed_test_guard(
                split_path=test_v2,
                config_id="cfg_1",
                expected_sha_path=sha_file,
            )
        assert "no tag matching 'freeze-*'" in str(exc.value)


def test_sealed_guard_env_var_mismatch_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If EVAL_SEALED_CONFIRM does not match sha prefix, execution must be refused."""
    test_v2 = tmp_path / "test_v2.jsonl"
    content = '{"ticket": {"ticket_id": "T1"}}'
    test_v2.write_text(content, encoding="utf-8")
    actual_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()

    sha_file = tmp_path / "test_v2.sha256"
    sha_file.write_text(actual_sha, encoding="utf-8")

    with patch("supportpipe.evaluation.sealed_guard._get_git_output") as mock_git:
        def fake_git(args: list[str], cwd: Path | None = None) -> str:
            if "status" in args:
                return ""
            if "tag" in args:
                return "freeze-2026-10-18"
            return "commit_123"

        mock_git.side_effect = fake_git

        # 1. Missing env var
        monkeypatch.delenv("EVAL_SEALED_CONFIRM", raising=False)
        with pytest.raises(SealedGuardError) as exc_missing:
            check_sealed_test_guard(
                split_path=test_v2,
                config_id="cfg_1",
                expected_sha_path=sha_file,
            )
        assert "EVAL_SEALED_CONFIRM environment variable is missing" in str(exc_missing.value)

        # 2. Mismatched prefix
        monkeypatch.setenv("EVAL_SEALED_CONFIRM", "deadbeef")
        with pytest.raises(SealedGuardError) as exc_mismatch:
            check_sealed_test_guard(
                split_path=test_v2,
                config_id="cfg_1",
                expected_sha_path=sha_file,
            )
        assert "does not match file sha256 prefix" in str(exc_mismatch.value)


def test_sealed_guard_single_run_and_override_lock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify first run records to lock file, second run is refused without override, and accepted with override."""
    test_v2 = tmp_path / "test_v2.jsonl"
    content = '{"ticket": {"ticket_id": "T1"}}'
    test_v2.write_text(content, encoding="utf-8")
    actual_sha = hashlib.sha256(content.encode("utf-8")).hexdigest()

    sha_file = tmp_path / "test_v2.sha256"
    sha_file.write_text(actual_sha, encoding="utf-8")
    lock_file = tmp_path / ".sealed_test_lock.json"

    monkeypatch.setenv("EVAL_SEALED_CONFIRM", actual_sha[:8])

    with patch("supportpipe.evaluation.sealed_guard._get_git_output") as mock_git:
        def fake_git(args: list[str], cwd: Path | None = None) -> str:
            if "status" in args:
                return ""
            if "tag" in args:
                return "freeze-final-2026"
            return "abc12345678"

        mock_git.side_effect = fake_git

        # 1. First run succeeds and creates lock file
        res1 = check_sealed_test_guard(
            split_path=test_v2,
            config_id="offline_rule_ml",
            lock_file_path=lock_file,
            expected_sha_path=sha_file,
        )
        assert res1["status"] == "authorized"
        assert lock_file.exists()

        lock_content = json.loads(lock_file.read_text(encoding="utf-8"))
        assert len(lock_content["runs"]) == 1
        assert lock_content["runs"][0]["config_id"] == "offline_rule_ml"
        assert lock_content["runs"][0]["override_reason"] is None

        # 2. Second run without override reason must be refused
        with pytest.raises(SealedGuardError) as exc_refused:
            check_sealed_test_guard(
                split_path=test_v2,
                config_id="offline_rule_ml",
                lock_file_path=lock_file,
                expected_sha_path=sha_file,
            )
        assert "A second run is strictly refused" in str(exc_refused.value)

        # 3. Second run WITH override reason must succeed and log reason
        res2 = check_sealed_test_guard(
            split_path=test_v2,
            config_id="offline_rule_ml",
            lock_file_path=lock_file,
            expected_sha_path=sha_file,
            override_reason="Benchmarking latency regression after compiler flag tweak",
        )
        assert res2["status"] == "authorized"
        assert res2["override_reason"] == "Benchmarking latency regression after compiler flag tweak"

        lock_content_updated = json.loads(lock_file.read_text(encoding="utf-8"))
        assert len(lock_content_updated["runs"]) == 2
        assert lock_content_updated["runs"][1]["override_reason"] == "Benchmarking latency regression after compiler flag tweak"
