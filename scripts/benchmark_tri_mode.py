"""Benchmark comparison: MOCK 13 vs JEV vs MOCK+JEV Waterfall.

Measures Speed (latency, throughput), Cost (calls, USD, cost/1k),
and Accuracy (classification correctness against ground truth).
Strictly uses only Mock v13 and Jev (no Gemini, no Groq).
Supports multi-threaded execution for high throughput.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import logging
import sys
import threading
import time
from pathlib import Path
from typing import Any

from supportpipe.classify.providers.hybrid_provider import HybridClassifierProvider
from supportpipe.classify.providers.jev_provider import JevClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.extract.extract import extract_ticket_details

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Unit economic constants (derived from actual TypeSafe billing: $0.07 / 1,041 calls)
JEV_COST_PER_CALL_USD = 0.000067243


def load_dev_tickets(limit: int | None = None) -> list[dict[str, Any]]:
    dev_path = Path("data/splits/dev.jsonl")
    if not dev_path.exists():
        raise FileNotFoundError(f"Missing {dev_path}")

    tickets: list[dict[str, Any]] = []
    with open(dev_path, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            rec = json.loads(line_str)
            t_data = rec.get("ticket", {})
            l_data = rec.get("label", {})
            tickets.append(
                {
                    "ticket_id": t_data.get("ticket_id"),
                    "channel": t_data.get("channel", "app"),
                    "raw_text": t_data.get("raw_text", ""),
                    "submitted_at": t_data.get("submitted_at", "2026-09-08T12:00:00Z"),
                    "gold_category": l_data.get("category"),
                    "gold_priority": l_data.get("priority", "medium"),
                }
            )
            if limit and len(tickets) >= limit:
                break
    return tickets


def load_stress_tickets(limit: int | None = None) -> list[dict[str, Any]]:
    stress_dir = Path("data/stress")
    files = sorted(stress_dir.glob("batch_*.jsonl"))
    tickets: list[dict[str, Any]] = []

    for f_path in files:
        with open(f_path, encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                rec = json.loads(line_str)
                t_data = rec.get("ticket", {})
                l_data = rec.get("label", {})
                tickets.append(
                    {
                        "ticket_id": t_data.get("ticket_id"),
                        "channel": t_data.get("channel", "app"),
                        "raw_text": t_data.get("raw_text", ""),
                        "submitted_at": t_data.get("submitted_at", "2026-09-08T12:00:00Z"),
                        "gold_category": l_data.get("category"),
                        "gold_priority": l_data.get("priority", "medium"),
                    }
                )
                if limit and len(tickets) >= limit:
                    return tickets
    return tickets


class ThreadSafeCountingJevProvider(JevClassifierProvider):
    """JevClassifierProvider with thread-safe live call counter."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.call_count = 0
        self._lock = threading.Lock()

    def classify(self, ticket_text: str, channel: str = "app", fast_extracted: Any = None, **kwargs: Any):
        with self._lock:
            self.call_count += 1
        return super().classify(ticket_text, channel=channel, fast_extracted=fast_extracted, **kwargs)


def process_single_ticket(idx: int, t: dict[str, Any], classify_fn: Any) -> tuple[int, dict[str, Any]]:
    raw_text = t["raw_text"]
    channel = t["channel"]
    gold_cat = t["gold_category"]

    ext = extract_ticket_details(raw_text, t["submitted_at"], channel)
    t0 = time.perf_counter()
    try:
        res = classify_fn(ticket_text=raw_text, channel=channel, fast_extracted=ext)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        is_correct = (res.category == gold_cat)
        return idx, {
            "ticket_id": t["ticket_id"],
            "gold": gold_cat,
            "pred": res.category,
            "conf": res.category_confidence,
            "correct": is_correct,
            "latency_ms": dt_ms,
            "reasoning": getattr(res, "reasoning_summary", ""),
        }
    except Exception as e:
        dt_ms = (time.perf_counter() - t0) * 1000.0
        return idx, {
            "ticket_id": t["ticket_id"],
            "gold": gold_cat,
            "pred": "error",
            "conf": 0.0,
            "correct": False,
            "latency_ms": dt_ms,
            "reasoning": f"Exception: {e}",
        }


