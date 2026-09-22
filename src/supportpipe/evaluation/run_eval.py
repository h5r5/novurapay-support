"""Evaluation runner executing benchmarks on dev and held-out test splits."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import pandas as pd
from supportpipe.config import settings
from supportpipe.datagen.splits import compute_sha256
from supportpipe.evaluation.metrics import (
    compute_calibration_buckets,
    compute_classification_metrics,
    compute_escalation_slice_metrics,
    compute_extraction_metrics,
)
from supportpipe.pipeline import process_ticket
from supportpipe.schemas import LabeledTicket, PipelineResult, RunManifest
from supportpipe.taxonomy.loader import taxonomy


def load_split(split_name: str) -> tuple[list[LabeledTicket], str]:
    """Load split from disk and verify its hash against data/manifest.json."""
    manifest_path = settings.data_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}. Run splits.py first.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    split_meta = manifest.get("splits", {}).get(split_name)
    if not split_meta:
        raise ValueError(f"Split '{split_name}' not defined in manifest.json")

    split_file = settings.project_root / split_meta["file"]
    if not split_file.exists():
        raise FileNotFoundError(f"Split file missing: {split_file}")

    actual_hash = compute_sha256(split_file)
    expected_hash = split_meta["sha256"]

    if actual_hash != expected_hash:
        raise ValueError(
            f"FROZEN SPLIT HASH MISMATCH for '{split_name}'!\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {actual_hash}\n"
            f"The test set must remain strictly frozen and unaltered."
        )

    tickets: list[LabeledTicket] = []
    with open(split_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                tickets.append(LabeledTicket.model_validate_json(line))

    return tickets, actual_hash


def execute_evaluation(split: str = "test", provider_name: str | None = None) -> dict[str, Any]:
    """Run full evaluation suite on the designated split."""
    labeled_tickets, dataset_hash = load_split(split)

    run_id = f"eval_{split}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    run_dir = settings.results_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results: list[PipelineResult] = []
    start_eval_time = time.perf_counter()

    for item in labeled_tickets:
        res = process_ticket(item.ticket)
        results.append(res)

    total_eval_time = time.perf_counter() - start_eval_time

    # 1. Classification Metrics
    valid_cats = taxonomy.get_valid_category_ids()
    y_true_cat = [item.label.category for item in labeled_tickets]
    y_pred_cat = [res.category for res in results]
    cat_metrics = compute_classification_metrics(y_true_cat, y_pred_cat, valid_cats)

    # 2. Priority Metrics
    y_true_prio = [item.label.priority for item in labeled_tickets]
    y_pred_prio = [res.priority for res in results]
    prio_correct = sum(1 for yt, yp in zip(y_true_prio, y_pred_prio, strict=False) if yt == yp)
    prio_acc = prio_correct / len(y_true_prio) if y_true_prio else 0.0

    # 3. Extraction Metrics
    ext_metrics = compute_extraction_metrics(labeled_tickets, results)

    # 4. Calibration Check
    confidences = [res.category_confidence for res in results]
    calibration = compute_calibration_buckets(confidences, y_true_cat, y_pred_cat, n_buckets=5)

    # 5. Escalation Behaviour & Slice Accuracy
    escalation_metrics = compute_escalation_slice_metrics(labeled_tickets, results)

    # 6. Baseline Comparison (Majority class)
    most_common_cat = max(set(y_true_cat), key=y_true_cat.count)
    majority_correct = sum(1 for yt in y_true_cat if yt == most_common_cat)
    baseline_acc = majority_correct / len(y_true_cat) if y_true_cat else 0.0

    # 7. Throughput & Latency
    latencies = [res.latency_ms for res in results]
    throughput_metrics = {
        "total_tickets": len(results),
        "wall_clock_seconds": round(total_eval_time, 3),
        "tickets_per_second": round(len(results) / total_eval_time, 1) if total_eval_time > 0 else 0.0,
        "avg_latency_ms": round(float(pd.Series(latencies).mean()), 2),
        "p95_latency_ms": round(float(pd.Series(latencies).quantile(0.95)), 2),
    }

    # Consolidated Metrics Dictionary
    consolidated_metrics = {
        "run_id": run_id,
        "split": split,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "baseline": {
            "majority_class_category": most_common_cat,
            "majority_class_accuracy": round(baseline_acc, 4),
        },
        "classification": {
            "overall_accuracy": cat_metrics["accuracy"],
            "priority_accuracy": round(prio_acc, 4),
            "macro_avg_f1": round(cat_metrics["classification_report"]["macro avg"]["f1-score"], 4),
            "per_category": {
                cat: {
                    "precision": round(cat_metrics["classification_report"][cat]["precision"], 3),
                    "recall": round(cat_metrics["classification_report"][cat]["recall"], 3),
                    "f1": round(cat_metrics["classification_report"][cat]["f1-score"], 3),
                    "support": cat_metrics["classification_report"][cat]["support"],
                }
                for cat in valid_cats
                if cat in cat_metrics["classification_report"]
            },
        },
        "extraction": ext_metrics,
        "escalation": escalation_metrics,
        "calibration": calibration,
        "throughput": throughput_metrics,
    }

    # Write metrics.json
    metrics_path = run_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(consolidated_metrics, f, ensure_ascii=False, indent=2)

    # Write confusion matrix CSV
    confusion_path = run_dir / "confusion.csv"
    cat_metrics["confusion_df"].to_csv(confusion_path, encoding="utf-8-sig")

    # Write per-ticket CSV
    per_ticket_rows = []
    for item, res in zip(labeled_tickets, results, strict=False):
        per_ticket_rows.append({
            "ticket_id": item.ticket.ticket_id,
            "raw_text": item.ticket.raw_text,
            "true_category": item.label.category,
            "pred_category": res.category,
            "category_correct": item.label.category == res.category,
            "category_confidence": res.category_confidence,
            "true_priority": item.label.priority,
            "pred_priority": res.priority,
            "priority_correct": item.label.priority == res.priority,
            "priority_confidence": res.priority_confidence,
            "team": res.team,
            "escalated": res.escalated,
            "escalation_reason": res.escalation_reason,
            "edge_case": item.label.edge_case,
            "latency_ms": res.latency_ms,
        })
    per_ticket_df = pd.DataFrame(per_ticket_rows)
    per_ticket_path = run_dir / "per_ticket.csv"
    per_ticket_df.to_csv(per_ticket_path, index=False, encoding="utf-8-sig")

    # Write run_meta.json
    run_meta = RunManifest(
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        git_commit="HEAD",
        split=split,
        dataset_hash=dataset_hash,
        model_id=settings.llm_mode,
        provider="supportpipe",
        config_hash="sha256_config",
        additional_metadata={"total_evaluated": len(results)},
    )
    with open(run_dir / "run_meta.json", "w", encoding="utf-8") as f:
        json.dump(run_meta.model_dump(), f, ensure_ascii=False, indent=2)

    return consolidated_metrics
