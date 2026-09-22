"""15-Ticket Spike Runner for TypeSafe AI Jev 1.13 Evaluation (Brief Section 7.5)."""

import json
import time

from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.schemas import LabeledTicket


def run_spike(num_tickets: int = 15) -> dict:
    """Run comparative 15-ticket spike on dev split between Jev 1.13 and Mock."""
    dev_path = settings.data_dir / "splits" / "dev.jsonl"
    if not dev_path.exists():
        raise FileNotFoundError(f"Dev split not found: {dev_path}")

    all_tickets: list[LabeledTicket] = []
    with open(dev_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_tickets.append(LabeledTicket.model_validate_json(line))

    # Select diverse tickets across distinct categories and edge cases
    seen_cats = set()
    selected: list[LabeledTicket] = []
    for item in all_tickets:
        cat = item.label.category
        if cat not in seen_cats and len(selected) < num_tickets:
            seen_cats.add(cat)
            selected.append(item)

    # Fill remaining if needed
    for item in all_tickets:
        if len(selected) >= num_tickets:
            break
        if item not in selected:
            selected.append(item)

    jev = JevClassifierProvider()
    mock = MockClassifierProvider()

    rows = []
    jev_correct_cat = 0
    jev_correct_prio = 0
    mock_correct_cat = 0
    mock_correct_prio = 0
    jev_latencies = []

    print(f"\n================ Running {len(selected)}-Ticket Spike with Jev 1.13 ================")

    for i, item in enumerate(selected, 1):
        t = item.ticket
        lbl = item.label

        # 1. Run Jev Live
        t0 = time.perf_counter()
        try:
            res_jev = jev.classify(ticket_text=t.raw_text, channel=t.channel)
            lat = (time.perf_counter() - t0) * 1000.0
            jev_latencies.append(lat)
            jev_cat_ok = res_jev.category == lbl.category
            jev_prio_ok = res_jev.priority == lbl.priority
            if jev_cat_ok:
                jev_correct_cat += 1
            if jev_prio_ok:
                jev_correct_prio += 1
        except Exception as e:
            lat = 0.0
            jev_cat_ok = False
            jev_prio_ok = False
            print(f"Error on ticket {t.ticket_id}: {e}")
            continue

        # 2. Run Mock
        res_mock = mock.classify(ticket_text=t.raw_text, channel=t.channel)
        mock_cat_ok = res_mock.category == lbl.category
        mock_prio_ok = res_mock.priority == lbl.priority
        if mock_cat_ok:
            mock_correct_cat += 1
        if mock_prio_ok:
            mock_correct_prio += 1

        rows.append(
            {
                "idx": i,
                "ticket_id": t.ticket_id,
                "text": t.raw_text[:40] + ("..." if len(t.raw_text) > 40 else ""),
                "true_cat": lbl.category,
                "jev_cat": res_jev.category,
                "jev_cat_conf": res_jev.category_confidence,
                "jev_cat_match": "✅" if jev_cat_ok else "❌",
                "mock_cat": res_mock.category,
                "mock_cat_match": "✅" if mock_cat_ok else "❌",
                "true_prio": lbl.priority,
                "jev_prio": res_jev.priority,
                "jev_prio_conf": res_jev.priority_confidence,
                "jev_prio_match": "✅" if jev_prio_ok else "❌",
                "latency_ms": round(lat, 1),
            }
        )

    avg_lat = sum(jev_latencies) / len(jev_latencies) if jev_latencies else 0.0
    jev_cat_acc = (jev_correct_cat / len(selected)) * 100.0
    jev_prio_acc = (jev_correct_prio / len(selected)) * 100.0
    mock_cat_acc = (mock_correct_cat / len(selected)) * 100.0
    mock_prio_acc = (mock_correct_prio / len(selected)) * 100.0

    summary = {
        "num_tickets": len(selected),
        "jev_cat_acc": round(jev_cat_acc, 2),
        "jev_prio_acc": round(jev_prio_acc, 2),
        "mock_cat_acc": round(mock_cat_acc, 2),
        "mock_prio_acc": round(mock_prio_acc, 2),
        "avg_latency_ms": round(avg_lat, 1),
        "rows": rows,
    }

    # Print summary table
    print(f"\nResults Summary across {len(selected)} Tickets:")
    print(
        f"- Jev 1.13 Category Accuracy: {jev_cat_acc:.1f}% (vs Offline Mock: {mock_cat_acc:.1f}%)"
    )
    print(
        f"- Jev 1.13 Priority Accuracy: {jev_prio_acc:.1f}% (vs Offline Mock: {mock_prio_acc:.1f}%)"
    )
    print(f"- Jev 1.13 Average Latency:   {avg_lat:.1f} ms per decision")

    # Save artifact
    out_file = settings.results_dir / "spike_jev_results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    return summary


if __name__ == "__main__":
    run_spike(15)
