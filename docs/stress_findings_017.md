# Stress Test Findings Report: Batch 017

- **Batch ID**: batch_017
- **Source File**: `data/stress_test/novurapay_tickets_round17.jsonl`
- **Ingested Location**: `data/stress/batch_017.jsonl` (198 tickets accepted, 2 duplicate rows rejected)
- **Evaluation Date**: 2026-10-27
- **Git Commit (Blind Run)**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **87.88%** (174/198) (Wilson 95% CI: `[82.60%, 91.72%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 017 is the seventeenth externally generated synthetic stress test batch, containing 200 tickets focusing heavily on the Western dialect alongside Arabizi and mixed queries, multi-intent tickets, and adversarial prompt injections.

During ingestion under Protocol S1:
- 200 total rows were processed.
- 2 duplicate rows were rejected:
  - Row 42 (`EXT-3-042`): Exact duplicate text of ticket `EXT-1-059` from `batch_001.jsonl`.
  - Row 189 (`EXT-3-189`): Exact duplicate text of ticket `EXT-1-015` from `batch_001.jsonl`.
- 198 valid tickets were accepted and registered into `data/stress/batch_017.jsonl`.

On blind evaluation using the offline engine (`rules_dialect_ml_v11`), the pipeline achieved **87.88% blind accuracy** (174/198, Wilson 95% CI: `[82.60%, 91.72%]`) with zero runtime errors, zero degraded classifications, and average latency of 4.98 ms.

---

## 2. Slice Breakdown

### A. Category Recall Performance (Blind V11)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `agent_dispute` | 14 | 14 | 100.00% | None |
| `balance_or_statement_inquiry` | 14 | 14 | 100.00% | None |
| `bill_payment_failure` | 14 | 14 | 100.00% | None |
| `fraud_report` | 14 | 14 | 100.00% | None |
| `card_issue` | 14 | 13 | 92.86% | `refund_status` (1) |
| `kyc_document_issue` | 14 | 13 | 92.86% | `app_bug` (1) |
| `account_blocked` | 14 | 12 | 85.71% | `failed_transfer` (2) |
| `failed_transfer` | 14 | 12 | 85.71% | `login_problem` (1), `balance_or_statement_inquiry` (1) |
| `refund_status` | 14 | 12 | 85.71% | `bill_payment_failure` (1), `unclear_or_incomplete` (1) |
| `general_inquiry` | 16 | 13 | 81.25% | `agent_dispute` (1), `balance_or_statement_inquiry` (1), `kyc_document_issue` (1) |
| `app_bug` | 14 | 11 | 78.57% | `login_problem` (2), `kyc_document_issue` (1) |
| `unclear_or_incomplete` | 14 | 11 | 78.57% | `general_inquiry` (2), `wrong_recipient` (1) |
| `wrong_recipient` | 14 | 11 | 78.57% | `failed_transfer` (2), `refund_status` (1) |
| `login_problem` | 14 | 10 | 71.43% | `app_bug` (2), `account_blocked` (1), `kyc_document_issue` (1) |

### B. Dialect & Tag Slice Performance

- **Dialects**:
  - `arabizi`: 25/27 (92.59%)
  - `mixed`: 31/34 (91.18%)
  - `western`: 118/137 (86.13%)
- **Attacks**:
  - `prompt_injection`: 9/10 (90.00%)
  - `None`: 165/188 (87.77%)
- **Length Buckets**:
  - `short`: 35/39 (89.74%)
  - `normal`: 92/103 (89.32%)
  - `long`: 47/56 (83.93%)

---

## 3. Failure Analysis & Root Cause

Total misclassifications across the batch: 24 tickets out of 198 (12.12%).
Analysis of error patterns shows high dispersion across multiple subtle boundaries:

1. **`app_bug` vs `login_problem` Boundary (4 tickets)**:
   - `app_bug -> login_problem` (2 tickets: `EXT-3-064`, `EXT-3-093`): Western and Arabizi tickets reporting technical crashes/freezes occurring during the authentication screen.
   - `login_problem -> app_bug` (2 tickets: `EXT-3-081`, `EXT-3-102`): Queries reporting password/credential lockout described as an application defect.
   - Both pairs are handled by ML fall-through rather than regex rules. Neither directional pair meets the $\ge 3$ ticket threshold.

2. **`wrong_recipient -> failed_transfer` (2 tickets)**:
   - Tickets `EXT-3-103` and `EXT-3-141`: Long-form Western dialect tickets describing transfers sent to an unintended recipient, confused by ML with general transfer failure due to transfer terminology. Both tickets belong to the same dialect cluster (`western`).

3. **`account_blocked -> failed_transfer` (2 tickets)**:
   - Tickets `EXT-3-007` and `EXT-3-121`: Tickets reporting account restriction occurring during a transaction attempt, where ML weighed transaction keywords over freeze terminology.

4. **`unclear_or_incomplete -> general_inquiry` (2 tickets)**:
   - Tickets `EXT-3-109` and `EXT-3-152`: Pure gratitude/salutation messages routed to `general_inquiry` by the `pure_gratitude` rule.

5. **Scattered Singletons (14 tickets)**:
   - 14 individual confusions occurring exactly once across 14 distinct category pairs.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `dev.jsonl`.
- **Evaluation**:
  - No directional category confusion in Batch 017 exceeds 2 tickets.
  - The largest cluster of related errors (`wrong_recipient -> failed_transfer`) contains only 2 tickets and originates from a single dialect cluster (`western`).
  - The reciprocal confusions (`app_bug` $\leftrightarrow$ `login_problem`) consist of 2 tickets in each direction, neither of which qualifies individually.
- **Decision**: **No rule remediation qualifies under S5**. In strict adherence to Protocol S5 and Ponytail architectural discipline ("the best code is the code never written"), zero code changes are proposed.
- **Offline Model Status**: Preserved at `rules_dialect_ml_v11`.
