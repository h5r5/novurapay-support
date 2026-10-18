"""Unit tests for Model Matrix Evaluation Harness (Task C4).

Verifies strictly held-out test.jsonl rejection, exact per_ticket.csv columns,
isolated mode failure recording without fallback, config hashing, Wilson CI, and McNemar test.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from supportpipe.classify.providers.base import BaseClassifierProvider
from supportpipe.evaluation.eval_harness import (
    compute_config_hash,
    export_per_ticket_csv,
    run_eval_config,
    run_evaluation_harness,
)
from supportpipe.schemas import ClassificationResult


def test_harness_strictly_refuses_burned_test_jsonl() -> None:
    """Evaluation harness must strictly refuse data/splits/test.jsonl."""
    with pytest.raises((AssertionError, ValueError)) as exc:
        run_evaluation_harness(split_path="data/splits/test.jsonl")
    assert "burned diagnostic set" in str(exc.value)


def test_per_ticket_csv_exact_columns(tmp_path: Path) -> None:
    """Verify per_ticket.csv has the exact 10 required columns."""
    sample_rows = [
        {
            "ticket_id": "TKT-001",
            "gold": "failed_transfer",
            "pred": "failed_transfer",
            "correct": True,
            "provider_path": "mock",
            "degraded": False,
            "model_id": "offline_mock",
            "latency_ms": 1.25,
            "error": "",
            "config_hash": "a1b2c3d4e5f6",
        }
    ]
    csv_file = tmp_path / "per_ticket.csv"
    export_per_ticket_csv(sample_rows, csv_file)

    assert csv_file.exists()
    with open(csv_file, encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

    expected_cols = [
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
    assert header == expected_cols


def test_isolated_mode_captures_error_without_fallback() -> None:
    """In isolated mode, a provider failure must record an error row and never fallback."""

    class FailingProvider(BaseClassifierProvider):
        model = "faulty-model"

        def classify(self, ticket_text: str, channel: str = "app", **kwargs) -> ClassificationResult:
            raise ConnectionError("Simulated provider outage (HTTP 503)")

    config = {
        "id": "failing_test_cfg",
        "provider": "failing_provider",
        "model_id": "faulty-model",
        "isolated": True,
        "temperature": 0.0,
        "prompt_id": "p1",
    }

    dataset_items = [
        {
            "ticket": {"ticket_id": "TKT-ERR-01", "raw_text": "حولت فلوس", "channel": "app"},
            "label": {"category": "failed_transfer"},
        }
    ]

    with patch(
        "supportpipe.evaluation.eval_harness.instantiate_matrix_provider",
        return_value=FailingProvider(),
    ):
        rows = run_eval_config(config, dataset_items)

    assert len(rows) == 1
    row = rows[0]
    assert row["ticket_id"] == "TKT-ERR-01"
    assert row["pred"] == ""
    assert row["correct"] is False
    assert row["provider_path"] == "failing_provider"
    assert "Simulated provider outage" in row["error"]
    assert row["degraded"] is False


def test_config_hash_is_deterministic() -> None:
    """Config hash must deterministically capture frozen prompt, temp 0, model, and provider."""
    cfg1 = {
        "id": "test_cfg",
        "provider": "mock",
        "model_id": "offline_mock",
        "temperature": 0.0,
        "prompt_id": "prompt_v1",
        "isolated": True,
    }
    cfg2 = dict(cfg1)

    hash1 = compute_config_hash(cfg1)
    hash2 = compute_config_hash(cfg2)
    assert hash1 == hash2
    assert len(hash1) == 12

    # Changing temperature or prompt changes hash
    cfg3 = dict(cfg1, temperature=0.7)
    assert compute_config_hash(cfg3) != hash1


def test_harness_summary_wilson_and_mcnemar(tmp_path: Path) -> None:
    """Verify execution of evaluation harness produces summary.json with Wilson CI and McNemar tests."""
    dev_split = tmp_path / "custom_dev.jsonl"
    items = [
        {
            "ticket": {"ticket_id": f"TKT-{i:03d}", "raw_text": "حولت رصيد", "channel": "app"},
            "label": {"category": "failed_transfer", "template_id": f"tmpl_{i % 3}"},
        }
        for i in range(10)
    ]
    with open(dev_split, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")

    matrix_yaml = tmp_path / "matrix.yaml"
    matrix_yaml.write_text(
        """
