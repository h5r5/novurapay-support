"""Tests for Stress Batch Ingestion, Blind Evaluation, and Protocol Gates (Block S).

Verifies:
1. Rejection of invalid category, invalid priority, empty text, exact duplicate, and near-duplicate (ratio >= 0.9).
2. Clean ingestion writes batch_NNN.jsonl and updates MANIFEST.json.
3. Blind evaluation runs offline, produces aggregates only, updates status to 'measured_blind'.
4. Blind evaluation strictly refuses second run on the same batch.
5. Outputs (summary.md, per_ticket.csv, console) contain zero ticket text.
6. Manifest sha256 checksum integrity.
7. Enforcement of Change Gate Rule (b): requires >= 3 tickets across >= 2 clusters.
8. Strict invariant: never loads data/test_v2*.
"""

import json
import sys
from pathlib import Path

import pytest

# Add project root to sys.path so scripts can be imported in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.ingest_stress_batch import (
    assert_not_test_v2,
    compute_file_sha256,
    ingest_stress_batch,
    normalize_text_for_dedup,
)
from scripts.stress_eval import run_stress_eval

from supportpipe.rules_gate import validate_rule_candidate


def test_strict_invariant_rejects_test_v2_paths() -> None:
    """Ensure any attempt to touch data/test_v2* raises PermissionError immediately."""
    with pytest.raises(PermissionError, match="STRICT INVARIANT VIOLATION"):
        assert_not_test_v2("data/test_v2.jsonl")

    with pytest.raises(PermissionError, match="STRICT INVARIANT VIOLATION"):
        assert_not_test_v2(Path("data/test_v2_sealed/eval.jsonl"))


