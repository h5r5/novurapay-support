"""Stress test batch ingestion script (S2).

Validates schema, taxonomy labels (14 categories, 3 priorities), and rejects:
1. Invalid category or priority
2. Empty or whitespace-only text
3. Exact duplicate text
4. Normalized near-duplicate (SequenceMatcher ratio >= 0.9) against dev, test, or existing stress batches.

Strict Invariant: NEVER loads data/test_v2*.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import logging
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from supportpipe.extract.normalize import strip_arabic_diacritics_and_tatweel
from supportpipe.taxonomy.loader import taxonomy

logger = logging.getLogger("supportpipe.stress.ingest")

VALID_PRIORITIES = {"high", "medium", "low"}


def assert_not_test_v2(path: Path | str | None) -> None:
    """Enforce strict invariant: NEVER load data/test_v2*."""
    if path is None:
        return
    norm = str(path).lower().replace("\\", "/")
    if "test_v2" in norm:
        raise PermissionError(
            f"STRICT INVARIANT VIOLATION: Access denied to protected test_v2 path: {path}"
        )


def normalize_text_for_dedup(text: str) -> str:
    """Standard text normalization for duplicate and near-duplicate detection.

    Steps:
    1. Lowercase
    2. Strip Arabic diacritics (harakat/tashkeel) and tatweel (kashida)
    3. Strip punctuation (ASCII & Arabic punctuation)
    4. Normalize whitespace
    """
    if not text:
        return ""
    t = text.lower()
    t = strip_arabic_diacritics_and_tatweel(t)
    # Strip ASCII and Arabic punctuation
    t = re.sub(
        r"""[!"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~،؟؛«»…—–“”’‘\u060C\u061B\u061F]""",
        " ",
        t,
    )
    t = re.sub(r"\s+", " ", t).strip()
    return t


