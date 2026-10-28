# Stress Test Findings Report: Batch 018

- **Batch ID**: batch_018
- **Source File**: `data/stress_test/novurapay_tickets_round18.jsonl`
- **Ingested Location**: `data/stress/batch_018.jsonl` (347 tickets accepted, 3 duplicate rows rejected)
- **Evaluation Date**: 2026-10-27
- **Git Commit (Blind Run)**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **85.01%** (295/347) (Wilson 95% CI: `[80.88%, 88.39%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 018 is the eighteenth externally generated synthetic stress test batch, containing 350 tickets spanning 5 Iraqi dialects (`baghdadi`, `basrawi`, `mosul`, `mixed`, `arabizi`), 3 length categories, and adversarial prompt injections.

During ingestion under Protocol S1:
- 350 total rows were processed.
- 3 duplicate rows were rejected:
  - Row 8 (`EXT-17-008`): Exact duplicate text of ticket `EXT-1-059` from `batch_001.jsonl`.
  - Row 182 (`EXT-17-182`): Normalized near-duplicate (similarity ratio $0.939 \ge 0.90$) with ticket `EXT-3-200` from `batch_017.jsonl`.
  - Row 259 (`EXT-17-259`): Exact duplicate text of ticket `EXT-1-015` from `batch_001.jsonl`.
- 347 valid tickets were accepted and registered into `data/stress/batch_018.jsonl`.

On blind evaluation using the offline engine (`rules_dialect_ml_v11`), the pipeline achieved **85.01% blind accuracy** (295/347, Wilson 95% CI: `[80.88%, 88.39%]`) with zero runtime errors, zero degraded classifications, and average latency of 5.16 ms.

---

## 2. Slice Breakdown

### A. Category Recall Performance (Blind V11)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `fraud_report` | 21 | 20 | 95.24% | `app_bug` (1) |
| `agent_dispute` | 20 | 19 | 95.00% | `failed_transfer` (1) |
| `unclear_or_incomplete` | 17 | 16 | 94.12% | `general_inquiry` (1) |
| `account_blocked` | 21 | 19 | 90.48% | `kyc_document_issue` (1), `login_problem` (1) |
| `bill_payment_failure` | 21 | 19 | 90.48% | `failed_transfer` (1), `card_issue` (1) |
| `failed_transfer` | 21 | 19 | 90.48% | `login_problem` (1), `general_inquiry` (1) |
| `balance_or_statement_inquiry` | 20 | 18 | 90.00% | `refund_status` (1), `general_inquiry` (1) |
| `kyc_document_issue` | 20 | 18 | 90.00% | `login_problem` (1), `general_inquiry` (1) |
| `wrong_recipient` | 20 | 18 | 90.00% | `failed_transfer` (2) |
| `card_issue` | 42 | 35 | 83.33% | `bill_payment_failure` (2), `refund_status` (1), `unclear_or_incomplete` (1), `login_problem` (1), `app_bug` (1), `general_inquiry` (1) |
| `app_bug` | 20 | 16 | 80.00% | `balance_or_statement_inquiry` (2), `login_problem` (2) |
| `refund_status` | 42 | 32 | 76.19% | `bill_payment_failure` (4), `balance_or_statement_inquiry` (2), `unclear_or_incomplete` (1), `failed_transfer` (1), `card_issue` (1), `login_problem` (1) |
| `general_inquiry` | 20 | 15 | 75.00% | `unclear_or_incomplete` (2), `app_bug` (1), `bill_payment_failure` (1), `login_problem` (1) |
| `login_problem` | 42 | 31 | 73.81% | `app_bug` (8), `account_blocked` (2), `unclear_or_incomplete` (1) |

### B. Dialect & Tag Slice Performance

- **Dialects**:
  - `mixed`: 57/63 (90.48%)
  - `basrawi`: 61/68 (89.71%)
  - `mosul`: 44/50 (88.00%)
  - `baghdadi`: 97/121 (80.17%)
  - `arabizi`: 36/45 (80.00%)
- **Attacks**:
  - `None`: 283/330 (85.76%)
  - `prompt_injection`: 12/17 (70.59%)
- **Length Buckets**:
  - `short`: 54/62 (87.10%)
  - `normal`: 160/185 (86.49%)
  - `long`: 81/100 (81.00%)

---

## 3. Failure Analysis & Root Cause

Total misclassifications across the batch: 52 tickets out of 347 (14.99%).
Analysis reveals two primary structural clusters:

1. **Authentication Crash & Error Code Disambiguation (`login_problem -> app_bug`, 8 tickets)**:
   - *Observation*: Customers reporting inability to sign in because the app closes, freezes, or throws an error code specifically during the authentication phase (`تسجيل الدخول`).
   - *Root Cause*: Because the text contains technical fault terms (`خطأ`, `يخرج التطبيق`, `كود`), the ML pipeline weighted `app_bug` over `login_problem`.
   - *Affected Clusters*: 5 distinct tickets (`EXT-17-001`, `EXT-17-059`, `EXT-17-104`, `EXT-17-319`, `EXT-17-329`) span 4 dialects (`mixed`, `baghdadi`, `basrawi`, `mosul`) and all long length bucket.

2. **Refund for Utility/Subscription Cancellation (`refund_status -> bill_payment_failure`, 4 tickets)**:
   - *Observation*: Customers requesting refund status for a cancelled utility payment or subscription.
   - *Root Cause*: Preponderance of bill terms (`فاتورة`, `قسط`, `اشتراك`) caused the ML classifier to classify as bill failure despite explicit refund demand.
   - *Affected Clusters*: 2 dialects (`baghdadi`, `mosul`) across 4 tickets (`EXT-17-098`, `EXT-17-129`, `EXT-17-176`, `EXT-17-191`).

3. **Minor Confusions**:
   - `wrong_recipient -> failed_transfer` (2 tickets).
   - `login_problem -> account_blocked` (2 tickets).
   - `general_inquiry -> unclear_or_incomplete` (2 tickets).
   - Other scattered pairs (1 occurrence each).

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `dev.jsonl`.
- **Proposed Remediation Candidate**:
  - **Target Category**: `login_problem`
  - **Proposed Rule Pattern**: Extend Rule 2.2b to capture explicit authentication failure accompanied by application error codes or technical crashes during sign-in:
    `r"(?:(?:خطأ|كود|رمز|يخرج|معلق).*(?:في|عند|بـ)?\s*تسجيل\s*(?:الـ?)?دخول|تسجيل\s*(?:الـ?)?دخول.*(?:يظهر\s*لي\s*خطأ|يعطي\s*خطأ|يخرج|يغلق|معلق))"`
  - **Supporting Tickets**: 5 tickets (`EXT-17-001`, `EXT-17-059`, `EXT-17-104`, `EXT-17-319`, `EXT-17-329`).
  - **Cluster Diversity**: 4 distinct dialect clusters (`mixed/long`, `baghdadi/long`, `basrawi/long`, `mosul/long`) $\ge 2$.
  - **Literal Phrase Check**: Syntactic generalized regex; zero literal sentences copied.
  - **Dev CV Impact**: 0 matches in `dev.jsonl` (zero regression risk, grouped-CV accuracy unchanged at 94.98%).
  - **Deployment Status**: Under the operational constraint keeping `src/classify` read-only during this run, this remediation is recorded as a validated proposal. The offline engine remains at version `v11`.
