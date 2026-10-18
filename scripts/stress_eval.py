"""Blind evaluation runner for stress test batches (S3).

Executes blind evaluation using offline local model (Rules + dialect ML trained on dev.jsonl only).
Prints AGGREGATES ONLY. Strictly NO ticket text in outputs or console.
Writes:
- results/stress_NNN_blind/summary.md
- results/stress_NNN_blind/per_ticket.csv
Updates data/stress/MANIFEST.json batch status to "measured_blind".
Strictly REFUSES second blind run on the same batch.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import subprocess
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.evaluation.metrics import compute_wilson_ci

logger = logging.getLogger("supportpipe.stress.eval")


def assert_not_test_v2(path: Path | str | None) -> None:
    """Enforce strict invariant: NEVER load data/test_v2*."""
    if path is None:
        return
    norm = str(path).lower().replace("\\", "/")
    if "test_v2" in norm:
        raise PermissionError(
            f"STRICT INVARIANT VIOLATION: Access denied to protected test_v2 path: {path}"
        )


def get_git_head_commit() -> str:
    """Retrieve git HEAD commit hash."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return res.stdout.strip()
    except Exception:
        return "unknown_head"


def parse_batch_identifier(batch_input: str) -> tuple[str, str]:
    """Extract batch stem (batch_NNN) and formatted number (NNN).

    Examples:
    'batch_001.jsonl' -> ('batch_001', '001')
    'batch_001' -> ('batch_001', '001')
    '001' -> ('batch_001', '001')
    """
    clean = Path(batch_input).stem
    m = re.search(r"(\d+)", clean)
    if m:
        num_str = f"{int(m.group(1)):03d}"
        stem = f"batch_{num_str}"
        return stem, num_str
    return clean, clean