def test_ingest_rejects_invalid_category(tmp_path: Path) -> None:
    """Ingestion must reject rows with categories outside the 14 valid taxonomy categories."""
    stress_dir = tmp_path / "stress"
    input_file = tmp_path / "raw_batch.jsonl"
    bad_row = {
        "ticket": {
            "ticket_id": "STRESS-BAD-CAT",
            "raw_text": "اريد اشتري بيتكوين من خلال المحفظة وماكو خيار",
        },
        "label": {
            "category": "crypto_trading",  # Invalid category
            "priority": "low",
        },
    }
    input_file.write_text(json.dumps(bad_row, ensure_ascii=False) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid category 'crypto_trading'"):
        ingest_stress_batch(
            input_file=input_file,
            stress_dir=stress_dir,
            dev_split=tmp_path / "empty_dev.jsonl",
            test_split=tmp_path / "empty_test.jsonl",
        )

    # Verify no batch was written
    assert not (stress_dir / "batch_001.jsonl").exists()


def test_ingest_rejects_invalid_priority(tmp_path: Path) -> None:
    """Ingestion must reject rows with priority outside {high, medium, low}."""
    stress_dir = tmp_path / "stress"
    input_file = tmp_path / "raw_batch.jsonl"
    bad_row = {
        "ticket": {
            "ticket_id": "STRESS-BAD-PRIO",
            "raw_text": "المحفظة واكفة وعندي عملية ضرورية هسة",
        },
        "label": {
            "category": "app_bug",
            "priority": "critical_emergency",  # Invalid priority
        },
    }
    input_file.write_text(json.dumps(bad_row, ensure_ascii=False) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid priority 'critical_emergency'"):
        ingest_stress_batch(
            input_file=input_file,
            stress_dir=stress_dir,
            dev_split=tmp_path / "empty_dev.jsonl",
            test_split=tmp_path / "empty_test.jsonl",
        )


def test_ingest_rejects_empty_or_whitespace_text(tmp_path: Path) -> None:
    """Ingestion must reject rows with empty or whitespace-only text."""
    stress_dir = tmp_path / "stress"
    input_file = tmp_path / "raw_batch.jsonl"
    bad_row = {
        "ticket": {
            "ticket_id": "STRESS-EMPTY",
            "raw_text": "    \t \n  ",
        },
        "label": {
            "category": "unclear_or_incomplete",
            "priority": "low",
        },
    }
    input_file.write_text(json.dumps(bad_row, ensure_ascii=False) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Empty or whitespace-only text"):
        ingest_stress_batch(
            input_file=input_file,
            stress_dir=stress_dir,
            dev_split=tmp_path / "empty_dev.jsonl",
            test_split=tmp_path / "empty_test.jsonl",
        )


def test_ingest_rejects_exact_duplicate_in_batch(tmp_path: Path) -> None:
    """Ingestion must reject exact duplicate text inside the incoming batch."""
    stress_dir = tmp_path / "stress"
    input_file = tmp_path / "raw_batch.jsonl"
    text = "حولت فلوس برقم TXN-11223344 وما وصلن للمستلم"
    row1 = {
        "ticket": {"ticket_id": "T1", "raw_text": text},
        "label": {"category": "failed_transfer", "priority": "high"},
    }
    row2 = {
        "ticket": {"ticket_id": "T2", "raw_text": text},
        "label": {"category": "failed_transfer", "priority": "high"},
    }
    content = f"{json.dumps(row1, ensure_ascii=False)}\n{json.dumps(row2, ensure_ascii=False)}\n"
    input_file.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match="Exact duplicate text"):
        ingest_stress_batch(
            input_file=input_file,
            stress_dir=stress_dir,
            dev_split=tmp_path / "empty_dev.jsonl",
            test_split=tmp_path / "empty_test.jsonl",
        )


def test_ingest_rejects_exact_duplicate_against_reference_dev(tmp_path: Path) -> None:
    """Ingestion must reject exact duplicate text against existing dev.jsonl."""
    stress_dir = tmp_path / "stress"
    dev_split = tmp_path / "dev.jsonl"
    existing_text = "عفوا دزيت حوالة بمبلغ 75000 برقم TXN-85329037 اليوم الصبح"
    dev_split.write_text(
        json.dumps({"ticket": {"ticket_id": "DEV-01", "raw_text": existing_text}}) + "\n",
        encoding="utf-8",
    )

    input_file = tmp_path / "raw_batch.jsonl"
    row = {
        "ticket": {"ticket_id": "STRESS-DUP", "raw_text": existing_text},
        "label": {"category": "failed_transfer", "priority": "medium"},
    }
    input_file.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Exact duplicate text of ticket 'DEV-01'"):
        ingest_stress_batch(
            input_file=input_file,
            stress_dir=stress_dir,
            dev_split=dev_split,
            test_split=tmp_path / "empty_test.jsonl",
        )


def test_ingest_rejects_near_duplicate_ratio_ge_09(tmp_path: Path) -> None:
    """Ingestion must reject normalized near-duplicates with SequenceMatcher ratio >= 0.9."""
    stress_dir = tmp_path / "stress"
    dev_split = tmp_path / "dev.jsonl"
    # Base text in dev split
    dev_text = "سلام عليكم خوي الصراف الالي مال فرع العشار بلع بطاقتي الماستر"
    dev_split.write_text(
        json.dumps({"ticket": {"ticket_id": "DEV-CARD", "raw_text": dev_text}}) + "\n",
        encoding="utf-8",
    )

    # Near-duplicate with minor punctuation / tatweel / slight shift >= 0.9 similarity
    stress_text = "سلام عليكم خوي،، الصراف الالي مال فرع العشار بلع بطاقتي الماستركارد!"

    input_file = tmp_path / "raw_batch.jsonl"
    row = {
        "ticket": {"ticket_id": "STRESS-NEAR", "raw_text": stress_text},
        "label": {"category": "card_issue", "priority": "high"},
    }
    input_file.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match=r"Normalized near-duplicate \(similarity [0-9\.]+ >= 0\.9\)"):
        ingest_stress_batch(
            input_file=input_file,
            stress_dir=stress_dir,
            dev_split=dev_split,
            test_split=tmp_path / "empty_test.jsonl",
        )


def test_ingest_accepts_clean_valid_batch_and_updates_manifest(tmp_path: Path) -> None:
    """Ingestion accepts clean valid batch and writes batch_001.jsonl and MANIFEST.json."""
    stress_dir = tmp_path / "stress"
    input_file = tmp_path / "raw_batch.jsonl"

    row1 = {
        "ticket": {
            "ticket_id": "STRESS-01",
            "raw_text": "الوكيل في البصرة طالب بعمولة 5 الاف اضافية على السحب",
        },
        "label": {
            "category": "agent_dispute",
            "priority": "medium",
            "tags": {"dialect": "basrawi", "attack_type": "extortion"},
        },
    }
    row2 = {
        "ticket": {
            "ticket_id": "STRESS-02",
            "raw_text": "حسابي مقفول وتطلعلي رسالة تم حظر الحساب راجع الادارة",
        },
        "label": {
            "category": "account_blocked",
            "priority": "high",
            "tags": {"dialect": "baghdadi", "attack_type": "account_lock"},
        },
    }
    content = f"{json.dumps(row1, ensure_ascii=False)}\n{json.dumps(row2, ensure_ascii=False)}\n"
    input_file.write_text(content, encoding="utf-8")

    res = ingest_stress_batch(
        input_file=input_file,
        stress_dir=stress_dir,
        dev_split=tmp_path / "empty_dev.jsonl",
        test_split=tmp_path / "empty_test.jsonl",
        batch_id="001",
        generator="synthetic_test_gen",
    )

    batch_path = Path(res["batch_file"])
    assert batch_path.exists()
    assert res["batch_id"] == "batch_001"
    assert res["n"] == 2
    assert res["status"] == "unmeasured"

    manifest_path = stress_dir / "MANIFEST.json"
    assert manifest_path.exists()
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    assert "batch_001" in manifest
    entry = manifest["batch_001"]
    assert entry["status"] == "unmeasured"
    assert entry["n"] == 2
    assert entry["generator"] == "synthetic_test_gen"
    assert entry["sha256"] == compute_file_sha256(batch_path)


def test_stress_eval_blind_run_and_refusal_of_second_run(tmp_path: Path) -> None:
    """Stress eval executes blind evaluation once, updates status, and refuses second run."""
    stress_dir = tmp_path / "stress"
    results_dir = tmp_path / "results"
    input_file = tmp_path / "raw_batch.jsonl"

    row1 = {
        "ticket": {
            "ticket_id": "TKT-STRESS-101",
            "raw_text": "فلوسي معلقة دزيت حوالة وما وصلت للطرف الثاني",
        },
        "label": {
            "category": "failed_transfer",
            "priority": "high",
            "tags": {"dialect": "baghdadi"},
        },
    }
    row2 = {
        "ticket": {
            "ticket_id": "TKT-STRESS-102",
            "raw_text": "الوكيل اخذ عمولة اضافية غير قانونية",
        },
        "label": {
            "category": "agent_dispute",
            "priority": "medium",
            "tags": {"dialect": "moslawi"},
        },
    }
    content = f"{json.dumps(row1, ensure_ascii=False)}\n{json.dumps(row2, ensure_ascii=False)}\n"
    input_file.write_text(content, encoding="utf-8")

    ingest_stress_batch(
        input_file=input_file,
        stress_dir=stress_dir,
        dev_split=tmp_path / "empty_dev.jsonl",
        test_split=tmp_path / "empty_test.jsonl",
        batch_id="001",
    )

    # First blind run: must succeed
    eval_res = run_stress_eval(
        batch_arg="batch_001",
        stress_dir=stress_dir,
        results_dir=results_dir,
    )

    assert eval_res["batch_id"] == "batch_001"
    assert eval_res["total_tickets"] == 2
    assert eval_res["status"] == "measured_blind"
    assert Path(eval_res["summary_md"]).exists()
    assert Path(eval_res["per_ticket_csv"]).exists()

    # Verify manifest updated
    manifest_path = stress_dir / "MANIFEST.json"
    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["batch_001"]["status"] == "measured_blind"

    # Second blind run: must be STRICTLY REFUSED
    with pytest.raises(RuntimeError, match="REFUSED: Second blind run prohibited"):
        run_stress_eval(
            batch_arg="batch_001",
            stress_dir=stress_dir,
            results_dir=results_dir,
        )


def test_stress_eval_outputs_contain_zero_ticket_text(tmp_path: Path) -> None:
    """Verify STRICT SECURITY: Outputs (summary.md, per_ticket.csv) contain zero raw ticket text."""
    stress_dir = tmp_path / "stress"
    results_dir = tmp_path / "results"
    input_file = tmp_path / "raw_batch.jsonl"

    secret_raw_text_1 = "تذكرة_سرية_للعميل_الاول_تتعلق_بسؤال_عام_عن_الخدمات"
    secret_raw_text_2 = "بيانات_حساب_مختلفة_تماما_لكشف_العمليات_المالية_السابقة"

    row1 = {
        "ticket": {"ticket_id": "SEC-01", "raw_text": secret_raw_text_1},
        "label": {"category": "general_inquiry", "priority": "low"},
    }
    row2 = {
        "ticket": {"ticket_id": "SEC-02", "raw_text": secret_raw_text_2},
        "label": {"category": "balance_or_statement_inquiry", "priority": "low"},
    }
    content = f"{json.dumps(row1, ensure_ascii=False)}\n{json.dumps(row2, ensure_ascii=False)}\n"
    input_file.write_text(content, encoding="utf-8")

    ingest_stress_batch(
        input_file=input_file,
        stress_dir=stress_dir,
        dev_split=tmp_path / "empty_dev.jsonl",
        test_split=tmp_path / "empty_test.jsonl",
        batch_id="002",
    )

    eval_res = run_stress_eval(
        batch_arg="batch_002",
        stress_dir=stress_dir,
        results_dir=results_dir,
    )

    summary_content = Path(eval_res["summary_md"]).read_text(encoding="utf-8")
    csv_content = Path(eval_res["per_ticket_csv"]).read_text(encoding="utf-8")

    # Assert secret text is absent from both output files
    assert secret_raw_text_1 not in summary_content
    assert secret_raw_text_2 not in summary_content
    assert secret_raw_text_1 not in csv_content
    assert secret_raw_text_2 not in csv_content

    # Assert CSV header is strictly formatted without raw text columns
    csv_lines = csv_content.strip().splitlines()
    header = csv_lines[0].split(",")
    expected_header = [
        "ticket_id",
        "gold",
        "pred",
        "correct",
        "provider_path",
        "degraded",
        "model_id",
        "latency_ms",
        "error",
    ]
    assert header == expected_header


def test_manifest_sha256_hash_checks(tmp_path: Path) -> None:
    """Verify manifest sha256 checksum integrity and tampering detection."""
    stress_dir = tmp_path / "stress"
    input_file = tmp_path / "raw_batch.jsonl"
    row = {
        "ticket": {"ticket_id": "H1", "raw_text": "اريد اعرف اوقات دوام الوكلاء"},
        "label": {"category": "general_inquiry", "priority": "low"},
    }
    input_file.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")

    res = ingest_stress_batch(
        input_file=input_file,
        stress_dir=stress_dir,
        dev_split=tmp_path / "empty_dev.jsonl",
        test_split=tmp_path / "empty_test.jsonl",
        batch_id="003",
    )

    batch_path = Path(res["batch_file"])
    actual_hash = compute_file_sha256(batch_path)
    assert res["sha256"] == actual_hash

    # Tamper with the file
    with open(batch_path, "a", encoding="utf-8") as f:
        f.write("\n")

    tampered_hash = compute_file_sha256(batch_path)
    assert tampered_hash != actual_hash


def test_enforce_rule_b_rejections_and_acceptance() -> None:
    """Verify Change Gate Rule (b): requires >= 3 tickets across >= 2 batch-tag clusters."""
    batch_tickets = [
        {
            "ticket": {"ticket_id": "T1", "raw_text": "الوكيل فرض عمولة خمسة الاف زيادة"},
            "label": {"tags": {"dialect": "basrawi", "attack_type": "extortion"}},
        },
        {
            "ticket": {"ticket_id": "T2", "raw_text": "طلب الوكيل عمولة اضافية غير قانونية"},
            "label": {"tags": {"dialect": "basrawi", "attack_type": "extortion"}},
        },
        {
            "ticket": {"ticket_id": "T3", "raw_text": "الوكيل اخذ عمولة زيادة من عندي بالموصل"},
            "label": {"tags": {"dialect": "moslawi", "attack_type": "extortion"}},
        },
        {
            "ticket": {"ticket_id": "T4", "raw_text": "يا معودين الوكيل دياخذ عمولة زايدة"},
            "label": {"tags": {"dialect": "baghdadi", "attack_type": "slang"}},
        },
    ]

    # Test 1: Literal single-ticket phrase (only matches T1) -> Rejection: insufficient support (<3)
    ok_1, msg_1 = validate_rule_candidate(
        pattern="الوكيل فرض عمولة خمسة الاف زيادة",
        batch_tickets=batch_tickets,
        min_support=3,
        min_clusters=2,
    )
    assert not ok_1
    assert "insufficient ticket support" in msg_1

    # Test 2: Matches 2 tickets in basrawi only -> Rejection: insufficient cluster diversity (<2)
    ok_2, msg_2 = validate_rule_candidate(
        pattern=r"عمولة.*(خمسة|اضافية)",
        batch_tickets=batch_tickets,
        min_support=2,
        min_clusters=2,
    )
    assert not ok_2
    assert "insufficient cluster diversity" in msg_2

    # Test 3: Generalized pattern matching 4 tickets across 3 clusters -> Approved!
    ok_3, msg_3 = validate_rule_candidate(
        pattern=r"عمولة\s+(زيادة|اضافية|زايدة)",
        batch_tickets=batch_tickets,
        min_support=3,
        min_clusters=2,
    )
    assert ok_3
    assert "Rule approved" in msg_3
    assert "across 3 clusters" in msg_3 or "across 2 clusters" in msg_3


def test_normalize_text_for_dedup() -> None:
    """Verify standard text normalization strips diacritics, punctuation, and extra whitespace."""
    raw = "  سلامٌ عليكمْ،،،   خويَ!   "
    expected = "سلام عليكم خوي"
    assert normalize_text_for_dedup(raw) == expected
