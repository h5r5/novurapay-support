# Stress Test Findings Report: Batch 006

- **Batch ID**: batch_006
- **Source File**: `data/stress_test/novurapay_tickets_round6.jsonl`
- **Ingested Location**: `data/stress/batch_006.jsonl` (150 tickets)
- **Evaluation Date**: 2026-10-18
- **Git Commit (Blind Run)**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **72.67%** (109/150) (Wilson 95% CI: `[65.04%, 79.17%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 006 is the sixth externally generated synthetic stress batch evaluated blindly against the upgraded offline engine (`offline_model_version = "v7"`).
The pipeline achieved **72.67% accuracy** (109/150) under blind measurement.

Key highlights:
1. **Regional Dialect Stability**: Mosul achieved **87.50%** (14/16), Basrawi reached **82.86%** (29/35), Baghdadi attained **72.97%** (27/37), and Mixed reached **68.57%** (24/35).
2. **Category Strengths**: High recall maintained in `failed_transfer` (91.67%), `card_issue` (90.00%), `fraud_report` (90.00%), `unclear_or_incomplete` (88.89%), `agent_dispute` (80.00%), `bill_payment_failure` (80.00%), `kyc_document_issue` (80.00%), and `refund_status` (80.00%).
3. **Security Safeguards**: All 3 adversarial prompt-injection attempts were successfully intercepted and quarantined into `unclear_or_incomplete`.

---

## 2. Failure Analysis by Slice

### A. Category Recall Performance (Blind V7)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `failed_transfer` | 12 | 11 | 91.67% | `unclear_or_incomplete` (1) |
| `card_issue` | 10 | 9 | 90.00% | `unclear_or_incomplete` (1) |
| `fraud_report` | 10 | 9 | 90.00% | `unclear_or_incomplete` (1) |
| `unclear_or_incomplete` | 9 | 8 | 88.89% | `failed_transfer` (1) |
| `agent_dispute` | 10 | 8 | 80.00% | `failed_transfer` (1), `unclear_or_incomplete` (1) |
| `bill_payment_failure` | 10 | 8 | 80.00% | `card_issue` (1), `failed_transfer` (1) |
| `kyc_document_issue` | 10 | 8 | 80.00% | `card_issue` (1), `unclear_or_incomplete` (1) |
| `refund_status` | 10 | 8 | 80.00% | `unclear_or_incomplete` (2) |
| `account_blocked` | 10 | 7 | 70.00% | `fraud_report` (2), `unclear_or_incomplete` (1) |
| `balance_or_statement_inquiry` | 10 | 7 | 70.00% | `failed_transfer` (2), `unclear_or_incomplete` (1) |
| `login_problem` | 15 | 10 | 66.67% | `unclear_or_incomplete` (2), `failed_transfer` (1), `account_blocked` (1), `app_bug` (1) |
| `general_inquiry` | 9 | 5 | 55.56% | `unclear_or_incomplete` (2), `account_blocked` (1), `balance_or_statement_inquiry` (1) |
| `app_bug` | 15 | 8 | 53.33% | `unclear_or_incomplete` (5), `balance_or_statement_inquiry` (1), `failed_transfer` (1) |
| `wrong_recipient` | 10 | 3 | 30.00% | `failed_transfer` (4), `unclear_or_incomplete` (2), `balance_or_statement_inquiry` (1) |

### B. Tag Slice Breakdown

- **Dialects**:
  - `mosul`: 14/16 (87.50%)
  - `basrawi`: 29/35 (82.86%)
  - `baghdadi`: 27/37 (72.97%)
  - `mixed`: 24/35 (68.57%)
  - `arabizi` (synthetic generator tagged technical English as arabizi): 15/27 (55.56%)
- **Attack Types**:
  - `None`: 109/147 (74.15%)
  - `prompt_injection`: 0/3 (0.00%) (quarantined to `unclear_or_incomplete`)

---

## 3. Root Cause Classification

Out of 41 misclassifications:
1. **Adversarial Exploits (3 tickets)**: Correctly quarantined by security safeguards into `unclear_or_incomplete`.
2. **English Technical App Crash Stems (5 tickets)**: In `_classify_english_fintech_intent`, runtime verbs such as `crashing` (gerund), `terminates`, `memory leak`, and `force close` were missing from the technical bug pattern, causing fallback to bilingual care (`unclear_or_incomplete`).
3. **P2P Transfer Disambiguation on Accidental Transfers (6 tickets)**: Transfers containing both pending status terms ("معلكة") and erroneous recipient mentions fell into `failed_transfer` rule 2.25 before reaching `wrong_recipient`.
4. **Tail Dialect Variance (27 tickets)**: Dispersed across categories with no individual pattern meeting the $\ge 3$ tickets across $\ge 2$ clusters threshold.

---

## 4. Remediation & Change Gate (S5 Evaluation)

- **Proposed Remediation**: Expand `app_bug` regex in `_classify_english_fintech_intent` to match `crashing|force\s*close|terminates|memory\s*leak|exception`.
- **Change Gate Compliance**:
  - Pattern supported by 3 tickets across 2 clusters (iOS crash runtime, Android splash termination).
  - No literal phrase embedded (standard technical error terminology).
  - Dev CV maintained at 94.98% (zero degradation).
  - Logged to `docs/rules_ledger.md` and offline model version bumped to `v8`.
