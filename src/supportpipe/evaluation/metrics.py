"""Evaluation metrics computation for classification, extraction, escalation, and calibration."""

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats
from sklearn.metrics import classification_report, confusion_matrix, f1_score

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


def compute_bootstrap_confidence_intervals(
    y_true: list[str],
    y_pred: list[str],
    escalated_flags: list[bool],
    labels: list[str],
    n_resamples: int = 1000,
    confidence_level: float = 0.95,
    random_seed: int = 42,
) -> dict[str, dict[str, float]]:
    """Calculate 95% Bootstrap Confidence Intervals (1,000 resamples) for metrics.

    Computes point estimates, bootstrap means, and empirical percentiles for:
    - Overall Accuracy
    - Macro Avg F1
    - Auto-Handled Accuracy

    Returns:
        dict mapping metric name to {
            "point_estimate": float,
            "mean": float,
            "lower_ci": float,
            "upper_ci": float,
        }
    """
    n = len(y_true)
    if n == 0:
        return {}

    rng = np.random.RandomState(random_seed)
    alpha = (1.0 - confidence_level) / 2.0
    lower_pct = alpha * 100.0
    upper_pct = (1.0 - alpha) * 100.0

    # Point estimates on full dataset
    point_acc = sum(1 for yt, yp in zip(y_true, y_pred, strict=False) if yt == yp) / n
    point_f1 = float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0))
    auto_indices = [i for i, e in enumerate(escalated_flags) if not e]
    point_auto_acc = (
        sum(1 for i in auto_indices if y_true[i] == y_pred[i]) / len(auto_indices)
        if auto_indices
        else 0.0
    )

    boot_accs: list[float] = []
    boot_f1s: list[float] = []
    boot_auto_accs: list[float] = []

    for _ in range(n_resamples):
        sample_indices = rng.randint(0, n, size=n)
        yt_sample = [y_true[i] for i in sample_indices]
        yp_sample = [y_pred[i] for i in sample_indices]
        esc_sample = [escalated_flags[i] for i in sample_indices]

        # Accuracy
        acc_s = sum(1 for yt, yp in zip(yt_sample, yp_sample, strict=False) if yt == yp) / n
        boot_accs.append(acc_s)

        # Macro F1
        f1_s = float(f1_score(yt_sample, yp_sample, labels=labels, average="macro", zero_division=0))
        boot_f1s.append(f1_s)

        # Auto-handled accuracy
        non_esc = [i for i, e in enumerate(esc_sample) if not e]
        if non_esc:
            auto_acc_s = sum(1 for i in non_esc if yt_sample[i] == yp_sample[i]) / len(non_esc)
            boot_auto_accs.append(auto_acc_s)

    return {
        "overall_accuracy": {
            "point_estimate": round(point_acc, 4),
            "mean": round(float(np.mean(boot_accs)), 4),
            "lower_ci": round(float(np.percentile(boot_accs, lower_pct)), 4),
            "upper_ci": round(float(np.percentile(boot_accs, upper_pct)), 4),
        },
        "macro_f1": {
            "point_estimate": round(point_f1, 4),
            "mean": round(float(np.mean(boot_f1s)), 4),
            "lower_ci": round(float(np.percentile(boot_f1s, lower_pct)), 4),
            "upper_ci": round(float(np.percentile(boot_f1s, upper_pct)), 4),
        },
        "auto_handled_accuracy": {
            "point_estimate": round(point_auto_acc, 4),
            "mean": round(float(np.mean(boot_auto_accs)), 4) if boot_auto_accs else 0.0,
            "lower_ci": round(float(np.percentile(boot_auto_accs, lower_pct)), 4) if boot_auto_accs else 0.0,
            "upper_ci": round(float(np.percentile(boot_auto_accs, upper_pct)), 4) if boot_auto_accs else 0.0,
        },
    }


def validate_dataset_path(path: Path | str) -> Path:
    """Validate dataset path and strictly refuse to touch test.jsonl."""
    p = Path(path).resolve()
    normalized_str = str(p).lower().replace("\\", "/")

    # Burned holdout diagnostic set protection
    assert not (p.name == "test.jsonl" or "test.jsonl" in normalized_str), (
        f"Access denied: {p} is a burned diagnostic set and must NEVER be opened or used for cross-validation!"
    )
    if p.name == "test.jsonl" or "test.jsonl" in normalized_str:
        raise ValueError(
            f"Access denied: {p} is a burned diagnostic set and must NEVER be opened or used for cross-validation!"
        )

    if not p.exists():
        raise FileNotFoundError(f"Dataset path not found: {p}")

    return p


def compute_wilson_ci(correct: int, total: int, confidence: float = 0.95) -> tuple[float, float, float]:
    """Calculate the Wilson score confidence interval for a binomial proportion.

    Returns:
        (accuracy, lower_ci, upper_ci)
    """
    if total == 0:
        return 0.0, 0.0, 0.0
    p = correct / total
    z = float(scipy.stats.norm.ppf(1.0 - (1.0 - confidence) / 2.0))
    z2 = z * z
    denom = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denom
    margin = (z / denom) * math.sqrt((p * (1.0 - p) / total) + (z2 / (4.0 * total * total)))
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return round(p, 4), round(lower, 4), round(upper, 4)


def compute_paired_mcnemar(
    y_true: list[str],
    y_pred_base: list[str],
    y_pred_cand: list[str],
) -> tuple[float, float, bool]:
    """Paired McNemar test on identical out-of-fold predictions.

    Returns:
        (statistic, p_value, is_significant_at_05)
    """
    b = sum(1 for yt, yb, yc in zip(y_true, y_pred_base, y_pred_cand, strict=True) if yt == yb and yt != yc)
    c = sum(1 for yt, yb, yc in zip(y_true, y_pred_base, y_pred_cand, strict=True) if yt != yb and yt == yc)
    total_discordant = b + c
    if total_discordant == 0:
        return 0.0, 1.0, False

    if total_discordant < 25:
        res = scipy.stats.binomtest(b, total_discordant, 0.5)
        p_val = float(res.pvalue)
        stat = float(abs(b - c))
    else:
        stat = ((abs(b - c) - 1.0) ** 2) / total_discordant
        p_val = float(scipy.stats.chi2.sf(stat, df=1))

    return round(stat, 4), round(p_val, 4), p_val < 0.05

