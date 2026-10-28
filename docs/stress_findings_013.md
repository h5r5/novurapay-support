# Stress Test Findings Report: Batch 013

- **Batch ID**: batch_013
- **Source File**: `data/stress_test/novurapay_tickets_round13.jsonl`
- **Ingested Location**: `data/stress/batch_013.jsonl` (15 tickets accepted, 20 invalid rows rejected)
- **Evaluation Date**: 2026-10-26
- **Git Commit (Blind Run)**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **80.00%** (12/15) (Wilson 95% CI: `[54.81%, 92.95%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 013 was submitted as the thirteenth externally generated synthetic stress test batch.
During ingestion under Protocol S1:
- 35 total rows were processed.
- 20 rows were rejected due to invalid category labels outside the authorized 14-category taxonomy:
  - `wrong_recipient_transfer` (2 rows)
  - `login_or_auth_issue` (3 rows)
  - `account_or_device_blocked` (2 rows)
  - `agent_or_cash_in_out` (2 rows)
  - `kyc_or_verification` (3 rows)
  - `fraud_or_phishing_report` (3 rows)
  - `refund_or_reversal_status` (2 rows)
  - `app_bug_or_crash` (3 rows)
- 15 valid rows were accepted and registered into `data/stress/batch_013.jsonl`.

On blind evaluation using the offline engine (`rules_dialect_ml_v10`), the pipeline achieved **80.00% blind accuracy** (12/15, Wilson 95% CI: `[54.81%, 92.95%]`) with zero degraded classifications and 4.54 ms average latency.

---

## 2. Slice Breakdown

### Category Recall Performance (Blind V10)

| Category | Total (Gold) | Correct | Recall | Confusions |
|---|---|---|---|---|
| `balance_or_statement_inquiry` | 2 | 2 | 100.00% | None |
| `bill_payment_failure` | 3 | 3 | 100.00% | None |
| `unclear_or_incomplete` | 2 | 2 | 100.00% | None |
| `card_issue` | 3 | 2 | 66.67% | `unclear_or_incomplete` (1) |
| `failed_transfer` | 3 | 2 | 66.67% | `card_issue` (1) |
| `general_inquiry` | 2 | 1 | 50.00% | `unclear_or_incomplete` (1) |

*(Note: Batch 013 raw tickets did not specify granular dialect/tag attributes).*

---

## 3. Failure Analysis & Root Cause

The 3 misclassified tickets represent isolated individual edge cases:
1. `TKT-1003` (`failed_transfer -> card_issue`): Multi-issue complaint mentioning both an uncredited P2P transfer and ATM Mastercard decline; card issues triggered card heuristics first.
2. `TKT-1013` (`card_issue -> unclear_or_incomplete`): Generic phrasing regarding card activation without explicit hardware/PIN identifiers.
3. `TKT-1033` (`general_inquiry -> unclear_or_incomplete`): Vague service inquiry routed to human triage via unclear safeguard.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `dev.jsonl`.
- **Finding**: Each of the 3 errors is an isolated single occurrence ($N = 1$). No error pattern reaches the $\ge 3$ tickets threshold.
- **Decision**: Nothing qualifies under the S5 change gate. No rule change is proposed or adopted. The offline engine remains at version `v10`.
