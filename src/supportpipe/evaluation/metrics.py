"""Evaluation metrics computation for classification, extraction, escalation, and calibration."""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

from supportpipe.schemas import LabeledTicket, PipelineResult


def compute_classification_metrics(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str],
) -> dict[str, Any]:
    """Compute overall accuracy, macro F1, and per-category metrics."""
    correct = sum(1 for yt, yp in zip(y_true, y_pred, strict=False) if yt == yp)
    total = len(y_true)
    accuracy = correct / total if total > 0 else 0.0

    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )

    conf_mat = confusion_matrix(y_true, y_pred, labels=labels)
    confusion_df = pd.DataFrame(conf_mat, index=labels, columns=labels)

    return {
        "accuracy": round(accuracy, 4),
        "total_evaluated": total,
        "classification_report": report,
        "confusion_matrix": confusion_df.to_dict(),
        "confusion_df": confusion_df,
    }


def compute_extraction_metrics(
    labeled_tickets: list[LabeledTicket],
    pipeline_results: list[PipelineResult],
) -> dict[str, Any]:
    """Compute exact match rate for transaction_ref, amount_iqd, and resolved event_date."""
    ref_matches = 0
    ref_applicable = 0

    amt_matches = 0
    amt_applicable = 0

    date_matches = 0
    date_applicable = 0

    for item, res in zip(labeled_tickets, pipeline_results, strict=False):
        exp = item.label.expected_fields
        got = res.extracted_fields

        # Transaction Ref
        if exp.transaction_ref is not None:
            ref_applicable += 1
            if got.transaction_ref == exp.transaction_ref:
                ref_matches += 1

        # Amount IQD
        if exp.amount_iqd is not None:
            amt_applicable += 1
            if got.amount_iqd == exp.amount_iqd:
                amt_matches += 1

        # Event Date Resolved
        if exp.event_date is not None:
            date_applicable += 1
            if got.event_date_resolved == exp.event_date:
                date_matches += 1

    return {
        "ref_exact_match_rate": round(ref_matches / ref_applicable, 4)
        if ref_applicable > 0
        else 1.0,
        "ref_evaluated_count": ref_applicable,
        "amt_exact_match_rate": round(amt_matches / amt_applicable, 4)
        if amt_applicable > 0
        else 1.0,
        "amt_evaluated_count": amt_applicable,
        "date_match_rate": round(date_matches / date_applicable, 4) if date_applicable > 0 else 1.0,
        "date_evaluated_count": date_applicable,
    }


def compute_calibration_buckets(
    confidences: list[float],
    y_true: list[str],
    y_pred: list[str],
    n_buckets: int = 5,
) -> list[dict[str, Any]]:
    """Bucket predictions by confidence decile/quintile to assess calibration."""
    correctness = [1 if yt == yp else 0 for yt, yp in zip(y_true, y_pred, strict=False)]
    bins = np.linspace(0.0, 1.0, n_buckets + 1)
    bucket_data = []

    for i in range(n_buckets):
        low, high = bins[i], bins[i + 1]
        indices = [
            j
            for j, c in enumerate(confidences)
            if (low <= c < high) or (i == n_buckets - 1 and low <= c <= high)
        ]
        if not indices:
            bucket_data.append(
                {
                    "range": f"{low:.1f}-{high:.1f}",
                    "count": 0,
                    "avg_confidence": round((low + high) / 2.0, 2),
                    "accuracy": 0.0,
                }
            )
            continue

        bucket_confs = [confidences[idx] for idx in indices]
        bucket_acc = [correctness[idx] for idx in indices]

        bucket_data.append(
            {
                "range": f"{low:.1f}-{high:.1f}",
                "count": len(indices),
                "avg_confidence": round(float(np.mean(bucket_confs)), 3),
                "accuracy": round(float(np.mean(bucket_acc)), 3),
            }
        )

    return bucket_data


def compute_escalation_slice_metrics(
    labeled_tickets: list[LabeledTicket],
    pipeline_results: list[PipelineResult],
) -> dict[str, Any]:
    """Compare accuracy on auto-handled (non-escalated) slice vs overall set."""
    overall_correct = 0
    auto_correct = 0
    auto_count = 0
    escalated_count = 0

    for item, res in zip(labeled_tickets, pipeline_results, strict=False):
        is_correct = item.label.category == res.category
        if is_correct:
            overall_correct += 1

        if not res.escalated:
            auto_count += 1
            if is_correct:
                auto_correct += 1
        else:
            escalated_count += 1

    total = len(labeled_tickets)
    overall_acc = overall_correct / total if total > 0 else 0.0
    auto_acc = auto_correct / auto_count if auto_count > 0 else 0.0

    return {
        "overall_accuracy": round(overall_acc, 4),
        "auto_handled_count": auto_count,
        "auto_handled_accuracy": round(auto_acc, 4),
        "accuracy_uplift": round(auto_acc - overall_acc, 4),
        "escalated_count": escalated_count,
        "escalation_rate_pct": round(escalated_count / total * 100.0, 2) if total > 0 else 0.0,
    }
