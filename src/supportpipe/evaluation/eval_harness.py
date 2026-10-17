"""Evaluation Harness for SupportPipe Model Matrix (Task C4 & C5).

Evaluates matrix configs against held-in evaluation splits in isolated mode (no fallback).
Records per_ticket.csv, computes Wilson score confidence intervals, and paired McNemar tests.
"""

from __future__ import annotations

import csv
import hashlib
import json
import logging
import time
from pathlib import Path
from typing import Any

import yaml

from supportpipe.classify.classify import get_classifier_provider
from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.classify.providers.gemini_provider import GeminiClassifierProvider
from supportpipe.classify.providers.groq_provider import GroqClassifierProvider
from supportpipe.classify.providers.hybrid_provider import HybridClassifierProvider
from supportpipe.classify.providers.local_llm_provider import LocalLLMClassifierProvider
from supportpipe.classify.providers.mock_provider import MockClassifierProvider
from supportpipe.config import settings
from supportpipe.evaluation.metrics import (
    compute_paired_mcnemar,
    compute_wilson_ci,
    validate_dataset_path,
)
from supportpipe.evaluation.sealed_guard import check_sealed_test_guard

logger = logging.getLogger(__name__)


def compute_config_hash(config: dict[str, Any]) -> str:
    """Generate deterministic sha256 hash prefix for frozen prompt, temperature, model, and provider."""
    frozen_keys = {
        "id": config.get("id"),
        "provider": config.get("provider"),
        "model_id": config.get("model_id"),
        "temperature": config.get("temperature", 0.0),
        "prompt_id": config.get("prompt_id"),
        "isolated": config.get("isolated", True),
    }
    encoded = json.dumps(frozen_keys, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:12]


def instantiate_matrix_provider(config: dict[str, Any]) -> BaseClassifierProvider:
    """Instantiate provider strictly configured for the matrix evaluation."""
    provider_type = config.get("provider", "mock").lower()
    model_id = config.get("model_id")

    if provider_type in ["mock", "offline_mock", "offline_rule_ml"]:
        return MockClassifierProvider()
    elif provider_type in ["gemini_flash_lite", "flash_lite"]:
        model = settings.gemini_flash_lite_model if model_id == "OWNER_CONFIRM" else model_id
        return GeminiClassifierProvider(model=model)
    elif provider_type in ["gemini_flash", "flash"]:
        model = settings.gemini_flash_model if not model_id else model_id
        return GeminiClassifierProvider(model=model)
    elif provider_type == "groq":
        return GroqClassifierProvider(model=model_id or settings.groq_model)
    elif provider_type in ["local", "local_llm"]:
        return LocalLLMClassifierProvider(
            model=model_id or settings.local_llm_model,
            enabled=True,
        )
    elif provider_type == "hybrid":
        return HybridClassifierProvider()
    else:
        return get_classifier_provider(provider_type)


