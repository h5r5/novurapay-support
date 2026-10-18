"""CLI Runner for Evaluation Matrix Harness (Task C4 & C5).

Usage:
    python scripts/eval_harness.py --config offline_rule_ml_oof --split data/splits/dev.jsonl
    python scripts/eval_harness.py --config offline_rule_ml_insample --split data/splits/dev.jsonl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure root directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from supportpipe.evaluation.eval_harness import run_evaluation_harness


def main() -> None:
    parser = argparse.ArgumentParser(description="SupportPipe Model Matrix Evaluation Harness")
    parser.add_argument(
        "--matrix-config",
        type=str,
        default="configs/eval_matrix.yaml",
        help="Path to evaluation matrix YAML config",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="data/splits/dev.jsonl",
        help="Path to evaluation dataset (refuses test.jsonl)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/eval_matrix",
        help="Directory to save per_ticket.csv and summary.json",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Target config ID to evaluate (e.g., offline_rule_ml_oof, offline_rule_ml_insample)",
    )
    parser.add_argument(
        "--override-reason",
        type=str,
        default=None,
        help="Override reason required for re-running sealed test sets",
    )

    args = parser.parse_args()

    print("=== SupportPipe Evaluation Harness ===")
    print(f"Matrix Config: {args.matrix_config}")
    print(f"Dataset Split: {args.split}")
    print(f"Target Config: {args.config or 'ALL ACTIVE'}")
    print()

    summary = run_evaluation_harness(
        matrix_config_path=args.matrix_config,
        split_path=args.split,
        output_dir=args.output_dir,
        target_config_id=args.config,
        override_reason=args.override_reason,
    )

    print("\n=== Evaluation Summary Results ===")
    for cfg_id, res in summary.get("configs", {}).items():
        print(f"[{cfg_id}] {res.get('name')}")
        if res.get("notes"):
            print(f"  Notes:         {res.get('notes')}")
        print(f"  Accuracy:      {res.get('accuracy'):.4f} (Wilson 95% CI: [{res['wilson_95_ci'][0]:.4f}, {res['wilson_95_ci'][1]:.4f}])")
        print(f"  Correct:       {res.get('correct_count')}/{res.get('total_tickets')}")
        print(f"  Errors:        {res.get('error_count')}")
        print(f"  Degraded:      {res.get('degraded_count')}")
        print(f"  Avg Latency:   {res.get('avg_latency_ms'):.2f} ms")
        print(f"  Config Hash:   {res.get('config_hash')}")
        print(f"  CSV:           {res.get('csv_path')}")
        print()

    comparisons = summary.get("paired_mcnemar_comparisons", [])
    if comparisons:
        print("=== Paired McNemar Tests ===")
        for comp in comparisons:
            sig = "SIGNIFICANT (p < 0.05)" if comp["is_significant_at_05"] else "not significant"
            print(f"  {comp['config_a']} vs {comp['config_b']}: p={comp['p_value']:.4f} ({sig})")


if __name__ == "__main__":
    main()
