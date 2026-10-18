"""Tests for Frozen Data Policy and Cryptographic Integrity (Task P1, P2).

Enforces:
1. Manifest verification: all files listed in data/PROTECTED.sha256 exist and match their SHA-256 hash.
2. Git diff check: fails if git diff --name-only <MAIN>..HEAD contains any protected path:
   - data/splits/test.jsonl
   - data/test_v2*
   - data/test_v2.sha256
   - results/eval_test_*
   - data/PROTECTED.sha256 (if modified unexpectedly)
3. Mutation proof: alters a single byte of a temporary protected copy and asserts that
   the verification helper detects the tampering (raises AssertionError or returns False).
"""

from __future__ import annotations

import fnmatch
import hashlib
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Strict patterns that can never be touched or committed in a branch
PROTECTED_PATTERNS: tuple[str, ...] = (
    "data/splits/test.jsonl",
    "data/test_v2*",
    "data/test_v2.sha256",
    "results/eval_test_*",
)


def compute_sha256(file_path: Path | str) -> str:
    """Compute the SHA-256 hex digest of a file."""
    path = Path(file_path)
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_protected_hashes(
    manifest_path: Path | str | None = None,
    root_dir: Path | str | None = None,
    raise_on_error: bool = False,
) -> bool:
    """Verify all files listed in the sha256 manifest match their hashes on disk.

    Args:
        manifest_path: Path to the .sha256 manifest file. Defaults to data/PROTECTED.sha256.
        root_dir: Root directory for relative paths in manifest. Defaults to PROJECT_ROOT.
        raise_on_error: If True, raises AssertionError on verification failure.

    Returns:
        True if all files exist and match their expected hashes, False otherwise.
    """
    root = Path(root_dir) if root_dir is not None else PROJECT_ROOT
    manifest = Path(manifest_path) if manifest_path is not None else (root / "data" / "PROTECTED.sha256")

    if not manifest.exists():
        if raise_on_error:
            raise AssertionError(f"Protected manifest not found at: {manifest}")
        return False

    lines = manifest.read_text(encoding="utf-8").splitlines()
    entries: list[tuple[str, str]] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            if raise_on_error:
                raise AssertionError(f"Malformed manifest line: '{line}' in {manifest}")
            return False
        expected_sha = parts[0].strip().lower()
        rel_path = parts[1].strip().lstrip("*")
        entries.append((expected_sha, rel_path))

    if not entries:
        if raise_on_error:
            raise AssertionError(f"Protected manifest {manifest} is empty.")
        return False

    for expected_sha, rel_path in entries:
        target_file = root / rel_path
        if not target_file.exists():
            if raise_on_error:
                raise AssertionError(f"Protected file not found on disk: {target_file}")
            return False
        actual_sha = compute_sha256(target_file).lower()
        if actual_sha != expected_sha:
            if raise_on_error:
                raise AssertionError(
                    f"SHA256 mismatch for protected file '{rel_path}': expected {expected_sha}, got {actual_sha}"
                )
            return False

    return True


def resolve_base_ref(cwd: Path | None = None) -> str:
    """Resolve base main reference, preferring 'merged-phases-1-5' then 'main'."""
    repo_cwd = cwd or PROJECT_ROOT
    for candidate in ("merged-phases-1-5", "main"):
        res = subprocess.run(
            ["git", "rev-parse", "--verify", candidate],
            cwd=repo_cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            return candidate
    return "main"


def get_git_diff_names(base_ref: str, cwd: Path | None = None) -> list[str]:
    """Retrieve changed files from git diff --name-only <base_ref>..HEAD."""
    repo_cwd = cwd or PROJECT_ROOT
    res = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}..HEAD"],
        cwd=repo_cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        raise RuntimeError(f"git diff failed: {res.stderr.strip()}")
    return [line.strip().replace("\\", "/") for line in res.stdout.splitlines() if line.strip()]