def run_eval_config(
    config: dict[str, Any],
    dataset_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Execute evaluation for one config over dataset items.

    In isolated mode: ONE provider, NO fallback. A failed call is an error row.
    """
    config_hash = compute_config_hash(config)
    isolated = config.get("isolated", True)
    provider = instantiate_matrix_provider(config)
    provider_name = config.get("provider", "unknown")
    cfg_model_id = config.get("model_id", "")

    rows: list[dict[str, Any]] = []

    for item in dataset_items:
        tkt = item.get("ticket", {})
        lbl = item.get("label", {})
        tkt_id = tkt.get("ticket_id", "")
        gold = lbl.get("category", "")
        raw_text = tkt.get("raw_text", "")
        channel = tkt.get("channel", "app")

        start_time = time.perf_counter()
        try:
            if isolated:
                # Direct provider call: strictly NO fallback to Mock
                res = provider.classify(ticket_text=raw_text, channel=channel)
            else:
                # Composite / hybrid execution
                res = provider.classify(ticket_text=raw_text, channel=channel)

            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            pred = res.category
            correct = bool(pred == gold)
            degraded = getattr(res, "degraded", False)
            model_returned = getattr(provider, "model", cfg_model_id) or cfg_model_id

            rows.append({
                "ticket_id": tkt_id,
                "gold": gold,
                "pred": pred,
                "correct": correct,
                "provider_path": provider_name,
                "degraded": degraded,
                "model_id": model_returned,
                "latency_ms": latency_ms,
                "error": "",
                "config_hash": config_hash,
            })
        except Exception as exc:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            rows.append({
                "ticket_id": tkt_id,
                "gold": gold,
                "pred": "",
                "correct": False,
                "provider_path": provider_name,
                "degraded": False,
                "model_id": cfg_model_id,
                "latency_ms": latency_ms,
                "error": str(exc),
                "config_hash": config_hash,
            })

    return rows


def export_per_ticket_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Save rows to per_ticket.csv with required columns."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ticket_id",
        "gold",
        "pred",
        "correct",
        "provider_path",
        "degraded",
        "model_id",
        "latency_ms",
        "error",
        "config_hash",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_dataset_records(path: Path | str) -> list[dict[str, Any]]:
    """Load items from jsonl dataset after validating test.jsonl exclusion."""
    valid_path = validate_dataset_path(path)
    items: list[dict[str, Any]] = []
    with open(valid_path, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                items.append(json.loads(line_str))
    return items


def run_evaluation_harness(
    matrix_config_path: Path | str = "configs/eval_matrix.yaml",
    split_path: Path | str = "data/splits/dev.jsonl",
    output_dir: Path | str = "results/eval_matrix",
    target_config_id: str | None = None,
    override_reason: str | None = None,
) -> dict[str, Any]:
    """Run evaluation matrix across requested configurations.

    Enforces burned test holdout protection and sealed-test guard when applicable.
    Computes Wilson CI and paired McNemar statistics.
    """
    valid_split = validate_dataset_path(split_path)

    # Load matrix configurations
    matrix_path = Path(matrix_config_path)
    if not matrix_path.exists():
        raise FileNotFoundError(f"Matrix config file not found: {matrix_path}")

    with open(matrix_path, encoding="utf-8") as f:
        matrix_data = yaml.safe_load(f)
    all_configs: list[dict[str, Any]] = matrix_data.get("configs", [])

    if target_config_id:
        configs_to_run = [c for c in all_configs if c.get("id") == target_config_id]
        if not configs_to_run:
            raise ValueError(f"Config ID '{target_config_id}' not found in {matrix_config_path}")
    else:
        configs_to_run = all_configs

    # Sealed-test guard check if split is test_v2
    for cfg in configs_to_run:
        check_sealed_test_guard(
            split_path=valid_split,
            config_id=cfg["id"],
            override_reason=override_reason,
        )

    # Load items (strictly held-in / verified)
    dataset_items = load_dataset_records(valid_split)
    total_tickets = len(dataset_items)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    config_results: dict[str, dict[str, Any]] = {}
    predictions_by_config: dict[str, list[str]] = {}
    golds: list[str] = [item.get("label", {}).get("category", "") for item in dataset_items]

    for cfg in configs_to_run:
        cfg_id = cfg["id"]
        cfg_status = cfg.get("status", "active")
        if cfg_status == "disabled":
            logger.info("Skipping disabled config: %s", cfg_id)
            continue
        if cfg_status == "excluded":
            logger.info("Skipping excluded config: %s", cfg_id)
            continue

        logger.info("Evaluating config '%s' (%s) on %d tickets...", cfg_id, cfg.get("name"), total_tickets)
        rows = run_eval_config(cfg, dataset_items)

        # Export per_ticket.csv for this config
        cfg_out_dir = out_dir / cfg_id
        csv_path = cfg_out_dir / "per_ticket.csv"
        export_per_ticket_csv(rows, csv_path)

        preds = [r["pred"] for r in rows]
        predictions_by_config[cfg_id] = preds

        correct_count = sum(1 for r in rows if r["correct"])
        error_count = sum(1 for r in rows if r["error"])
        degraded_count = sum(1 for r in rows if r["degraded"])
        avg_latency = float(sum(r["latency_ms"] for r in rows) / total_tickets) if total_tickets > 0 else 0.0

        # Wilson 95% Confidence Interval
        acc, low_ci, high_ci = compute_wilson_ci(correct_count, total_tickets)

        config_results[cfg_id] = {
            "name": cfg.get("name"),
            "provider": cfg.get("provider"),
            "model_id": cfg.get("model_id"),
            "config_hash": compute_config_hash(cfg),
            "total_tickets": total_tickets,
            "correct_count": correct_count,
            "error_count": error_count,
            "degraded_count": degraded_count,
            "accuracy": acc,
            "wilson_95_ci": [low_ci, high_ci],
            "avg_latency_ms": round(avg_latency, 2),
            "csv_path": str(csv_path),
        }

    # Paired McNemar tests between all evaluated active config pairs
    mcnemar_tests: list[dict[str, Any]] = []
    evaluated_ids = list(predictions_by_config.keys())
    for i in range(len(evaluated_ids)):
        for j in range(i + 1, len(evaluated_ids)):
            id_a = evaluated_ids[i]
            id_b = evaluated_ids[j]
            stat, p_val, is_sig = compute_paired_mcnemar(
                golds,
                predictions_by_config[id_a],
                predictions_by_config[id_b],
            )
            mcnemar_tests.append({
                "config_a": id_a,
                "config_b": id_b,
                "statistic": stat,
                "p_value": p_val,
                "is_significant_at_05": is_sig,
            })

    summary: dict[str, Any] = {
        "split": str(valid_split),
        "total_tickets": total_tickets,
        "configs": config_results,
        "paired_mcnemar_comparisons": mcnemar_tests,
    }

    summary_file = out_dir / "summary.json"
    summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return summary
