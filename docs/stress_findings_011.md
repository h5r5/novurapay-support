# Stress Test Findings Report: Batch 011

- **Batch ID**: batch_011
- **Source File**: `data/stress_test/novurapay_tickets_round11.jsonl`
- **Ingested Location**: `data/stress/batch_011.jsonl` (4 tickets accepted, 146 duplicate rows rejected)
- **Evaluation Date**: 2026-10-26
- **Git Commit (Blind Run)**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **100.00%** (4/4) (Wilson 95% CI: `[51.01%, 100.00%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 011 was submitted as the eleventh externally generated synthetic stress test batch.
During ingestion under Protocol S1:
- 150 total rows were processed.
- 146 rows were rejected:
  - 145 rows were exact duplicates of tickets previously ingested in `batch_002.jsonl` (e.g. `EXT-2-001` through `EXT-2-150`).
  - 1 row (`EXT-2-120`, row 120) was rejected as a normalized near-duplicate (similarity ratio $0.924 \ge 0.90$) with ticket `EXT-2-120` from `batch_002.jsonl`.
- 4 rows were accepted and ingested into `data/stress/batch_011.jsonl`: `EXT-2-013`, `EXT-2-048`, `EXT-2-064`, and `EXT-2-131`.

On blind evaluation using the offline engine (`rules_dialect_ml_v10`), the pipeline achieved **100.00% blind accuracy** (4/4, Wilson 95% CI: `[51.01%, 100.00%]`) with zero errors, zero degraded classifications, and 7.78 ms average latency.

---

## 2. Slice Breakdown

### A. Category Recall Performance (Blind V10)

| Category | Total (Gold) | Correct | Recall | Confusions |
|---|---|---|---|---|
| `balance_or_statement_inquiry` | 1 | 1 | 100.00% | None |
| `bill_payment_failure` | 1 | 1 | 100.00% | None |
| `fraud_report` | 1 | 1 | 100.00% | None |
| `refund_status` | 1 | 1 | 100.00% | None |

### B. Dialect & Tag Slice Performance

- **Dialects**:
  - `baghdadi`: 3/3 (100.00%)
  - `arabizi`: 1/1 (100.00%)
- **Attacks**:
  - `None`: 4/4 (100.00%)
- **Length Buckets**:
  - `short`: 1/1 (100.00%)
  - `normal`: 2/2 (100.00%)
  - `long`: 1/1 (100.00%)
- **Secondary Hints**:
  - `None`: 2/2 (100.00%)
  - `account_blocked`: 1/1 (100.00%)
  - `fraud_report`: 1/1 (100.00%)

---

## 3. Error Analysis & Root Cause

Zero classification errors were observed on the accepted tickets. All 4 tickets were correctly classified by the offline V10 pipeline.

---

## 4. Change Gate Assessment (S5 Evaluation)

- **Criteria**: Rule remediations require pattern support by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, no literal phrase embedded, and no regression on `dev.jsonl`.
- **Finding**: With zero misclassifications and an accepted batch volume of 4 tickets, no failure pattern exists to remediate.
- **Decision**: No rule change is proposed or adopted. The offline engine remains at version `v10`.
