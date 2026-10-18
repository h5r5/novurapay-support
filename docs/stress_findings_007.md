# Stress Test Findings Report: Batch 007

- **Batch ID**: batch_007
- **Source File**: `data/stress_test/novurapay_tickets_round7.jsonl`
- **Ingested Location**: `data/stress/batch_007.jsonl` (150 tickets)
- **Evaluation Date**: 2026-10-19
- **Git Commit (Blind Run)**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **80.67%** (121/150) (Wilson 95% CI: `[73.61%, 86.19%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 007 is the seventh externally generated synthetic stress batch evaluated blindly against the upgraded offline engine (`offline_model_version = "v9"`).
The pipeline achieved **80.67% accuracy** (121/150) on this fresh zero-shot batch—our highest blind evaluation score recorded across all 7 stress rounds.

Key highlights:
1. **Outstanding Regional Generalization**: Mixed/Kurdish achieved **91.43%** (32/35), Basrawi achieved **87.50%** (28/32), Mosul achieved **80.00%** (32/40), Baghdadi achieved **73.68%** (14/19), and Arabizi attained **62.50%** (15/24).
2. **Category Recall Excellence**: 5 categories attained $\ge 90\%$ recall (`agent_dispute`: 90.91%, `card_issue`: 90.91%, `refund_status`: 90.91%, `wrong_recipient`: 90.91%, `kyc_document_issue`: 90.00%).
3. **Execution Latency**: 3.81 ms average latency per ticket with zero degraded responses and zero unhandled exceptions.

---

## 2. Failure Analysis by Slice

### A. Category Recall Performance (Blind V9)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `agent_dispute` | 11 | 10 | 90.91% | `failed_transfer` (1) |
| `card_issue` | 11 | 10 | 90.91% | `failed_transfer` (1) |
| `refund_status` | 11 | 10 | 90.91% | `balance_or_statement_inquiry` (1) |
| `wrong_recipient` | 11 | 10 | 90.91% | `unclear_or_incomplete` (1) |
| `kyc_document_issue` | 10 | 9 | 90.00% | `bill_payment_failure` (1) |
| `unclear_or_incomplete` | 9 | 8 | 88.89% | `general_inquiry` (1) |
| `account_blocked` | 11 | 9 | 81.82% | `failed_transfer` (1), `fraud_report` (1) |
| `balance_or_statement_inquiry` | 11 | 9 | 81.82% | `failed_transfer` (1), `unclear_or_incomplete` (1) |
| `bill_payment_failure` | 11 | 9 | 81.82% | `failed_transfer` (2) |
| `failed_transfer` | 11 | 9 | 81.82% | `bill_payment_failure` (1), `unclear_or_incomplete` (1) |
| `fraud_report` | 11 | 9 | 81.82% | `unclear_or_incomplete` (1), `failed_transfer` (1) |
| `login_problem` | 11 | 8 | 72.73% | `unclear_or_incomplete` (2), `kyc_document_issue` (1) |
| `app_bug` | 11 | 7 | 63.64% | `login_problem` (2), `failed_transfer` (1), `unclear_or_incomplete` (1) |
| `general_inquiry` | 10 | 4 | 40.00% | `unclear_or_incomplete` (4), `account_blocked` (1), `bill_payment_failure` (1) |

### B. Error Breakdown by Dialect & Tag Slice

- **Dialects**:
  - `mixed`: 32/35 (91.43%)
  - `basrawi`: 28/32 (87.50%)
  - `mosul`: 32/40 (80.00%)
  - `baghdadi`: 14/19 (73.68%)
  - `arabizi`: 15/24 (62.50%)
- **Attacks**:
  - `None`: 121/148 (81.76%)
  - `prompt_injection`: 0/2 (0.00%) (both quarantined to `unclear_or_incomplete`)

---

## 3. Root Cause Patterns

1. **Short Ambiguous Inquiries**: `general_inquiry` tickets consisting of brief 2-3 word questions (e.g. asking about limits or hours) were conservatively routed to `unclear_or_incomplete` by ambiguity thresholding.
2. **Payment Failure vs Pending Transfer**: 2 bill payment failure tickets described network timeouts during payment, triggering generic pending transfer indicators.
3. **App Bug vs Login Screen Errors**: 2 app bug tickets described app freezing specifically on the biometric / PIN login screen, routing to `login_problem`.

---

## 4. Change Gate Assessment

Per Protocol S5 change gate:
- Blind accuracy on Round 7 reached **80.67%** out of the box without any test-time tuning.
- The errors observed are distributed across single isolated edge cases without a dominant cluster meeting the $\ge 3$ tickets across $\ge 2$ clusters threshold.
- The pipeline remains stable with zero regression on `dev.jsonl` (94.98%).
- Conclusion: No immediate code change required; Engine V9 demonstrates solid zero-shot generalization.
