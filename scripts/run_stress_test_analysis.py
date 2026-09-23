"""Adversarial stress test runner and weakness analyzer for SupportPipe."""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from supportpipe.config import settings
from supportpipe.pipeline import process_ticket
from supportpipe.schemas import LabeledTicket

# Ensure stress test runs in fast deterministic offline mode
settings.llm_mode = "offline"


def evaluate_adversarial_set(provider: str = "mock") -> dict[str, Any]:
    dataset_path = Path("data/stress_test_100_adversarial.jsonl")
    if not dataset_path.exists():
        raise FileNotFoundError(f"Adversarial dataset not found at {dataset_path}")

    labeled_tickets: list[LabeledTicket] = []
    with open(dataset_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                labeled_tickets.append(LabeledTicket.model_validate_json(line))

    total = len(labeled_tickets)
    cat_correct = 0
    ref_correct = 0
    ref_total_expected = 0
    amt_correct = 0
    amt_total_expected = 0
    date_correct = 0
    date_total_expected = 0

    results = []
    failures = []

    for item in labeled_tickets:
        ticket = item.ticket
        label = item.label

        res = process_ticket(ticket, provider_override=provider)

        # Classification check
        is_cat_match = res.category == label.category
        if is_cat_match:
            cat_correct += 1

        # Ref check
        exp_ref = label.expected_fields.transaction_ref
        pred_ref = res.extracted_fields.transaction_ref
        is_ref_match = True
        if exp_ref is not None:
            ref_total_expected += 1
            if pred_ref is not None:
                exp_clean = exp_ref.lower().replace(" ", "").replace("-", "")
                pred_clean = pred_ref.lower().replace(" ", "").replace("-", "")
                is_ref_match = (exp_clean in pred_clean) or (pred_clean in exp_clean)
            else:
                is_ref_match = False

            if is_ref_match:
                ref_correct += 1

        # Amount check
        exp_amt = label.expected_fields.amount_iqd if label.expected_fields.currency == "IQD" else label.expected_fields.amount_usd
        pred_amt = res.extracted_fields.amount_iqd if res.extracted_fields.currency == "IQD" else res.extracted_fields.amount_usd
        is_amt_match = True
        if exp_amt is not None:
            amt_total_expected += 1
            if pred_amt is not None:
                diff_ratio = abs(pred_amt - exp_amt) / max(exp_amt, 1)
                is_amt_match = diff_ratio < 0.05
            else:
                is_amt_match = False

            if is_amt_match:
                amt_correct += 1

        # Date check
        exp_date = label.expected_fields.event_date
        pred_date = res.extracted_fields.event_date_resolved
        is_date_match = True
        if exp_date is not None:
            date_total_expected += 1
            is_date_match = (pred_date == exp_date)
            if is_date_match:
                date_correct += 1

        record = {
            "ticket_id": ticket.ticket_id,
            "edge_case": label.edge_case,
            "raw_text": ticket.raw_text,
            "expected_cat": label.category,
            "pred_cat": res.category,
            "cat_match": is_cat_match,
            "expected_ref": exp_ref,
            "pred_ref": pred_ref,
            "ref_match": is_ref_match,
            "expected_amt": exp_amt,
            "pred_amt": pred_amt,
            "amt_match": is_amt_match,
            "expected_date": exp_date,
            "pred_date": pred_date,
            "date_match": is_date_match,
            "escalated": res.escalated,
            "escalation_reason": res.escalation_reason,
            "confidence": res.category_confidence,
            "audit_status": res.audit_status,
        }
        results.append(record)

        if not (is_cat_match and is_ref_match and is_amt_match and is_date_match):
            failures.append(record)

    summary = {
        "provider": provider,
        "total_tickets": total,
        "category_accuracy": round(cat_correct / total * 100, 2),
        "ref_accuracy": round(ref_correct / max(ref_total_expected, 1) * 100, 2),
        "ref_evaluated": ref_total_expected,
        "amount_accuracy": round(amt_correct / max(amt_total_expected, 1) * 100, 2),
        "amount_evaluated": amt_total_expected,
        "date_accuracy": round(date_correct / max(date_total_expected, 1) * 100, 2),
        "date_evaluated": date_total_expected,
        "total_failures": len(failures),
        "total_escalated": sum(1 for r in results if r["escalated"]),
    }

    # Save detailed CSV
    out_dir = Path("results/adversarial_stress_test")
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(out_dir / f"adversarial_results_{provider}.csv", index=False, encoding="utf-8-sig")

    with open(out_dir / f"adversarial_summary_{provider}.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return {"summary": summary, "failures": failures}


if __name__ == "__main__":
    res = evaluate_adversarial_set("mock")
    print("\n================ ADVERSARIAL STRESS TEST SUMMARY (OFFLINE SYSTEM 1) ================")
    for k, v in res["summary"].items():
        print(f"{k}: {v}")
    print(f"\nTotal Flawed/Broken Tickets: {len(res['failures'])} / {res['summary']['total_tickets']}")