def check_git_diff_integrity(
    base_ref: str | None = None,
    cwd: Path | None = None,
    diff_files: list[str] | None = None,
    raise_on_error: bool = False,
) -> list[str]:
    """Check git diff against base_ref for protected path modifications.

    Protected patterns checked:
      - data/splits/test.jsonl
      - data/test_v2*
      - data/test_v2.sha256
      - results/eval_test_*
      - data/PROTECTED.sha256 (if modified unexpectedly)

    Args:
        base_ref: Base ref ('merged-phases-1-5' or 'main'). Resolved automatically if None.
        cwd: Git working directory. Defaults to PROJECT_ROOT.
        diff_files: Explicit list of changed files to check (useful for unit testing).
        raise_on_error: If True, raises AssertionError if any violations are found.

    Returns:
        List of violating file paths.
    """
    repo_cwd = cwd or PROJECT_ROOT
    target_base = base_ref or resolve_base_ref(cwd=repo_cwd)
    files = diff_files if diff_files is not None else get_git_diff_names(target_base, cwd=repo_cwd)

    violations: list[str] = []
    for file_path in files:
        norm_path = file_path.replace("\\", "/").strip()

        # 1. Strict patterns check
        is_strict_violation = False
        for pat in PROTECTED_PATTERNS:
            if norm_path == pat or fnmatch.fnmatch(norm_path, pat):
                violations.append(norm_path)
                is_strict_violation = True
                break

        if is_strict_violation:
            continue

        # 2. Manifest check: data/PROTECTED.sha256 if modified unexpectedly
        if norm_path == "data/PROTECTED.sha256":
            # If the file already existed in target_base, any diff in target_base..HEAD is an unexpected modification.
            res = subprocess.run(
                ["git", "cat-file", "-e", f"{target_base}:data/PROTECTED.sha256"],
                cwd=repo_cwd,
                capture_output=True,
                text=True,
                check=False,
            )
            if res.returncode == 0:
                violations.append(norm_path)
            # If it did not exist in target_base, initial addition in this phase is expected.

    if violations and raise_on_error:
        raise AssertionError(
            f"Git diff against '{target_base}..HEAD' violates frozen data policy: {violations}"
        )

    return violations


# --- Test Suite ---


def test_frozen_data_hash_integrity() -> None:
    """(a) Hash check: reads data/PROTECTED.sha256 and verifies all listed files match their sha256 hashes on disk."""
    assert verify_protected_hashes(raise_on_error=True) is True


def test_frozen_data_manifest_contains_burned_holdout() -> None:
    """Ensure data/splits/test.jsonl is explicitly registered in data/PROTECTED.sha256."""
    manifest_path = PROJECT_ROOT / "data" / "PROTECTED.sha256"
    assert manifest_path.exists(), f"Manifest file missing: {manifest_path}"
    content = manifest_path.read_text(encoding="utf-8")
    assert "data/splits/test.jsonl" in content


def test_frozen_data_git_diff_integrity() -> None:
    """(b) Git diff check: fails if git diff --name-only <MAIN>..HEAD contains any protected path."""
    violations = check_git_diff_integrity(raise_on_error=True)
    assert not violations, f"Protected paths violated in git diff: {violations}"


def test_frozen_data_mutation_proof(tmp_path: Path) -> None:
    """(c) Mutation proof on a TEMP copy: creates a temporary copy of a protected file

    and temporary manifest, alters a single byte, and asserts that the verification helper
    raises AssertionError or returns False.
    """
    sub_dir = tmp_path / "data" / "splits"
    sub_dir.mkdir(parents=True)
    temp_test_file = sub_dir / "test.jsonl"

    original_bytes = (
        b'{"ticket_id": "T1", "text": "NovuraPay transfer issue"}\n'
        b'{"ticket_id": "T2", "text": "Card PIN blocked"}\n'
    )
    temp_test_file.write_bytes(original_bytes)
    real_sha = hashlib.sha256(original_bytes).hexdigest()

    temp_manifest = tmp_path / "data" / "PROTECTED.sha256"
    temp_manifest.write_text(f"{real_sha}  data/splits/test.jsonl\n", encoding="utf-8")

    # 1. Verification succeeds before mutation
    assert verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=True) is True
    assert verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=False) is True

    # 2. Mutate a single byte in the protected file
    mutated_bytes = bytearray(original_bytes)
    mutated_bytes[0] ^= 0x01
    temp_test_file.write_bytes(bytes(mutated_bytes))

    # 3. Assert helper returns False when raise_on_error=False
    assert verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=False) is False

    # 4. Assert helper raises AssertionError when raise_on_error=True
    with pytest.raises(AssertionError) as exc_info:
        verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=True)
    assert "SHA256 mismatch" in str(exc_info.value)


