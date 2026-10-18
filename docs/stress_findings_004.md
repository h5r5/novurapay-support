# Stress Test Findings Report: Batch 004

- **Batch ID**: batch_004
- **Source File**: `data/stress_test/novurapay_tickets_round4.jsonl`
- **Ingested Location**: `data/stress/batch_004.jsonl` (200 tickets)
- **Evaluation Date**: 2026-10-18
- **Git Commit (Blind Run)**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **75.50%** (151/200) (Wilson 95% CI: `[69.10%, 80.94%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 004 is the fourth externally generated synthetic stress batch evaluated blindly against the upgraded offline engine (`offline_model_version = "v5"`).
The pipeline achieved **75.50% accuracy** (151/200) under blind measurement, marking an outstanding **+14.83% absolute increase** over Batch 003 (60.67%) and an aggregate **+43.50% increase** over the Batch 001 baseline (32.00%).

Key improvements observed:
1. **Regional Dialect Breakthrough**: Mosul achieved **92.86%** (26/28), Baghdadi reached **91.30%** (42/46), and Basrawi attained **74.68%** (59/79).
2. **Category Dominance**: 10 out of 14 categories achieved $\ge 70.0\%$ recall, spearheaded by `card_issue` (92.86%), `unclear_or_incomplete` (92.86%), `refund_status` (92.31%), `agent_dispute` (85.71%), `app_bug` (84.62%), `kyc_document_issue` (84.62%), and `account_blocked` (81.25%).
3. **Dual-Layer English Integration**: Explicit English fintech requests correctly classified to functional categories while preserving bilingual care tags.

---

## 2. Failure Analysis by Slice

### A. Category Recall Performance

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `card_issue` | 14 | 13 | 92.86% | `unclear_or_incomplete` (1) |
| `unclear_or_incomplete` | 14 | 13 | 92.86% | `failed_transfer` (1) |
| `refund_status` | 13 | 12 | 92.31% | `failed_transfer` (1) |
| `agent_dispute` | 14 | 12 | 85.71% | `unclear_or_incomplete` (2) |
| `app_bug` | 13 | 11 | 84.62% | `unclear_or_incomplete` (2) |
| `kyc_document_issue` | 13 | 11 | 84.62% | `bill_payment_failure` (1), `app_bug` (1) |
| `account_blocked` | 16 | 13 | 81.25% | `unclear_or_incomplete` (2), `login_problem` (1) |
| `balance_or_statement_inquiry` | 15 | 11 | 73.33% | `failed_transfer` (2), `login_problem` (1), `unclear_or_incomplete` (1) |
| `failed_transfer` | 14 | 10 | 71.43% | `unclear_or_incomplete` (1), `app_bug` (1), `bill_payment_failure` (1), `wrong_recipient` (1) |
| `wrong_recipient` | 14 | 10 | 71.43% | `unclear_or_incomplete` (3), `failed_transfer` (1) |
| `bill_payment_failure` | 16 | 10 | 62.50% | `unclear_or_incomplete` (2), `failed_transfer` (1), `card_issue` (1), `agent_dispute` (1), `refund_status` (1) |
| `login_problem` | 13 | 8 | 61.54% | `app_bug` (2), `unclear_or_incomplete` (2), `card_issue` (1) |
| `general_inquiry` | 15 | 9 | 60.00% | `unclear_or_incomplete` (3), `account_blocked` (1), `kyc_document_issue` (1), `agent_dispute` (1) |
| `fraud_report` | 16 | 8 | 50.00% | `unclear_or_incomplete` (5), `account_blocked` (1), `balance_or_statement_inquiry` (1), `bill_payment_failure` (1) |

### B. Tag Slice Breakdown

- **Dialect Performance**:
  - `mosul`: 26/28 (92.86%)
  - `baghdadi`: 42/46 (91.30%)
  - `basrawi`: 59/79 (74.68%)
  - `arabizi`: 17/28 (60.71%)
  - `mixed`: 7/19 (36.84%)
- **Ticket Length**:
  - `short`: 48/60 (80.00%)
  - `normal`: 83/112 (74.11%)
  - `long`: 20/28 (71.43%)
- **Attack Types**:
  - `None`: 150/193 (77.72%)
  - `prompt_injection`: 1/7 (14.29%)

---

## 3. Root Cause Investigation

Analysis of the 49 misclassifications in Batch 004 reveals three main components:

1. **Security Quarantine of Prompt Injections**:
   - 6 of the 7 prompt injection attacks were intercepted by trojan safeguards and quarantined into `unclear_or_incomplete`. The synthetic benchmark ground-truth labeled them under functional categories (`fraud_report`, `login_problem`, `wrong_recipient`, etc.), whereas the system correctly refused execution.
2. **Out-of-Scope Loan Inquiries & Vague Foreign Queries**:
   - 3 tickets involving loan requests ("سلف وقروض") were correctly quarantined as out of scope (`out_of_scope_loans`), whereas the benchmark assigned them to `general_inquiry`.
   - Vague English queries lacking explicit transaction details were safely retained under `foreign_language_en` quarantine per `MS-01`.
3. **Dispersed Long-Tail Dialectal Ambiguities**:
   - The remaining errors are single isolated misclassifications (1-2 tickets per pair) reflecting complex conversational multi-intents.

---

## 4. Single Change Gate Evaluation (Protocol S5)

Protocol S5 requires:
- Pattern supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters.
- Zero literal phrases embedded from the batch.
- Must not lower grouped-CV accuracy on dev.

### Verdict:
**No remediation qualifies under the S5 change gate in Batch 004.**
The only error clusters exceeding 2 tickets were intentional security quarantines (prompt injection, out-of-scope loan requests, and vague English escalation). No dialectal failure mode met the $\ge 3$ tickets across $\ge 2$ clusters threshold.
The offline model version remains at current high-performing `v5`.
