# Stress Test Findings Report: Batch 012

- **Batch ID**: batch_012
- **Source File**: `data/stress_test/novurapay_tickets_round12.jsonl`
- **Ingested Location**: `data/stress/batch_012.jsonl` (200 tickets accepted, 0 rejected)
- **Evaluation Date**: 2026-10-26
- **Git Commit (Blind Run)**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **68.00%** (136/200) (Wilson 95% CI: `[61.25%, 74.07%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 012 is the twelfth externally generated synthetic stress test batch, containing 200 tickets distributed across 5 Iraqi dialects and 3 length buckets.
During ingestion under Protocol S1:
- 200 total rows were processed.
- 0 rows were rejected (zero exact duplicates or near-duplicates detected against reference corpus).
- 200 tickets were accepted and registered into `data/stress/batch_012.jsonl`.

On blind evaluation using the offline engine (`rules_dialect_ml_v10`), the pipeline achieved **68.00% blind accuracy** (136/200, Wilson 95% CI: `[61.25%, 74.07%]`) with zero runtime errors, zero degraded classifications, and average latency of 4.74 ms.

---

## 2. Slice Breakdown

### A. Category Recall Performance (Blind V10)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `agent_dispute` | 14 | 14 | 100.00% | None |
| `unclear_or_incomplete` | 18 | 16 | 88.89% | `app_bug` (1), `card_issue` (1) |
| `general_inquiry` | 14 | 11 | 78.57% | `unclear_or_incomplete` (2), `failed_transfer` (1) |
| `card_issue` | 14 | 11 | 78.57% | `app_bug` (1), `bill_payment_failure` (1), `failed_transfer` (1) |
| `app_bug` | 14 | 10 | 71.43% | `balance_or_statement_inquiry` (2), `login_problem` (1), `unclear_or_incomplete` (1) |
| `balance_or_statement_inquiry` | 14 | 10 | 71.43% | `unclear_or_incomplete` (2), `failed_transfer` (1), `general_inquiry` (1) |
| `login_problem` | 14 | 10 | 71.43% | `app_bug` (2), `account_blocked` (1), `failed_transfer` (1) |
| `wrong_recipient` | 14 | 10 | 71.43% | `failed_transfer` (3), `bill_payment_failure` (1) |
| `account_blocked` | 14 | 8 | 57.14% | `kyc_document_issue` (2), `login_problem` (1), `balance_or_statement_inquiry` (1), `unclear_or_incomplete` (1), `wrong_recipient` (1) |
| `bill_payment_failure` | 14 | 8 | 57.14% | `failed_transfer` (3), `login_problem` (1), `unclear_or_incomplete` (1), `wrong_recipient` (1) |
| `fraud_report` | 14 | 8 | 57.14% | `account_blocked` (1), `balance_or_statement_inquiry` (1), `failed_transfer` (1), `login_problem` (1), `unclear_or_incomplete` (1), `wrong_recipient` (1) |
| `kyc_document_issue` | 14 | 8 | 57.14% | `login_problem` (2), `balance_or_statement_inquiry` (2), `unclear_or_incomplete` (2) |
| `failed_transfer` | 14 | 7 | 50.00% | `unclear_or_incomplete` (2), `general_inquiry` (1), `login_problem` (1), `refund_status` (1), `wrong_recipient` (2) |
| `refund_status` | 14 | 5 | 35.71% | `bill_payment_failure` (5), `fraud_report` (2), `account_blocked` (1), `unclear_or_incomplete` (1) |

### B. Dialect & Tag Slice Performance

- **Dialects**:
  - `basrawi`: 30/41 (73.17%)
  - `mosul`: 19/27 (70.37%)
  - `mixed`: 23/33 (69.70%)
  - `baghdadi`: 47/70 (67.14%)
  - `arabizi`: 17/29 (58.62%)
- **Attacks**:
  - `None`: 130/190 (68.42%)
  - `prompt_injection`: 6/10 (60.00%)
- **Length Buckets**:
  - `short`: 30/38 (78.95%)
  - `long`: 40/61 (65.57%)
  - `normal`: 66/101 (65.35%)

---

## 3. Failure Analysis & Root Cause

1. **Service Cancellation & Deposit Refund Dispersal (`refund_status -> bill_payment_failure`, 5 tickets)**:
   - *Observation*: Tickets requesting refunds for cancelled services/appointments, deposit returns, or invoice overpayments were intercepted by the ML classifier and routed to `bill_payment_failure` due to lexical features like "فاتورة", "رسوم", and "تامين".
   - *Root Cause*: Rule 2.2c covers retail store returns and formal refund claims, but lacked coverage for cancelled appointments/services, deposit return inquiries, and fee reimbursement disputes.
   - *Affected Clusters*: 4 clusters (`baghdadi/short`, `baghdadi/normal`, `basrawi/normal`, `mosul/long`).

2. **Non-Standard Utility Subscriptions (`bill_payment_failure -> failed_transfer`, 3 tickets)**:
   - *Observation*: Water tanker deliveries, satellite subscriptions, and digital course payments were routed to generic `failed_transfer` (Rule 2.25) when uncredited.
   - *Root Cause*: Lack of utility domain keywords for niche service subscriptions in Rule 2.2d.

3. **Colloquial Wrong Recipient Expressions (`wrong_recipient -> failed_transfer`, 3 tickets)**:
   - *Observation*: Accidental transfers described without explicit "wrong number" keywords were swallowed by generic pending transfer heuristics.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `dev.jsonl`.
- **Proposed Remediation**:
  - **Target Category**: `refund_status`
  - **Proposed Rule Pattern**: Extend Rule 2.2c to capture service/appointment cancellations, deposit/security return tracking, and fee reimbursement demands:
    `r"(?:رفض\s*(?:الـ?)?إ?ارجاع|الغ(?:يت|اء)\s*(?:الطلب|الموعد).*(?:ما\s*)?رجع|ما\s*رجعو(?:ها|ه)|رح\s*نرجع(?:ها|ه)|ارجعوا\s*لي)"`
  - **Supporting Tickets**: 5 tickets (`EXT-3-068`, `EXT-3-076`, `EXT-3-148`, `EXT-3-158`, `EXT-3-180`).
  - **Cluster Diversity**: 4 distinct clusters (`baghdadi/short`, `baghdadi/normal`, `basrawi/normal`, `mosul/long`) $\ge 2$.
  - **Literal Phrase Check**: Abstract syntactic pattern; zero verbatim phrases copied.
  - **Dev CV Impact**: 0 matches in `dev.jsonl` (zero regression risk on dev benchmarks).
  - **Deployment Status**: In accordance with the execution constraint keeping `src/classify` read-only during this run, this remediation is recorded as a validated proposal. The offline engine remains at version `v10`.