def run_engine_benchmark(
    name: str,
    classify_fn: Any,
    tickets: list[dict[str, Any]],
    jev_tracker: ThreadSafeCountingJevProvider | None = None,
    workers: int = 1,
) -> dict[str, Any]:
    print(f"\n[RUNNING] Benchmark for: {name} ({len(tickets)} tickets, workers={workers})...")
    start_calls = jev_tracker.call_count if jev_tracker else 0
    t0_wall = time.perf_counter()

    results_by_idx: dict[int, dict[str, Any]] = {}
    total_tickets = len(tickets)
    completed = 0

    if workers <= 1:
        for idx, t in enumerate(tickets):
            _, res = process_single_ticket(idx, t, classify_fn)
            results_by_idx[idx] = res
            completed += 1
            if completed % 250 == 0 or completed == total_tickets:
                cur_correct = sum(1 for r in results_by_idx.values() if r["correct"])
                acc = (cur_correct / completed) * 100.0
                print(f"  Processed {completed}/{total_tickets} tickets | Accuracy: {acc:.2f}%")
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_idx = {
                executor.submit(process_single_ticket, idx, t, classify_fn): idx
                for idx, t in enumerate(tickets)
            }
            for fut in concurrent.futures.as_completed(future_to_idx):
                idx, res = fut.result()
                results_by_idx[idx] = res
                completed += 1
                if completed % 250 == 0 or completed == total_tickets:
                    cur_correct = sum(1 for r in results_by_idx.values() if r["correct"])
                    acc = (cur_correct / completed) * 100.0
                    print(f"  Processed {completed}/{total_tickets} tickets | Accuracy: {acc:.2f}%")

    total_wall_sec = time.perf_counter() - t0_wall
    end_calls = jev_tracker.call_count if jev_tracker else 0
    jev_calls = end_calls - start_calls
    total_cost_usd = jev_calls * JEV_COST_PER_CALL_USD

    # Reconstruct in original order
    predictions = [results_by_idx[i] for i in range(total_tickets)]
    latencies = [p["latency_ms"] for p in predictions]
    correct_count = sum(1 for p in predictions if p["correct"])

    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)
    avg_latency = sum(latencies) / n if n > 0 else 0.0
    p50_latency = sorted_latencies[int(n * 0.50)] if n > 0 else 0.0
    p95_latency = sorted_latencies[int(n * 0.95)] if n > 0 else 0.0
    min_latency = sorted_latencies[0] if n > 0 else 0.0
    max_latency = sorted_latencies[-1] if n > 0 else 0.0

    accuracy_pct = (correct_count / total_tickets) * 100.0 if total_tickets else 0.0
    throughput = total_tickets / total_wall_sec if total_wall_sec > 0 else 0.0

    return {
        "engine": name,
        "total_tickets": total_tickets,
        "correct_predictions": correct_count,
        "accuracy_pct": round(accuracy_pct, 2),
        "total_wall_seconds": round(total_wall_sec, 2),
        "throughput_tps": round(throughput, 2),
        "avg_latency_ms": round(avg_latency, 2),
        "p50_latency_ms": round(p50_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "min_latency_ms": round(min_latency, 2),
        "max_latency_ms": round(max_latency, 2),
        "jev_calls": jev_calls,
        "total_cost_usd": round(total_cost_usd, 6),
        "cost_per_1k_usd": round((total_cost_usd / total_tickets) * 1000.0, 4) if total_tickets else 0.0,
        "predictions": predictions,
    }


def main() -> None:
    if sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run 3-mode benchmark on full stress/dev dataset")
    parser.add_argument("--dataset", choices=["dev", "stress"], default="stress", help="Dataset to evaluate on")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of tickets to evaluate")
    parser.add_argument("--threshold", type=float, default=0.95, help="Waterfall confidence threshold (default: 0.95)")
    parser.add_argument("--workers", type=int, default=12, help="Number of concurrent worker threads for network calls")
    parser.add_argument("--engine", choices=["all", "mock", "jev", "waterfall"], default="all", help="Engine to run")
    args = parser.parse_args()

    print("=" * 75)
    print("TRI-MODE FINTECH ENGINE BENCHMARK: MOCK 13 vs JEV vs MOCK+JEV WATERFALL")
    print("=" * 75)

    # 1. Load dataset
    if args.dataset == "dev":
        tickets = load_dev_tickets(limit=args.limit)
        dataset_name = f"Development Gold Set ({len(tickets):,} tickets)"
    else:
        tickets = load_stress_tickets(limit=args.limit)
        dataset_name = f"Complete Stress Test Set ({len(tickets):,} tickets across 20 batches)"

    print(f"Target Dataset: {dataset_name}")
    print(f"Waterfall Confidence Threshold: {args.threshold:.2f}")
    print(f"Worker Threads: {args.workers}")
    print(f"Selected Engine: {args.engine}")

    cache_file = Path("reports") / f"benchmark_cache_{args.dataset}_{len(tickets)}.json"
    cached_data: dict[str, Any] = {}
    if cache_file.exists():
        try:
            with open(cache_file, encoding="utf-8") as cf:
                cached_data = json.load(cf)
        except Exception:
            cached_data = {}

    def save_to_cache(key: str, data: dict[str, Any]) -> None:
        saveable = {k: v for k, v in data.items() if k != "predictions"}
        cached_data[key] = saveable
        cache_file.parent.mkdir(exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as cf:
            json.dump(cached_data, cf, indent=2)

    # 2. Instantiate engines
    mock_provider = MockClassifierProvider(offline_model_version="v13")
    jev_tracker = ThreadSafeCountingJevProvider()

    # Pure Waterfall composed STRICTLY of Mock v13 + Jev (No Gemini, No Groq)
    waterfall_provider = HybridClassifierProvider(
        mock_provider=mock_provider,
        jev_provider=jev_tracker,
        gemini_provider=None,
        groq_provider=None,
        audit_sampling_rate=0.0,
        confidence_threshold=args.threshold,
    )

    # Mode 1: Pure Mock v13
    if args.engine in ["all", "mock"]:
        res_mock = run_engine_benchmark(
            name="MOCK 13 (Local Rules + ML)",
            classify_fn=mock_provider.classify,
            tickets=tickets,
            jev_tracker=None,
            workers=min(args.workers, 4),
        )
        save_to_cache("mock", res_mock)
    else:
        res_mock = cached_data.get("mock", {})

    # Mode 2: Pure JEV 1.13
    if args.engine in ["all", "jev"]:
        res_jev = run_engine_benchmark(
            name="JEV 1.13 (TypeSafe AI Cloud)",
            classify_fn=jev_tracker.classify,
            tickets=tickets,
            jev_tracker=jev_tracker,
            workers=args.workers,
        )
        save_to_cache("jev", res_jev)
    else:
        res_jev = cached_data.get("jev", {})

    # Mode 3: MOCK + JEV Waterfall
    if args.engine in ["all", "waterfall"]:
        res_waterfall = run_engine_benchmark(
            name=f"MOCK + JEV Waterfall (Threshold: {args.threshold:.2f})",
            classify_fn=lambda **kwargs: waterfall_provider.classify(force_audit=False, **kwargs),
            tickets=tickets,
            jev_tracker=jev_tracker,
            workers=args.workers,
        )
        save_to_cache("waterfall", res_waterfall)
    else:
        res_waterfall = cached_data.get("waterfall", {})

    # 3. Print Comparison Table
    print("\n" + "=" * 80)
    print("FINAL BENCHMARK COMPARISON MATRIX (FULL RUN)")
    print("=" * 80)

    results = [res_mock, res_jev, res_waterfall]

    header = f"{'Engine':<32} | {'Accuracy':<10} | {'Avg Latency':<12} | {'P95 Latency':<12} | {'Jev Calls':<10} | {'Total Cost':<12} | {'Cost/1k'}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(
            f"{r['engine']:<32} | "
            f"{r['accuracy_pct']:>8.2f}% | "
            f"{r['avg_latency_ms']:>9.2f} ms | "
            f"{r['p95_latency_ms']:>9.2f} ms | "
            f"{r['jev_calls']:>10d} | "
            f"${r['total_cost_usd']:>10.5f} | "
            f"${r['cost_per_1k_usd']:>6.4f}"
        )

    # 4. Save markdown report for README
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / "benchmark_mock_vs_jev_waterfall_4321.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# تقرير المقارنة المعيارية الشامل: MOCK 13 مقابل JEV مقابل MOCK+JEV الشلال\n\n")
        f.write(f"- **مجموعة البيانات المفحوصة:** {dataset_name}\n")
        f.write(f"- **إجمالي التذاكر المفحوصة:** {len(tickets):,}\n")
        f.write(f"- **عتبة الشلال (Confidence Threshold):** {args.threshold:.2f}\n")
        f.write("- **معمارية الشلال:** محركان حصراً (Mock 13 محلي + Jev 1.13 سحابي)\n\n")

        f.write("## 1. جدول المقارنة الشامل (Speed, Cost, Accuracy)\n\n")
        f.write("| المحرك | الدقة الكلية (%) | متوسط زمن المعالجة (ms) | زمن P95 (ms) | معدل التدفق (Ticket/s) | استدعاءات Jev السحابية | التكلفة الإجمالية ($) | تكلفة كل 1,000 تذكرة ($) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in results:
            f.write(
                f"| **{r['engine']}** | "
                f"{r['accuracy_pct']:.2f}% | "
                f"{r['avg_latency_ms']:.2f} ms | "
                f"{r['p95_latency_ms']:.2f} ms | "
                f"{r['throughput_tps']:.2f} | "
                f"{r['jev_calls']:,} | "
                f"${r['total_cost_usd']:.5f} | "
                f"${r['cost_per_1k_usd']:.4f} |\n"
            )

        f.write("\n## 2. تحليل الكفاءة الهندسية والاقتصادية للشلال\n\n")
        jev_calls = res_jev["jev_calls"]
        wf_calls = res_waterfall["jev_calls"]

        saving_ratio = ((jev_calls - wf_calls) / jev_calls * 100.0) if jev_calls > 0 else 0.0
        fast_exit_ratio = ((len(tickets) - wf_calls) / len(tickets) * 100.0) if tickets else 0.0

        f.write(f"- **نسبة التذاكر المحسومة محلياً فوراً (Fast-Exit at Stage 1):** {fast_exit_ratio:.2f}% ({len(tickets) - wf_calls:,} تذكرة بـ 0.00$ و 0 ms)\n")
        f.write(f"- **نسبة التذاكر المحولة إلى سحابة Jev (Escalated to Stage 2):** {(100.0 - fast_exit_ratio):.2f}% ({wf_calls:,} تذكرة)\n")
        f.write(f"- **نسبة التوفير المالي المحققة بواسطة الشلال مقارنة بـ Jev الصرف:** {saving_ratio:.2f}%\n")
        f.write(f"- **تكلفة معالجة 4,321 تذكرة عبر الشلال:** ${res_waterfall['total_cost_usd']:.4f} فقط\n\n")

        f.write("## 3. مقطع جاهز للـ README (README Markdown Snippet)\n\n")
        f.write("```markdown\n")
        f.write("### Benchmark Comparison: MOCK 13 vs JEV 1.13 vs MOCK+JEV Waterfall (4,321 Stress Tickets)\n\n")
        f.write("| Engine | Accuracy | Latency (Avg) | Latency (P95) | Throughput | Cloud API Calls | Total Cost | Cost / 1k |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in results:
            f.write(
                f"| {r['engine']} | {r['accuracy_pct']:.2f}% | {r['avg_latency_ms']:.2f} ms | {r['p95_latency_ms']:.2f} ms | {r['throughput_tps']:.1f} tps | {r['jev_calls']:,} | ${r['total_cost_usd']:.4f} | ${r['cost_per_1k_usd']:.4f} |\n"
            )
        f.write("```\n")

    print(f"\nReport generated successfully: {report_file}")


if __name__ == "__main__":
    main()
