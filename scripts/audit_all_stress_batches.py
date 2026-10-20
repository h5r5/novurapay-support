"""Audit runner for all stress batches (001 through 008)."""
import glob
import json
import time
from pathlib import Path

from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.evaluation.metrics import compute_wilson_ci


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="v9", help="Engine version (e.g. v9)")
    args = parser.parse_args()

    classifier = MockClassifierProvider(offline_model_version=args.version)
    version = getattr(classifier, "version", args.version)
    print(f"Classifier Engine: {version.upper()}")

    batches = sorted(glob.glob("data/stress/batch_*.jsonl"))
    total_tickets = 0
    correct_classifications = 0
    per_batch = {}

    start_t = time.perf_counter()

    for b_path in batches:
        b_name = Path(b_path).stem
        b_total = 0
        b_correct = 0
        with open(b_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                ticket_data = data["ticket"]
                label_data = data["label"]

                raw_text = ticket_data["raw_text"]
                pred = classifier.classify(raw_text)
                gold_cat = label_data["category"]

                if pred.category == gold_cat:
                    b_correct += 1
                    correct_classifications += 1
                b_total += 1
                total_tickets += 1

        b_acc = b_correct / b_total if b_total else 0
        per_batch[b_name] = {"total": b_total, "correct": b_correct, "accuracy": b_acc}

    elapsed = time.perf_counter() - start_t
    overall_acc = correct_classifications / total_tickets if total_tickets else 0
    _, ci_low, ci_high = compute_wilson_ci(correct_classifications, total_tickets)

    print("\n" + "=" * 55)
    print("           STRESS TEST BATCHES AUDIT (V9)")
    print("=" * 55)
    print(f"Total Batches Evaluated: {len(batches)}")
    print(f"Total Tickets:           {total_tickets}")
    print(f"Correct Classifications: {correct_classifications}/{total_tickets}")
    print(f"Overall Accuracy:        {overall_acc * 100:.2f}%")
    print(f"Wilson 95% CI:           [{ci_low * 100:.2f}%, {ci_high * 100:.2f}%]")
    print(f"Total Elapsed Time:      {elapsed:.2f}s ({elapsed / total_tickets * 1000:.2f}ms/ticket)")
    print("-" * 55)
    print("Per-Batch Breakdown:")
    for b, s in per_batch.items():
        tot = s["total"]
        cor = s["correct"]
        acc = s["accuracy"] * 100
        print(f"  - {b:12s}: {cor:3d}/{tot:3d} ({acc:6.2f}%)")
    print("=" * 55)

if __name__ == "__main__":
    main()