def test_frozen_data_mutation_proof_on_manifest_hash(tmp_path: Path) -> None:
    """Mutation proof altering a single byte in the manifest checksum itself."""
    sub_dir = tmp_path / "data" / "splits"
    sub_dir.mkdir(parents=True)
    temp_test_file = sub_dir / "test.jsonl"

    original_bytes = b'{"ticket_id": "T1"}\n'
    temp_test_file.write_bytes(original_bytes)
    real_sha = hashlib.sha256(original_bytes).hexdigest()

    # Tamper with the hash in the manifest (flip last char)
    tampered_sha = real_sha[:-1] + ("0" if real_sha[-1] != "0" else "1")
    temp_manifest = tmp_path / "data" / "PROTECTED.sha256"
    temp_manifest.write_text(f"{tampered_sha}  data/splits/test.jsonl\n", encoding="utf-8")

    assert verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=False) is False
    with pytest.raises(AssertionError) as exc_info:
        verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=True)
    assert "SHA256 mismatch" in str(exc_info.value)


def test_frozen_data_missing_file_detection(tmp_path: Path) -> None:
    """Verification helper fails if a listed file does not exist."""
    temp_manifest = tmp_path / "PROTECTED.sha256"
    temp_manifest.write_text(
        "78877a78997ea03ff9f543024f6bfa0951d96970f9a9abdaa92e8a9e442bfb56  nonexistent.jsonl\n",
        encoding="utf-8",
    )
    assert verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=False) is False
    with pytest.raises(AssertionError) as exc_info:
        verify_protected_hashes(manifest_path=temp_manifest, root_dir=tmp_path, raise_on_error=True)
    assert "Protected file not found on disk" in str(exc_info.value)


@pytest.mark.parametrize(
    "forbidden_path",
    [
        "data/splits/test.jsonl",
        "data/test_v2.jsonl",
        "data/test_v2_holdout.jsonl",
        "data/test_v2.sha256",
        "results/eval_test_matrix_2026.json",
        "results/eval_test_benchmark.jsonl",
    ],
)
def test_git_diff_integrity_detects_forbidden_paths(forbidden_path: str) -> None:
    """Ensure check_git_diff_integrity flags any protected pattern."""
    violations = check_git_diff_integrity(
        base_ref="merged-phases-1-5",
        diff_files=["src/supportpipe/classifier.py", forbidden_path],
        raise_on_error=False,
    )
    assert forbidden_path in violations

    with pytest.raises(AssertionError) as exc_info:
        check_git_diff_integrity(
            base_ref="merged-phases-1-5",
            diff_files=["src/supportpipe/classifier.py", forbidden_path],
            raise_on_error=True,
        )
    assert forbidden_path in str(exc_info.value)


def test_git_diff_integrity_allows_safe_files() -> None:
    """Ensure regular files are not flagged as violations."""
    safe_files = [
        "src/supportpipe/classifier.py",
        "tests/test_something.py",
        "docs/evaluation.md",
        "configs/model_config.yaml",
    ]
    violations = check_git_diff_integrity(
        base_ref="merged-phases-1-5",
        diff_files=safe_files,
        raise_on_error=True,
    )
    assert violations == []


def test_git_diff_integrity_manifest_modification_policy() -> None:
    """Manifest is flagged if modified when already in base_ref, but allowed when newly added."""
    # Scenario A: Manifest existed in base_ref (returncode == 0) -> modification is a violation
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        violations = check_git_diff_integrity(
            base_ref="merged-phases-1-5",
            diff_files=["data/PROTECTED.sha256"],
            raise_on_error=False,
        )
        assert "data/PROTECTED.sha256" in violations

    # Scenario B: Manifest did NOT exist in base_ref (returncode == 1) -> initial addition is allowed
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)
        violations = check_git_diff_integrity(
            base_ref="merged-phases-1-5",
            diff_files=["data/PROTECTED.sha256"],
            raise_on_error=False,
        )
        assert "data/PROTECTED.sha256" not in violations