configs:
  - id: cfg_mock_1
    name: "Mock 1"
    provider: mock
    model_id: "mock_model"
    isolated: true
    status: active
    temperature: 0.0
    prompt_id: "p1"
  - id: cfg_mock_2
    name: "Mock 2"
    provider: mock
    model_id: "mock_model"
    isolated: true
    status: active
    temperature: 0.0
    prompt_id: "p1"
""",
        encoding="utf-8",
    )

    out_dir = tmp_path / "eval_results"
    summary = run_evaluation_harness(
        matrix_config_path=matrix_yaml,
        split_path=dev_split,
        output_dir=out_dir,
    )

    assert "configs" in summary
    assert "cfg_mock_1" in summary["configs"]
    cfg_res = summary["configs"]["cfg_mock_1"]
    assert "wilson_95_ci" in cfg_res
    assert len(cfg_res["wilson_95_ci"]) == 2
    assert (out_dir / "cfg_mock_1" / "per_ticket.csv").exists()

    # Paired McNemar comparison must be present
    assert len(summary["paired_mcnemar_comparisons"]) == 1
    comp = summary["paired_mcnemar_comparisons"][0]
    assert comp["config_a"] == "cfg_mock_1"
    assert comp["config_b"] == "cfg_mock_2"
    assert comp["p_value"] == 1.0  # Identical mock outputs


def test_offline_rule_ml_oof_equals_grouped_cv_accuracy(tmp_path: Path) -> None:
    """Verify offline_rule_ml_oof accuracy equals grouped-CV Rules+ML result (78/219).

    Verifies exact equality to 78/219 (0.3562), in-sample stamping on offline_rule_ml_insample (202/219),
    identical per_ticket.csv columns, and valid paired McNemar testing.
    """
    matrix_yaml = tmp_path / "matrix_offline.yaml"
    matrix_yaml.write_text(
        """
configs:
  - id: offline_rule_ml_insample
    name: "Offline Heuristics + ML Baseline (In-Sample)"
    provider: mock
    model_id: "offline_mock"
    isolated: true
    status: active
    notes: "IN-SAMPLE, not a performance number"
  - id: offline_rule_ml_oof
    name: "Offline Heuristics + ML Baseline (Out-of-Fold)"
    provider: offline_rule_ml_oof
    model_id: "offline_mock_oof"
    isolated: true
    status: active
""",
        encoding="utf-8",
    )

    out_dir = tmp_path / "eval_dev_results"
    summary = run_evaluation_harness(
        matrix_config_path=matrix_yaml,
        split_path="data/splits/dev.jsonl",
        output_dir=out_dir,
    )

    # 1. Out-of-Fold Rules+ML exact match to grouped-CV
    oof_res = summary["configs"]["offline_rule_ml_oof"]
    assert oof_res["total_tickets"] == 219
    assert oof_res["correct_count"] == 78
    assert oof_res["accuracy"] == round(78 / 219, 4)
    assert oof_res["error_count"] == 0

    # 2. In-sample baseline check & stamping
    insample_res = summary["configs"]["offline_rule_ml_insample"]
    assert insample_res["total_tickets"] == 219
    assert insample_res["correct_count"] == 202
    assert insample_res["accuracy"] == round(202 / 219, 4)
    assert insample_res["notes"] == "IN-SAMPLE, not a performance number"
    assert summary["notes"]["offline_rule_ml_insample"] == "IN-SAMPLE, not a performance number"

    # 3. Identical 10 columns in per_ticket.csv
    expected_cols = [
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
    for cfg_id in ["offline_rule_ml_oof", "offline_rule_ml_insample"]:
        csv_p = Path(summary["configs"][cfg_id]["csv_path"])
        assert csv_p.exists()
        with open(csv_p, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
        assert header == expected_cols
        assert len(rows) == 219

    # 4. Paired McNemar test presence and validity
    assert len(summary["paired_mcnemar_comparisons"]) == 1
    comp = summary["paired_mcnemar_comparisons"][0]
    assert {comp["config_a"], comp["config_b"]} == {"offline_rule_ml_insample", "offline_rule_ml_oof"}
    assert comp["p_value"] < 0.001  # Significant difference between in-sample and out-of-fold
