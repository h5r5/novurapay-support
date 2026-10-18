# Stress Test Findings Report: Batch 003

- **Batch ID**: batch_003
- **Source File**: `data/stress_test/novurapay_tickets_round3.jsonl`
- **Ingested Location**: `data/stress/batch_003.jsonl` (150 tickets)
- **Evaluation Date**: 2026-10-18
- **Git Commit (Blind Run)**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **60.67%** (91/150) (Wilson 95% CI: `[52.68%, 68.12%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 003 is the third externally generated synthetic stress batch evaluated blindly against the offline engine (`offline_model_version = "v4"`).
The pipeline achieved **60.67% accuracy** (91/150) under blind measurement, representing a notable **+10.67% absolute gain** over Batch 002 (50.00%) and **+28.67% absolute gain** over Batch 001 (32.00%).

Key improvements observed:
1. **Arabizi Dialect Leap**: Arabizi accuracy surged from 19.05% in Batch 002 to **61.11% (11/18)** in Batch 003 due to the principled dual-channel phonetic transliteration engine (`is_arabizi_text` + `enrich_text_with_arabizi`).
2. **Robust Regional Dialect Generalization**: Baghdadi achieved **73.91%** (34/46), Mosul achieved **66.67%** (18/27), and Basrawi achieved **60.53%** (23/38).
3. **Category Stability**: 11 out of 14 categories achieved $\ge 50.0\%$ recall, led by `general_inquiry` (81.82%), `agent_dispute` (72.73%), `unclear_or_incomplete` (72.73%), and `card_issue` (70.00%).

---

## 2. Failure Analysis by Slice

### A. Category Recall Performance

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `general_inquiry` | 11 | 9 | 81.82% | `unclear_or_incomplete` (2) |
| `agent_dispute` | 11 | 8 | 72.73% | `kyc_document_issue` (1), `card_issue` (1), `unclear_or_incomplete` (1) |
| `unclear_or_incomplete` | 11 | 8 | 72.73% | `general_inquiry` (1), `balance_or_statement_inquiry` (1), `app_bug` (1) |
| `card_issue` | 10 | 7 | 70.00% | `unclear_or_incomplete` (3) |
| `refund_status` | 10 | 7 | 70.00% | `failed_transfer` (2), `unclear_or_incomplete` (1) |
| `account_blocked` | 12 | 8 | 66.67% | `unclear_or_incomplete` (2), `failed_transfer` (1), `refund_status` (1) |
| `kyc_document_issue` | 10 | 6 | 60.00% | `card_issue` (1), `login_problem` (1), `unclear_or_incomplete` (1), `account_blocked` (1) |
| `wrong_recipient` | 10 | 6 | 60.00% | `failed_transfer` (2), `unclear_or_incomplete` (2) |
| `fraud_report` | 12 | 7 | 58.33% | `unclear_or_incomplete` (3), `card_issue` (1), `account_blocked` (1) |
| `balance_or_statement_inquiry` | 11 | 6 | 54.55% | `general_inquiry` (2), `unclear_or_incomplete` (2), `app_bug` (1) |
| `app_bug` | 10 | 5 | 50.00% | `unclear_or_incomplete` (3), `failed_transfer` (1), `login_problem` (1) |
| `bill_payment_failure` | 12 | 6 | 50.00% | `unclear_or_incomplete` (2), `balance_or_statement_inquiry` (2), `agent_dispute` (1), `card_issue` (1) |
| `failed_transfer` | 10 | 5 | 50.00% | `refund_status` (2), `general_inquiry` (1), `kyc_document_issue` (1), `unclear_or_incomplete` (1) |
| `login_problem` | 10 | 3 | 30.00% | `unclear_or_incomplete` (3), `account_blocked` (2), `fraud_report` (1), `app_bug` (1) |

### B. Tag Slice Breakdown

- **Dialect Performance**:
  - `baghdadi`: 34/46 (73.91%)
  - `mosul`: 18/27 (66.67%)
  - `basrawi`: 23/38 (60.53%)
  - `arabizi`: 11/18 (61.11%)
  - `mixed`: 5/21 (23.81%)
- **Ticket Length**:
  - `short`: 24/38 (63.16%)
  - `long`: 19/31 (61.29%)
  - `normal`: 48/81 (59.26%)
- **Attack Types**:
  - `None`: 90/142 (63.38%)
  - `prompt_injection`: 1/8 (12.50%)

---

## 3. Root Cause Investigation

Error analysis of the 59 misclassifications reveals two predominant structural factors:

1. **Bilingual Care Escalation (Rule MS-01 Intentional Guard)**:
   - 15 tickets were routed to `unclear_or_incomplete` with reasoning `English or foreign language ticket detected; routed to human care for bilingual assistance`.
   - 14 of these tickets belong to the `mixed` dialect slice and are written entirely in English. Under project policy and regression test `test_ms01_english_language_ticket_routing`, English tickets must route to bilingual human assistance. The external batch assigned synthetic domain labels (e.g. `card_issue`, `account_blocked`), but automated offline English processing is intentionally disabled in this Iraqi wallet service tier.
2. **Security Prompt Injection Safeguard**:
   - 7 of the 8 prompt injection tickets were correctly intercepted by security heuristics and assigned `unclear_or_incomplete`. In the batch gold annotations, these tickets were assigned domain labels corresponding to the scenario framing rather than security escalation.
3. **Linguistic Tail Dispersion**:
   - The remaining 37 Arabic/Arabizi errors are dispersed evenly across all categories. No single confusion pair exceeds 2 tickets (e.g. `wrong_recipient -> failed_transfer` (2), `failed_transfer -> refund_status` (2), `login_problem -> account_blocked` (2)).

---

## 4. Single Change Gate Evaluation (Protocol S5)

Protocol S5 requires:
- Pattern supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters.
- Zero literal phrases embedded from the batch.
- Must not lower grouped-CV accuracy on dev.

### Findings on S5 Qualification:
- English tickets cannot be classified offline without violating architectural requirement MS-01 and failing `tests/test_remediation_regressions.py`.
- Prompt injection tickets cannot be routed to operational queues without violating core security policy.
- No Arabic or Arabizi failure mode reached the qualification threshold ($\ge 3$ tickets across $\ge 2$ clusters); all remaining confusion pairs contain at most 2 tickets.

### Verdict:
**No remediation qualifies under the S5 change gate in Batch 003.**
Per protocol instructions, no rule change is proposed, and the offline model version remains at current stable `v4`.