def compute_file_sha256(filepath: Path) -> str:
    """Compute sha256 checksum of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_reference_corpus(
    dev_path: Path | None = None,
    test_path: Path | None = None,
    stress_dir: Path | None = None,
) -> list[dict[str, str]]:
    """Load reference tickets for duplicate detection.

    Loads from dev.jsonl, test.jsonl, and any existing stress batches in stress_dir.
    Strictly enforces that no test_v2 file is loaded.
    """
    assert_not_test_v2(dev_path)
    assert_not_test_v2(test_path)
    assert_not_test_v2(stress_dir)

    corpus: list[dict[str, str]] = []

    def _ingest_split_file(filepath: Path, source_label: str) -> None:
        if not filepath.exists():
            return
        assert_not_test_v2(filepath)
        with open(filepath, encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                s = line.strip()
                if not s:
                    continue
                try:
                    data = json.loads(s)
                    raw_text = ""
                    t_id = f"{source_label}_row_{idx}"
                    if "ticket" in data and isinstance(data["ticket"], dict):
                        raw_text = str(data["ticket"].get("raw_text") or data["ticket"].get("text") or "")
                        t_id = str(data["ticket"].get("ticket_id") or t_id)
                    elif "raw_text" in data or "text" in data:
                        raw_text = str(data.get("raw_text") or data.get("text") or "")
                        t_id = str(data.get("ticket_id") or t_id)

                    if raw_text:
                        corpus.append({
                            "ticket_id": t_id,
                            "raw_text": raw_text,
                            "norm_text": normalize_text_for_dedup(raw_text),
                            "source": source_label,
                        })
                except json.JSONDecodeError:
                    continue

    if dev_path:
        _ingest_split_file(dev_path, str(dev_path))
    if test_path:
        _ingest_split_file(test_path, str(test_path))

    if stress_dir and stress_dir.exists():
        for batch_file in sorted(stress_dir.glob("batch_*.jsonl")):
            assert_not_test_v2(batch_file)
            _ingest_split_file(batch_file, batch_file.name)

    return corpus


def parse_and_validate_row(
    raw_item: dict[str, Any],
    row_idx: int,
    valid_categories: set[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    """Validate a single ticket row schema and taxonomy values.

    Returns:
        (canonical_row_dict or None, list_of_error_strings)
    """
    errors: list[str] = []

    # Extract ticket fields
    if "ticket" in raw_item and isinstance(raw_item["ticket"], dict):
        t_data = raw_item["ticket"]
        ticket_id = str(t_data.get("ticket_id") or f"ROW-{row_idx}").strip()
        raw_text = str(t_data.get("raw_text") or t_data.get("text") or "")
        channel = str(t_data.get("channel") or "app").strip()
        submitted_at = str(
            t_data.get("submitted_at") or datetime.now(UTC).isoformat()
        )
        synthetic_user_id = str(
            t_data.get("synthetic_user_id") or f"SYN-USR-{row_idx:04d}"
        )
    else:
        ticket_id = str(raw_item.get("ticket_id") or f"ROW-{row_idx}").strip()
        raw_text = str(raw_item.get("raw_text") or raw_item.get("text") or "")
        channel = str(raw_item.get("channel") or "app").strip()
        submitted_at = str(
            raw_item.get("submitted_at") or datetime.now(UTC).isoformat()
        )
        synthetic_user_id = str(
            raw_item.get("synthetic_user_id") or f"SYN-USR-{row_idx:04d}"
        )

    # Extract label fields
    if "label" in raw_item and isinstance(raw_item["label"], dict):
        l_data = raw_item["label"]
        category = str(l_data.get("category") or "").strip()
        priority = str(l_data.get("priority") or "").strip().lower()
        expected_team = str(l_data.get("expected_team") or taxonomy.get_team_for_category(category))
        expected_fields = l_data.get("expected_fields") or {}
        edge_case = l_data.get("edge_case")
        notes = l_data.get("notes")
        template_id = l_data.get("template_id")
        tags = l_data.get("tags") or raw_item.get("tags") or {}
    else:
        category = str(raw_item.get("category") or "").strip()
        priority = str(raw_item.get("priority") or "").strip().lower()
        expected_team = str(raw_item.get("expected_team") or taxonomy.get_team_for_category(category))
        expected_fields = raw_item.get("expected_fields") or {}
        edge_case = raw_item.get("edge_case")
        notes = raw_item.get("notes")
        template_id = raw_item.get("template_id")
        tags = raw_item.get("tags") or {}

    # Validation 1: Empty or whitespace-only text
    if not raw_text or not raw_text.strip():
        errors.append("Empty or whitespace-only text")

    # Validation 2: Category
    if not category:
        errors.append("Missing required field 'category'")
    elif category not in valid_categories:
        errors.append(
            f"Invalid category '{category}'. Must be one of the 14 valid taxonomy categories: {sorted(valid_categories)}"
        )

    # Validation 3: Priority
    if not priority:
        errors.append("Missing required field 'priority'")
    elif priority not in VALID_PRIORITIES:
        errors.append(
            f"Invalid priority '{priority}'. Must be one of: {sorted(VALID_PRIORITIES)}"
        )

    if errors:
        return None, errors

    canonical: dict[str, Any] = {
        "ticket": {
            "ticket_id": ticket_id,
            "channel": channel,
            "raw_text": raw_text,
            "submitted_at": submitted_at,
            "synthetic_user_id": synthetic_user_id,
        },
        "label": {
            "category": category,
            "priority": priority,
            "expected_team": expected_team,
            "expected_fields": expected_fields,
            "edge_case": edge_case,
            "notes": notes,
            "template_id": template_id,
            "tags": tags if isinstance(tags, dict) else {},
        },
    }
    return canonical, []


def check_duplicates_and_near_duplicates(
    row_text: str,
    row_id: str,
    preceding_batch_items: list[dict[str, str]],
    reference_corpus: list[dict[str, str]],
    threshold: float = 0.9,
) -> list[str]:
    """Check against preceding batch items and reference corpus for exact or near duplicate text."""
    errors: list[str] = []
    norm_text = normalize_text_for_dedup(row_text)
    clean_raw = row_text.strip()

    all_comparisons = [("current_batch", preceding_batch_items), ("reference_corpus", reference_corpus)]

    for _group_name, items in all_comparisons:
        for ref in items:
            ref_raw = ref["raw_text"].strip()
            # Exact duplicate check
            if clean_raw == ref_raw:
                errors.append(
                    f"Exact duplicate text of ticket '{ref['ticket_id']}' in {ref['source']}"
                )
                return errors  # No need to check near-duplicate if exact match

            # Fast length pruning before SequenceMatcher
            ref_norm = ref["norm_text"]
            len_a, len_b = len(norm_text), len(ref_norm)
            if not len_a or not len_b:
                continue

            min_len = min(len_a, len_b)
            # Maximum possible ratio is 2 * min_len / (len_a + len_b)
            max_possible_ratio = 2.0 * min_len / (len_a + len_b)
            if max_possible_ratio < threshold:
                continue

            # SequenceMatcher ratio check
            ratio = difflib.SequenceMatcher(None, norm_text, ref_norm).ratio()
            if ratio >= threshold:
                errors.append(
                    f"Normalized near-duplicate (similarity {ratio:.3f} >= {threshold}) with ticket '{ref['ticket_id']}' in {ref['source']}"
                )
                return errors

    return errors


def resolve_next_batch_id(stress_dir: Path) -> str:
    """Find the next batch number batch_NNN."""
    existing = list(stress_dir.glob("batch_*.jsonl"))
    max_num = 0
    for p in existing:
        m = re.match(r"batch_(\d+)\.jsonl", p.name)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"batch_{max_num + 1:03d}"


def ingest_stress_batch(
    input_file: Path | str,
    stress_dir: Path | str = "data/stress",
    dev_split: Path | str = "data/splits/dev.jsonl",
    test_split: Path | str = "data/splits/test.jsonl",
    batch_id: str | None = None,
    generator: str = "unknown",
    prompt_hash: str = "none",
) -> dict[str, Any]:
    """Ingest, validate, and register a stress test batch.

    Raises ValueError if any row is invalid. Never silently drops or auto-repairs rows.
    """
    input_path = Path(input_file).resolve()
    stress_path = Path(stress_dir).resolve()
    dev_path = Path(dev_split).resolve()
    test_path = Path(test_split).resolve()

    # Invariant guard
    assert_not_test_v2(input_path)
    assert_not_test_v2(stress_path)
    assert_not_test_v2(dev_path)
    assert_not_test_v2(test_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input batch file not found: {input_path}")

    valid_categories = set(taxonomy.get_valid_category_ids())
    reference_corpus = load_reference_corpus(
        dev_path=dev_path if dev_path.exists() else None,
        test_path=test_path if test_path.exists() else None,
        stress_dir=stress_path if stress_path.exists() else None,
    )

    batch_failures: dict[int, dict[str, Any]] = {}
    valid_rows: list[dict[str, Any]] = []
    preceding_items: list[dict[str, str]] = []

    with open(input_path, encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        raise ValueError(f"Batch file is empty: {input_path}")

    for idx, raw_line in enumerate(lines, 1):
        line_str = raw_line.strip()
        if not line_str:
            batch_failures[idx] = {
                "ticket_id": f"ROW-{idx}",
                "errors": ["Empty line in JSONL file"],
            }
            continue

        try:
            item_data = json.loads(line_str)
        except json.JSONDecodeError as e:
            batch_failures[idx] = {
                "ticket_id": f"ROW-{idx}",
                "errors": [f"Malformed JSON: {e}"],
            }
            continue

        if not isinstance(item_data, dict):
            batch_failures[idx] = {
                "ticket_id": f"ROW-{idx}",
                "errors": ["Row is not a JSON object"],
            }
            continue

        canonical_row, row_errors = parse_and_validate_row(
            item_data, idx, valid_categories
        )

        ticket_id = (
            canonical_row["ticket"]["ticket_id"]
            if canonical_row
            else str(item_data.get("ticket_id") or f"ROW-{idx}")
        )
        raw_text = (
            canonical_row["ticket"]["raw_text"]
            if canonical_row
            else str(item_data.get("raw_text") or item_data.get("text") or "")
        )

        # Check duplicates only if text is non-empty
        if raw_text.strip():
            dup_errors = check_duplicates_and_near_duplicates(
                row_text=raw_text,
                row_id=ticket_id,
                preceding_batch_items=preceding_items,
                reference_corpus=reference_corpus,
            )
            row_errors.extend(dup_errors)

        if row_errors:
            batch_failures[idx] = {
                "ticket_id": ticket_id,
                "errors": row_errors,
            }
        else:
            assert canonical_row is not None
            valid_rows.append(canonical_row)
            preceding_items.append({
                "ticket_id": ticket_id,
                "raw_text": raw_text,
                "norm_text": normalize_text_for_dedup(raw_text),
                "source": "incoming_batch",
            })

    if batch_failures:
        report_lines = [
            "=== STRESS BATCH INGESTION FAILED ===",
            f"Input File: {input_path}",
            f"Total Rows: {len(lines)}",
            f"Invalid Rows: {len(batch_failures)}",
            "",
        ]
        for row_num, fail_info in sorted(batch_failures.items()):
            report_lines.append(f"Row {row_num} (ticket_id: {fail_info['ticket_id']}):")
            for err in fail_info["errors"]:
                report_lines.append(f"  - {err}")
        err_msg = "\n".join(report_lines)
        sys.stderr.write(err_msg + "\n")
        raise ValueError(err_msg)

    # Ingestion accepted: Write to target stress directory
    stress_path.mkdir(parents=True, exist_ok=True)

    if not batch_id:
        batch_stem = resolve_next_batch_id(stress_path)
    else:
        batch_stem = batch_id if batch_id.startswith("batch_") else f"batch_{batch_id}"

    out_batch_file = stress_path / f"{batch_stem}.jsonl"

    with open(out_batch_file, "w", encoding="utf-8") as f:
        for row in valid_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    file_sha256 = compute_file_sha256(out_batch_file)
    manifest_path = stress_path / "MANIFEST.json"

    manifest_data: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception as e:
            logger.warning("Could not read existing MANIFEST.json (%s), starting fresh", e)

    batch_entry = {
        "sha256": file_sha256,
        "n": len(valid_rows),
        "generator": generator,
        "date": datetime.now(UTC).isoformat(),
        "prompt_hash": prompt_hash,
        "status": "unmeasured",
    }
    manifest_data[batch_stem] = batch_entry

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    return {
        "batch_id": batch_stem,
        "batch_file": str(out_batch_file),
        "sha256": file_sha256,
        "n": len(valid_rows),
        "status": "unmeasured",
        "manifest_path": str(manifest_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest and validate a synthetic stress test batch")
    parser.add_argument("input_file", type=str, help="Path to raw JSONL batch file to ingest")
    parser.add_argument(
        "--stress-dir",
        type=str,
        default="data/stress",
        help="Target stress directory (default: data/stress)",
    )
    parser.add_argument(
        "--batch-id",
        type=str,
        default=None,
        help="Batch identifier (e.g., batch_001 or 001). Auto-resolved if omitted.",
    )
    parser.add_argument(
        "--generator",
        type=str,
        default="unknown",
        help="Generator model or procedure name",
    )
    parser.add_argument(
        "--prompt-hash",
        type=str,
        default="none",
        help="Prompt hash used for generation",
    )
    parser.add_argument(
        "--dev-split",
        type=str,
        default="data/splits/dev.jsonl",
        help="Path to dev.jsonl split",
    )
    parser.add_argument(
        "--test-split",
        type=str,
        default="data/splits/test.jsonl",
        help="Path to test.jsonl split",
    )

    args = parser.parse_args()

    try:
        res = ingest_stress_batch(
            input_file=args.input_file,
            stress_dir=args.stress_dir,
            dev_split=args.dev_split,
            test_split=args.test_split,
            batch_id=args.batch_id,
            generator=args.generator,
            prompt_hash=args.prompt_hash,
        )
        print("=== STRESS BATCH INGESTION SUCCESSFUL ===")
        print(f"Batch ID:      {res['batch_id']}")
        print(f"Batch File:    {res['batch_file']}")
        print(f"Tickets Count: {res['n']}")
        print(f"SHA-256:       {res['sha256']}")
        print(f"Status:        {res['status']}")
        print(f"Manifest:      {res['manifest_path']}")
    except Exception as e:
        sys.stderr.write(f"\nIngestion aborted: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
