"""Sealed-test guard enforcing cryptographic integrity, clean git tree, freeze tag, and single-run lock (Task C5)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from supportpipe.config import settings

logger = logging.getLogger(__name__)


class SealedGuardError(RuntimeError):
    """Raised when any condition of the sealed-test guard is violated."""

    pass


def _get_git_output(args: list[str], cwd: Path | None = None) -> str:
    """Helper to run git commands with error handling."""
    try:
        res = subprocess.run(
            ["git", *args],
            cwd=cwd or settings.project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        return res.stdout.strip()
    except Exception as exc:
        raise SealedGuardError(f"Failed to execute git command: {exc}") from exc


def check_sealed_test_guard(
    split_path: Path | str,
    config_id: str,
    lock_file_path: Path | None = None,
    override_reason: str | None = None,
    expected_sha_path: Path | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    """Verify cryptographic, git, and execution constraints for sealed test sets (test_v2).

    If split name contains 'test_v2', execution is permitted ONLY if:
      1. File sha256 matches data/test_v2.sha256.
      2. Git working tree is completely clean.
      3. A tag matching 'freeze-*' points at current HEAD.
      4. EVAL_SEALED_CONFIRM env var equals the sha256 prefix.
      5. Config has not been run against this test set before, or an explicit override_reason is provided.

    Returns:
        dict with verification metadata.
    Raises:
        SealedGuardError: If any condition fails.
    """
    path = Path(split_path)
    split_name = path.name.lower()

    # Bypassed for non-sealed splits (e.g., dev.jsonl, synthetic stress sets)
    if "test_v2" not in split_name:
        return {"sealed": False, "status": "bypassed", "split": str(split_path)}

    if not path.exists():
        raise FileNotFoundError(f"Sealed test file not found: {path}")

    # 1. Compute and verify sha256
    file_bytes = path.read_bytes()
    actual_sha = hashlib.sha256(file_bytes).hexdigest()

    sha_file = Path(expected_sha_path or (settings.data_dir / "test_v2.sha256"))
    if not sha_file.exists():
        raise SealedGuardError(
            f"Sealed test reference sha256 file not found at: {sha_file}. Cannot verify integrity."
        )

    expected_sha_content = sha_file.read_text(encoding="utf-8").strip()
    expected_sha = expected_sha_content.split()[0].lower()

    if actual_sha.lower() != expected_sha:
        raise SealedGuardError(
            f"SHA256 mismatch for sealed test: expected '{expected_sha}', got '{actual_sha}'."
        )

    # 2. Check clean git working tree
    git_status = _get_git_output(["status", "--porcelain"], cwd=cwd)
    if git_status:
        raise SealedGuardError(
            "Git tree is dirty. Sealed test execution strictly requires a clean working tree."
        )

    # 3. Check tag freeze-* points at HEAD
    tags_output = _get_git_output(["tag", "--points-at", "HEAD"], cwd=cwd)
    tags = [t.strip() for t in tags_output.splitlines() if t.strip()]
    freeze_tags = [t for t in tags if t.startswith("freeze-")]
    if not freeze_tags:
        raise SealedGuardError(
            f"Current HEAD has tags {tags}, but no tag matching 'freeze-*' points at HEAD."
        )
    active_tag = freeze_tags[0]

    # 4. Environment variable confirmation
    env_confirm = os.environ.get("EVAL_SEALED_CONFIRM", "").strip()
    if not env_confirm:
        raise SealedGuardError(
            "EVAL_SEALED_CONFIRM environment variable is missing. "
            "Must be set to the sha256 prefix of the sealed test."
        )

    if not actual_sha.lower().startswith(env_confirm.lower()):
        raise SealedGuardError(
            f"EVAL_SEALED_CONFIRM prefix '{env_confirm}' does not match file sha256 prefix '{actual_sha[:len(env_confirm)]}'."
        )

    # 5. Lock file check and single-run enforcement
    lock_file = Path(lock_file_path or (settings.data_dir / ".sealed_test_lock.json"))
    lock_data: dict[str, Any] = {"runs": []}

    if lock_file.exists():
        try:
            content = lock_file.read_text(encoding="utf-8").strip()
            if content:
                loaded = json.loads(content)
                if isinstance(loaded, dict) and "runs" in loaded:
                    lock_data = loaded
        except Exception as e:
            logger.warning("Could not read sealed test lock file %s: %s", lock_file, e)

    runs: list[dict[str, Any]] = lock_data.get("runs", [])
    prior_runs = [
        r for r in runs if r.get("config_id") == config_id and r.get("sha256") == actual_sha
    ]

    has_prior = len(prior_runs) > 0
    clean_override = override_reason.strip() if override_reason else None

    if has_prior and not clean_override:
        raise SealedGuardError(
            f"Sealed test has already been run for config '{config_id}' (sha256: {actual_sha[:10]}...). "
            f"A second run is strictly refused unless --override-reason is provided and logged."
        )

    head_commit = _get_git_output(["rev-parse", "HEAD"], cwd=cwd)
    run_record: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "config_id": config_id,
        "sha256": actual_sha,
        "git_commit": head_commit,
        "tag": active_tag,
        "override_reason": clean_override,
    }

    runs.append(run_record)
    lock_data["runs"] = runs

    try:
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_file.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")
    except Exception as exc:
        raise SealedGuardError(f"Failed to record run to sealed test lock file: {exc}") from exc

    logger.info(
        "Sealed test guard authorized execution for config '%s' (tag: %s, commit: %s)",
        config_id,
        active_tag,
        head_commit[:8],
    )
    return {
        "sealed": True,
        "status": "authorized",
        "sha256": actual_sha,
        "tag": active_tag,
        "git_commit": head_commit,
        "override_reason": clean_override,
    }
