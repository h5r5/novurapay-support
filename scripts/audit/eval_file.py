"""Independent blind evaluation harness for arbitrary JSONL ticket batches.

Evaluates category classification and escalation metrics without assumptions
about predefined split names or dataset locations.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import classification_report, confusion_matrix

from supportpipe.config import settings
from supportpipe.pipeline import process_ticket
from supportpipe.schemas import LabeledTicket, Ticket
from supportpipe.taxonomy.loader import taxonomy


def evaluate_jsonl_file(
    file_path: Path,
    provider: str = "mock",
    mode: str = "offline",
) -> dict[str, Any]:
    """Evaluate an arbitrary JSONL dataset of customer tickets."""
    if not file_path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {file_path}")

    settings.llm_mode = mode.lower()  # type: ignore[assignment]

    records: list[tuple[Ticket, str, str]] = []
    with open(file_path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            raw = json.loads(line_str)
            if "label" in raw and "ticket" in raw:
                # LabeledTicket format
                lt = LabeledTicket.model_validate(raw)
                records.append((lt.ticket, lt.label.category, lt.label.priority))
            elif "category" in raw and ("raw_text" in raw or "text" in raw):
                # Flat labeled format
                txt = raw.get("raw_text") or raw.get("text")
                t = Ticket(
                    ticket_id=raw.get("ticket_id", f"TKT-BLIND-{line_no:04d}"),
                    raw_text=str(txt),
                    channel=raw.get("channel", "app"),
                    submitted_at=raw.get("submitted_at", "2026-10-01T12:00:00+03:00"),
                    synthetic_user_id=raw.get("synthetic_user_id", "SYN-BLIND"),
                )
                records.append((t, raw["category"], raw.get("priority", "medium")))
            elif "ticket" in raw:
                # ticket object with flat category label
                t_obj = Ticket.model_validate(raw["ticket"])
                cat = raw.get("category") or (raw.get("label", {}).get("category") if isinstance(raw.get("label"), dict) else "unknown")
                prio = raw.get("priority") or (raw.get("label", {}).get("priority") if isinstance(raw.get("label"), dict) else "medium")
                records.append((t_obj, cat, prio))
            else:
                raise ValueError(f"Line {line_no}: unparseable ticket record schema")

    if not records:
        raise ValueError(f"File {file_path} contained no valid records")

    y_true: list[str] = []
    y_pred: list[str] = []
    confidences: list[float] = []
    escalated_flags: list[bool] = []

    for ticket, exp_cat, _ in records:
        res = process_ticket(ticket, provider_override=provider)
        y_true.append(exp_cat)
        y_pred.append(res.category)
        confidences.append(res.category_confidence)
        escalated_flags.append(res.escalated)

    # Valid classes
    valid_categories = sorted(taxonomy.get_valid_category_ids())
    # Include any unexpected classes from ground truth or prediction
    all_classes = sorted(set(valid_categories) | set(y_true) | set(y_pred))

    # Compute overall accuracy
    correct = [t == p for t, p in zip(y_true, y_pred, strict=True)]
    overall_acc = sum(correct) / len(correct)

    # Classification report
    clf_report = classification_report(
        y_true=y_true,
        y_pred=y_pred,
        labels=all_classes,
        output_dict=True,
        zero_division=0,
    )

    # Confusion matrix
    cm = confusion_matrix(y_true=y_true, y_pred=y_pred, labels=all_classes)

    # Accuracy vs Coverage curve across confidence thresholds
    acc_vs_cov: list[dict[str, Any]] = []
    for thresh in np.arange(0.1, 1.0, 0.05):
        covered_indices = [i for i, c in enumerate(confidences) if c >= thresh]
        cov_pct = len(covered_indices) / len(records) * 100.0
        if covered_indices:
            cov_correct = sum(1 for i in covered_indices if correct[i])
            cov_acc = (cov_correct / len(covered_indices)) * 100.0
        else:
            cov_acc = 0.0
        acc_vs_cov.append({
            "threshold": round(float(thresh), 2),
            "coverage_pct": round(cov_pct, 2),
            "accuracy_on_covered_pct": round(cov_acc, 2),
            "covered_count": len(covered_indices),
        })

    # Auto-handled vs Escalated
    auto_handled_idx = [i for i, esc in enumerate(escalated_flags) if not esc]
    if auto_handled_idx:
        auto_acc = sum(1 for i in auto_handled_idx if correct[i]) / len(auto_handled_idx) * 100.0
    else:
        auto_acc = 0.0

    esc_rate = (sum(escalated_flags) / len(records)) * 100.0

    return {
        "file": str(file_path),
        "total_tickets": len(records),
        "overall_accuracy_pct": round(overall_acc * 100.0, 2),
        "macro_f1": round(clf_report["macro avg"]["f1-score"], 4),
        "auto_handled_accuracy_pct": round(auto_acc, 2),
        "escalation_rate_pct": round(esc_rate, 2),
        "all_classes": all_classes,
        "classification_report": clf_report,
        "confusion_matrix": cm.tolist(),
        "accuracy_vs_coverage": acc_vs_cov,
    }


def print_evaluation_summary(results: dict[str, Any]) -> None:
    """Print readable CLI evaluation summary."""
    print("=" * 70)
    print(f"BLIND EVALUATION RESULTS: {results['file']}")
    print(f"Total Tickets:             {results['total_tickets']}")
    print(f"Overall Accuracy:          {results['overall_accuracy_pct']}%")
    print(f"Macro Avg F1:              {results['macro_f1']}")
    print(f"Auto-Handled Accuracy:     {results['auto_handled_accuracy_pct']}%")
    print(f"Escalation Rate:           {results['escalation_rate_pct']}%")
    print("=" * 70)

    print("\nPER-CLASS PRECISION, RECALL & F1:")
    print(f"{'Category':<32} {'Precision':<10} {'Recall':<10} {'F1':<10} {'Support':<8}")
    print("-" * 70)
    cr = results["classification_report"]
    for cls in results["all_classes"]:
        if cls in cr and cr[cls]["support"] > 0:
            m = cr[cls]
            print(f"{cls:<32} {m['precision']:<10.3f} {m['recall']:<10.3f} {m['f1-score']:<10.3f} {int(m['support']):<8}")

    print("\nACCURACY VS COVERAGE (Confidence Threshold Sweep):")
    print(f"{'Threshold':<12} {'Coverage %':<15} {'Covered Accuracy %':<22} {'Covered Count'}")
    print("-" * 65)
    for row in results["accuracy_vs_coverage"]:
        print(f"{row['threshold']:<12.2f} {row['coverage_pct']:<15.1f} {row['accuracy_on_covered_pct']:<22.2f} {row['covered_count']}")

    print("\nCONFUSION MATRIX:")
    classes = results["all_classes"]
    cm = np.array(results["confusion_matrix"])
    # Print header
    header = "True \\ Pred".ljust(20) + " ".join(f"{c[:4]:>4}" for c in classes)
    print(header)
    for idx, c in enumerate(classes):
        row_str = f"{c[:18]:<20}" + " ".join(f"{val:>4}" for val in cm[idx])
        print(row_str)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate any JSONL dataset with SupportPipe")
    parser.add_argument("--file", "-f", type=Path, required=True, help="Path to JSONL ticket batch")
    parser.add_argument("--provider", "-p", default="mock", help="Classifier provider (mock, hybrid, etc.)")
    parser.add_argument("--mode", "-m", default="offline", choices=["offline", "live"], help="Execution mode")
    parser.add_argument("--json", action="store_true", help="Output raw JSON metrics instead of text")

    args = parser.parse_args()
    results = evaluate_jsonl_file(file_path=args.file, provider=args.provider, mode=args.mode)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_evaluation_summary(results)


if __name__ == "__main__":
    main()
