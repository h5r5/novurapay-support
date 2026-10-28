# Stress Test Findings Report: Batch 014

- **Batch ID**: batch_014
- **Source File**: `data/stress_test/novurapay_tickets_round14.jsonl`
- **Ingested Location**: `data/stress/batch_014.jsonl` (147 tickets accepted, 3 duplicate rows rejected)
- **Evaluation Date**: 2026-10-26
- **Git Commit (Blind Run)**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **82.99%** (122/147) (Wilson 95% CI: `[76.10%, 88.21%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 014 is the fourteenth externally generated synthetic stress test batch, containing 150 tickets distributed across 5 Iraqi dialects, 3 length distributions, and adversarial payloads.
During ingestion under Protocol S1:
- 150 total rows were processed.
- 3 duplicate rows were rejected due to exact text duplication with tickets from `batch_001.jsonl`:
  - Row 30 (`EXT-1-030` matching `EXT-1-059`)
  - Row 72 (`EXT-1-072` matching `EXT-1-103`)
  - Row 145 (`EXT-1-145` matching `EXT-1-015`)
- 147 tickets were accepted and registered into `data/stress/batch_014.jsonl`.

On blind evaluation using the offline engine (`rules_dialect_ml_v10`), the pipeline achieved **82.99% blind accuracy** (122/147, Wilson 95% CI: `[76.10%, 88.21%]`) with zero runtime errors, zero degraded classifications, and average latency of 5.06 ms.

---

## 2. Slice Breakdown

### A. Category Recall Performance (Blind V10)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `account_blocked` | 10 | 10 | 100.00% | None |
| `wrong_recipient` | 10 | 10 | 100.00% | None |
| `failed_transfer` | 11 | 10 | 90.91% | `general_inquiry` (1) |
| `unclear_or_incomplete` | 11 | 10 | 90.91% | `general_inquiry` (1) |
| `agent_dispute` | 10 | 9 | 90.00% | `unclear_or_incomplete` (1) |
| `balance_or_statement_inquiry` | 10 | 9 | 90.00% | `unclear_or_incomplete` (1) |
| `refund_status` | 10 | 9 | 90.00% | `failed_transfer` (1) |
| `bill_payment_failure` | 11 | 9 | 81.82% | `failed_transfer` (1), `card_issue` (1) |
| `app_bug` | 10 | 8 | 80.00% | `unclear_or_incomplete` (1), `failed_transfer` (1) |
| `kyc_document_issue` | 10 | 8 | 80.00% | `unclear_or_incomplete` (1), `account_blocked` (1) |
| `fraud_report` | 11 | 8 | 72.73% | `unclear_or_incomplete` (1), `bill_payment_failure` (1), `login_problem` (1) |
| `general_inquiry` | 11 | 8 | 72.73% | `unclear_or_incomplete` (2), `card_issue` (1) |
| `card_issue` | 11 | 7 | 63.64% | `unclear_or_incomplete` (1), `fraud_report` (1), `login_problem` (1), `failed_transfer` (1) |
| `login_problem` | 11 | 7 | 63.64% | `fraud_report` (1), `account_blocked` (1), `app_bug` (1), `unclear_or_incomplete` (1) |

### B. Dialect & Tag Slice Performance

- **Dialects**:
  - `basrawi`: 24/28 (85.71%)
  - `mixed`: 21/25 (84.00%)
  - `baghdadi`: 40/48 (83.33%)
  - `mosul`: 19/23 (82.61%)
  - `arabizi`: 18/23 (78.26%)
- **Attacks**:
  - `None`: 118/140 (84.29%)
  - `prompt_injection`: 4/7 (57.14%)
- **Length Buckets**:
  - `normal`: 63/72 (87.50%)
  - `long`: 37/46 (80.43%)
  - `short`: 22/29 (75.86%)

---

## 3. Failure Analysis & Root Cause

Total misclassifications: 25 tickets.
An analysis of the confusion matrix reveals that errors are widely dispersed across categories, with no dominant systematic failure pattern:
- The single most frequent confusion pair is `general_inquiry -> unclear_or_incomplete` with only 2 tickets (due to vague service questions safely routed to triage).
- All other error pairs (`login_problem -> fraud_report`, `card_issue -> unclear_or_incomplete`, etc.) are isolated single instances ($N = 1$).
- No category exhibits a systematic cluster failure.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `dev.jsonl`.
- **Finding**: No error pattern reaches the $\ge 3$ tickets threshold (the maximum confusion pair has only 2 tickets).
- **Decision**: Nothing qualifies under the S5 change gate. No rule change is proposed or adopted. The offline engine remains at version `v10`.