def run_stress_eval(
    batch_arg: str,
    stress_dir: Path | str = "data/stress",
    results_dir: Path | str = "results",
    model_version: str | None = None,
) -> dict[str, Any]:
    """Execute blind stress evaluation on a batch.

    Refuses execution if batch is not in 'unmeasured' status.
    """
    stress_path = Path(stress_dir).resolve()
    results_base = Path(results_dir).resolve()
    assert_not_test_v2(stress_path)
    assert_not_test_v2(results_base)

    batch_stem, batch_num = parse_batch_identifier(batch_arg)
    batch_file = stress_path / f"{batch_stem}.jsonl"

    if not batch_file.exists():
        # Also check if user passed full relative path directly
        direct_p = Path(batch_arg).resolve()
        assert_not_test_v2(direct_p)
        if direct_p.exists():
            batch_file = direct_p
            batch_stem, batch_num = parse_batch_identifier(direct_p.name)
        else:
            raise FileNotFoundError(f"Stress batch file not found: {batch_file}")

    manifest_path = stress_path / "MANIFEST.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with open(manifest_path, encoding="utf-8") as f:
        manifest_data = json.load(f)

    batch_entry = manifest_data.get(batch_stem) or manifest_data.get(f"{batch_stem}.jsonl")
    if not batch_entry:
        raise ValueError(
            f"Batch '{batch_stem}' is not registered in manifest: {manifest_path}"
        )

    current_status = batch_entry.get("status")
    if current_status != "unmeasured":
        err_msg = (
            f"REFUSED: Second blind run prohibited on batch '{batch_stem}'. "
            f"Current status is '{current_status}'. Blind evaluation can only execute once on status 'unmeasured'."
        )
        sys.stderr.write(err_msg + "\n")
        raise RuntimeError(err_msg)

    # Load tickets
    tickets: list[dict[str, Any]] = []
    with open(batch_file, encoding="utf-8") as f:
        for _idx, line in enumerate(f, 1):
            s = line.strip()
            if not s:
                continue
            data = json.loads(s)
            tickets.append(data)

    if not tickets:
        raise ValueError(f"No tickets found in batch: {batch_file}")

    # Offline classifier (dev-trained Rules + ML)
    version = (
        model_version
        or getattr(settings, "offline_model_version", "v1")
    )
    provider = MockClassifierProvider(offline_model_version=version)
    model_id = f"rules_dialect_ml_{provider.version}"
    provider_path = "mock"

    results_dir_blind = results_base / f"stress_{batch_num}_blind"
    results_dir_blind.mkdir(parents=True, exist_ok=True)

    csv_records: list[dict[str, Any]] = []
    gold_counts: dict[str, int] = defaultdict(int)
    correct_counts: dict[str, int] = defaultdict(int)

    # Slice tracking
    tag_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    tag_correct: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    total_latency_ms = 0.0
    degraded_count = 0
    error_count = 0

    for item in tickets:
        ticket_id = (
            item.get("ticket", {}).get("ticket_id")
            or item.get("ticket_id")
            or "TKT-UNKNOWN"
        )
        raw_text = (
            item.get("ticket", {}).get("raw_text")
            or item.get("ticket", {}).get("text")
            or item.get("raw_text")
            or item.get("text")
            or ""
        )
        channel = item.get("ticket", {}).get("channel") or item.get("channel") or "app"
        gold = (
            item.get("label", {}).get("category")
            or item.get("category")
            or "unclear_or_incomplete"
        )
        tags = item.get("label", {}).get("tags") or item.get("tags") or {}

        gold_counts[gold] += 1
        t0 = time.perf_counter()
        pred = "unclear_or_incomplete"
        err_str = ""
        degraded = False

        try:
            res = provider.classify(ticket_text=raw_text, channel=channel, ticket_id=ticket_id)
            pred = res.category
            degraded = getattr(res, "degraded", False)
            if degraded:
                degraded_count += 1
        except Exception as e:
            error_count += 1
            err_str = f"InferenceError: {type(e).__name__}"

        latency_ms = (time.perf_counter() - t0) * 1000.0
        total_latency_ms += latency_ms

        is_correct = 1 if pred == gold else 0
        if is_correct:
            correct_counts[gold] += 1

        # Track tags
        if isinstance(tags, dict):
            for tag_k, tag_v in tags.items():
                val_str = str(tag_v)
                tag_counts[tag_k][val_str] += 1
                if is_correct:
                    tag_correct[tag_k][val_str] += 1

        csv_records.append({
            "ticket_id": ticket_id,
            "gold": gold,
            "pred": pred,
            "correct": is_correct,
            "provider_path": provider_path,
            "degraded": 1 if degraded else 0,
            "model_id": model_id,
            "latency_ms": round(latency_ms, 2),
            "error": err_str,
        })

    total_tickets = len(tickets)
    total_correct = sum(r["correct"] for r in csv_records)
    acc_point, ci_lower, ci_upper = compute_wilson_ci(
        correct=total_correct, total=total_tickets, confidence=0.95
    )
    avg_latency = total_latency_ms / total_tickets if total_tickets > 0 else 0.0

    # Write per_ticket.csv (STRICT SECURITY: Contains ZERO ticket text)
    csv_path = results_dir_blind / "per_ticket.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "ticket_id",
                "gold",
                "pred",
                "correct",
                "provider_path",
                "degraded",
                "model_id",
                "latency_ms",
                "error",
            ],
        )
        writer.writeheader()
        writer.writerows(csv_records)

    git_head = get_git_head_commit()
    now_iso = datetime.now(UTC).isoformat()

    # Build summary.md (STRICT SECURITY: Aggregates ONLY, NO ticket text)
    summary_lines = [
        f"# Stress Test Blind Evaluation Summary: {batch_stem}",
        "",
        f"- **Date**: `{now_iso}`",
        f"- **Git HEAD**: `{git_head}`",
        f"- **Batch File**: `{batch_file.name}`",
        f"- **Model**: `{model_id}` (Offline dev-trained Rules + ML)",
        f"- **Provider**: `{provider_path}` (Strictly offline, zero API calls)",
        "",
        "## Overall Performance",
        "",
        f"- **Total Tickets**: {total_tickets}",
        f"- **Correct Predictions**: {total_correct}",
        f"- **Overall Accuracy**: **{acc_point:.2%}**",
        f"- **Wilson 95% Confidence Interval**: `[{ci_lower:.4f}, {ci_upper:.4f}]` (`[{ci_lower * 100:.2f}%, {ci_upper * 100:.2f}%]`)",
        f"- **Average Latency**: {avg_latency:.2f} ms",
        f"- **Degraded Classifications**: {degraded_count}",
        f"- **Errors**: {error_count}",
        "",
        "## Per-Category Recall",
        "",
        "| Category | Total (Gold) | Correct | Recall |",
        "|---|---|---|---|",
    ]

    for cat in sorted(gold_counts.keys()):
        tot = gold_counts[cat]
        corr = correct_counts[cat]
        rec = corr / tot if tot > 0 else 0.0
        summary_lines.append(f"| `{cat}` | {tot} | {corr} | {rec:.2%} |")

    summary_lines.append("")

    if tag_counts:
        summary_lines.append("## Per-Tag Slice Performance")
        summary_lines.append("")
        for tag_k in sorted(tag_counts.keys()):
            summary_lines.append(f"### Slice: `{tag_k}`")
            summary_lines.append("")
            summary_lines.append("| Tag Value | Total | Correct | Accuracy |")
            summary_lines.append("|---|---|---|---|")
            for tag_v in sorted(tag_counts[tag_k].keys()):
                tot_v = tag_counts[tag_k][tag_v]
                corr_v = tag_correct[tag_k][tag_v]
                acc_v = corr_v / tot_v if tot_v > 0 else 0.0
                summary_lines.append(f"| `{tag_v}` | {tot_v} | {corr_v} | {acc_v:.2%} |")
            summary_lines.append("")

    summary_md_path = results_dir_blind / "summary.md"
    with open(summary_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines) + "\n")

    # Update manifest status to 'measured_blind'
    manifest_data[batch_stem]["status"] = "measured_blind"
    manifest_data[batch_stem]["measured_at"] = now_iso
    manifest_data[batch_stem]["git_commit"] = git_head
    manifest_data[batch_stem]["blind_accuracy"] = acc_point
    manifest_data[batch_stem]["blind_wilson_95_ci"] = [ci_lower, ci_upper]

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    # Print AGGREGATES ONLY to console
    print("\n=======================================================")
    print(f"STRESS BATCH BLIND EVALUATION: {batch_stem}")
    print("=======================================================")
    print(f"Git HEAD:         {git_head}")
    print(f"Total Tickets:    {total_tickets}")
    print(f"Correct:          {total_correct}/{total_tickets}")
    print(f"Overall Accuracy: {acc_point:.2%} (Wilson 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}])")
    print(f"Avg Latency:      {avg_latency:.2f} ms")
    print(f"Degraded:         {degraded_count}")
    print(f"Errors:           {error_count}")
    print("\n--- Per-Category Recall ---")
    for cat in sorted(gold_counts.keys()):
        tot = gold_counts[cat]
        corr = correct_counts[cat]
        rec = corr / tot if tot > 0 else 0.0
        print(f"  {cat:<30}: {corr:>3}/{tot:<3} ({rec:.2%})")

    if tag_counts:
        print("\n--- Per-Tag Slice Breakdown ---")
        for tag_k in sorted(tag_counts.keys()):
            print(f"[{tag_k}]")
            for tag_v in sorted(tag_counts[tag_k].keys()):
                tot_v = tag_counts[tag_k][tag_v]
                corr_v = tag_correct[tag_k][tag_v]
                acc_v = corr_v / tot_v if tot_v > 0 else 0.0
                print(f"  {tag_v:<25}: {corr_v:>3}/{tot_v:<3} ({acc_v:.2%})")

    print("\nOutput Files:")
    print(f"  Summary:     {summary_md_path}")
    print(f"  Per-Ticket:  {csv_path}")
    print(f"Manifest Updated: {batch_stem} -> 'measured_blind'")
    print("=======================================================\n")

    return {
        "batch_id": batch_stem,
        "total_tickets": total_tickets,
        "correct": total_correct,
        "accuracy": acc_point,
        "wilson_95_ci": [ci_lower, ci_upper],
        "summary_md": str(summary_md_path),
        "per_ticket_csv": str(csv_path),
        "git_commit": git_head,
        "status": "measured_blind",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Blind stress evaluation runner (offline only)")
    parser.add_argument("batch", type=str, help="Batch identifier (e.g. batch_001 or 001)")
    parser.add_argument(
        "--blind",
        action="store_true",
        default=True,
        help="Run in blind mode (aggregates only, zero ticket text)",
    )
    parser.add_argument(
        "--stress-dir",
        type=str,
        default="data/stress",
        help="Stress batch directory (default: data/stress)",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Directory to save evaluation results (default: results)",
    )
    parser.add_argument(
        "--model-version",
        type=str,
        default=None,
        help="Offline model version to evaluate (e.g. v1, v2, v3)",
    )

    args = parser.parse_args()

    try:
        run_stress_eval(
            batch_arg=args.batch,
            stress_dir=args.stress_dir,
            results_dir=args.results_dir,
            model_version=args.model_version,
        )
    except Exception as e:
        sys.stderr.write(f"\nStress evaluation failed: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
