# Stress Test Findings Report: Batch 008

- **Batch ID**: batch_008
- **Source File**: `data/stress_test/novurapay_tickets_round8.jsonl`
- **Ingested Location**: `data/stress/batch_008.jsonl` (198 tickets accepted, 2 duplicate rows rejected)
- **Evaluation Date**: 2026-10-20
- **Git Commit (Blind Run)**: `f0ceaaa9e3a9ba84ced4c59fca078c366ca1439b`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **75.76%** (150/198) (Wilson 95% CI: `[69.33%, 81.20%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 008 is the eighth externally generated synthetic stress batch evaluated blindly against the upgraded offline engine (`offline_model_version = "v9"`).
The raw batch contained 200 tickets; 2 exact duplicates of earlier batch tickets were identified and rejected during ingestion per protocol S1 (`EXT-1-072` matching `EXT-1-015` in `batch_001.jsonl`, and `EXT-1-165` matching `EXT-1-059` in `batch_001.jsonl`).
On the 198 valid accepted tickets, the pipeline achieved **75.76% blind accuracy** (150/198, Wilson 95% CI: `[69.33%, 81.20%]`).

Key highlights:
1. **Dialect Robustness**: Mixed/Kurdish code-switching achieved **84.62%** (33/39), Arabizi achieved **81.25%** (26/32), Basrawi achieved **77.14%** (27/35), Mosul achieved **76.67%** (23/30), and Baghdadi achieved **66.13%** (41/62).
2. **Category Recall Highlights**: Three core financial categories attained **91.67%** recall (`balance_or_statement_inquiry`, `bill_payment_failure`, `failed_transfer`), followed by `unclear_or_incomplete` (85.71%), `app_bug` (81.82%), and `account_blocked` (80.00%).
3. **Security Safeguards**: Adversarial prompt injection attempts were actively intercepted and quarantined into `unclear_or_incomplete`.
4. **Execution Latency**: 4.15 ms average latency per ticket with zero degraded responses and zero unhandled runtime exceptions.

---

## 2. Failure Analysis by Slice

### A. Category Recall Performance (Blind V9)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `balance_or_statement_inquiry` | 12 | 11 | 91.67% | `unclear_or_incomplete` (1) |
| `bill_payment_failure` | 12 | 11 | 91.67% | `card_issue` (1) |
| `failed_transfer` | 12 | 11 | 91.67% | `unclear_or_incomplete` (1) |
| `unclear_or_incomplete` | 14 | 12 | 85.71% | `balance_or_statement_inquiry` (1), `kyc_document_issue` (1) |
| `app_bug` | 22 | 18 | 81.82% | `login_problem` (4) |
| `account_blocked` | 20 | 16 | 80.00% | `unclear_or_incomplete` (2), `login_problem` (1), `refund_status` (1) |
| `agent_dispute` | 12 | 9 | 75.00% | `failed_transfer` (1), `refund_status` (1), `card_issue` (1) |
| `card_issue` | 12 | 9 | 75.00% | `bill_payment_failure` (1), `failed_transfer` (1), `app_bug` (1) |
| `refund_status` | 12 | 9 | 75.00% | `failed_transfer` (2), `unclear_or_incomplete` (1) |
| `login_problem` | 20 | 14 | 70.00% | `unclear_or_incomplete` (2), `app_bug` (2), `bill_payment_failure` (1), `fraud_report` (1) |
| `kyc_document_issue` | 12 | 8 | 66.67% | `account_blocked` (2), `unclear_or_incomplete` (2) |
| `wrong_recipient` | 12 | 8 | 66.67% | `failed_transfer` (3), `unclear_or_incomplete` (1) |
| `general_inquiry` | 14 | 8 | 57.14% | `unclear_or_incomplete` (3), `app_bug` (2), `kyc_document_issue` (1) |
| `fraud_report` | 12 | 6 | 50.00% | `unclear_or_incomplete` (2), `card_issue` (1), `login_problem` (1), `account_blocked` (1), `bill_payment_failure` (1) |

### B. Error Breakdown by Dialect & Tag Slice

- **Dialects**:
  - `mixed`: 33/39 (84.62%)
  - `arabizi`: 26/32 (81.25%)
  - `basrawi`: 27/35 (77.14%)
  - `mosul`: 23/30 (76.67%)
  - `baghdadi`: 41/62 (66.13%)
- **Attacks**:
  - `None`: 144/185 (77.84%)
  - `prompt_injection`: 6/13 (46.15%) (unmatched injections routed safely to `unclear_or_incomplete`)
- **Length Buckets**:
  - `long`: 45/56 (80.36%)
  - `short`: 35/44 (79.55%)
  - `normal`: 70/98 (71.43%)

---

## 3. Root Cause Patterns

1. **Security Prompt Injection Quarantine (7 tickets)**: Injected prompts containing adversarial system override requests across multiple categories (`fraud_report`, `account_blocked`, `login_problem`, `general_inquiry`) were quarantined into `unclear_or_incomplete`.
2. **App Store & Installation Stems (`app_bug -> login_problem`, 4 tickets)**: Tickets describing store download errors, OS compatibility, or stalled package downloads were routed to `login_problem` by subword n-gram similarities in Baghdadi dialect.
3. **Accidental P2P Transfer Nuance (`wrong_recipient -> failed_transfer`, 3 tickets)**: Tickets describing transfers to wrong contacts with partial return or cancellation requests were routed to pending transfer ML representations.
4. **KYC Expiration Warning vs Account Block (`kyc_document_issue -> account_blocked`, 2 tickets)**: Tickets describing expired national ID cards with impending account restriction warnings were routed to `account_blocked`.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `dev.jsonl`.
- **Evaluation of Error Clusters**:
  1. `app_bug -> login_problem` (4 tickets): All 4 tickets originate from a single dialect cluster (`baghdadi`). Fails the requirement of $\ge 2$ batch-tag clusters.
  2. `general_inquiry -> unclear_or_incomplete` (3 tickets): 2 of the 3 tickets are adversarial prompt injection attacks intentionally quarantined by safety guards. Fails the requirement for a valid functional pattern.
  3. `wrong_recipient -> failed_transfer` (3 tickets): Distinct syntactic formulations across 2 clusters without a safe shared root or semantic regex pattern that would avoid false positives against general transfer issues.
- **Verdict**: **No change qualifies under S5 gate criteria.** Offline model version remains at `v9`. Zero regression on `dev.jsonl` (94.98%).
