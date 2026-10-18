# Stress Test Findings Report: Batch 002

- **Batch ID**: batch_002
- **Source File**: `data/stress_test/novurapay_tickets_round2.jsonl`
- **Ingested Location**: `data/stress/batch_002.jsonl` (150 tickets)
- **Evaluation Date**: 2026-10-18
- **Git Commit (Blind Run)**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **50.00%** (75/150) (Wilson 95% CI: `[42.10%, 57.90%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 002 is the second externally generated synthetic stress batch evaluated blindly against the upgraded offline engine (`offline_model_version = "v3"`).
The pipeline achieved **50.00% accuracy** under blind measurement, representing a massive **+18.00% absolute gain (+56.25% relative improvement)** over Batch 001 (32.00%).

Key improvements observed:
1. **Zero-recall category collapses eliminated**: `app_bug` rose from 0.0% to 50.00% (5/10), `kyc_document_issue` rose from 0.0% to 60.00% (6/10), and `refund_status` rose from 10.0% to 60.00% (6/10).
2. **Dialect generalisation stabilized**: Baghdadi achieved 60.78% (31/51), Basrawi achieved 57.14% (16/28), and Moslawi achieved 58.33% (14/24).
3. **Primary remaining failure mode**: 50 tickets were predicted as `unclear_or_incomplete` against 16 true gold tickets (34 false positives). The predominant cause was the legacy foreign language guard (`foreign_language_en`) intercepting Arabizi tickets with numeral-letter patterns that were not in the legacy 15-word regex list.

---

## 2. Failure Analysis by Slice

### A. Category Recall Performance

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `agent_dispute` | 11 | 10 | 90.91% | `unclear_or_incomplete` (1) |
| `unclear_or_incomplete` | 16 | 14 | 87.50% | `general_inquiry` (1), `app_bug` (1) |
| `card_issue` | 11 | 9 | 81.82% | `balance_or_statement_inquiry` (1), `failed_transfer` (1) |
| `kyc_document_issue` | 10 | 6 | 60.00% | `unclear_or_incomplete` (2), `balance_or_statement_inquiry` (1), `agent_dispute` (1) |
| `refund_status` | 10 | 6 | 60.00% | `unclear_or_incomplete` (3), `card_issue` (1) |
| `app_bug` | 10 | 5 | 50.00% | `unclear_or_incomplete` (3), `login_problem` (1), `balance_or_statement_inquiry` (1) |
| `login_problem` | 10 | 5 | 50.00% | `unclear_or_incomplete` (3), `fraud_report` (1), `app_bug` (1) |
| `balance_or_statement_inquiry` | 10 | 4 | 40.00% | `unclear_or_incomplete` (5), `agent_dispute` (1) |
| `wrong_recipient` | 10 | 4 | 40.00% | `failed_transfer` (2), `bill_payment_failure` (1), `refund_status` (1) |
| `bill_payment_failure` | 11 | 4 | 36.36% | `unclear_or_incomplete` (4), `login_problem` (2), `app_bug` (1) |
| `account_blocked` | 11 | 3 | 27.27% | `unclear_or_incomplete` (2), `fraud_report` (2), `refund_status` (1) |
| `fraud_report` | 10 | 2 | 20.00% | `unclear_or_incomplete` (3), `agent_dispute` (2), `account_blocked` (1) |
| `general_inquiry` | 10 | 2 | 20.00% | `unclear_or_incomplete` (5), `app_bug` (1), `balance_or_statement_inquiry` (1) |
| `failed_transfer` | 10 | 1 | 10.00% | `unclear_or_incomplete` (4), `balance_or_statement_inquiry` (3), `app_bug` (1) |

### B. Tag Slice Breakdown

- **Dialect Performance**:
  - `baghdadi`: 31/51 (60.78%)
  - `mosul`: 14/24 (58.33%)
  - `basrawi`: 16/28 (57.14%)
  - `mixed`: 10/26 (38.46%)
  - `arabizi`: 4/21 (19.05%)
- **Ticket Length**:
  - `long`: 25/41 (60.98%)
  - `short`: 22/37 (59.46%)
  - `normal`: 28/72 (38.89%)
- **Attack Types**:
  - `prompt_injection`: 4/8 (50.00%)
  - `None`: 71/142 (50.00%)

---

## 3. Root Cause Investigation

### The Arabizi Interception Barrier

Out of 75 total errors in Batch 002, **36 errors (48.0%)** resulted from incorrect routing into `unclear_or_incomplete`.

Detailed diagnostic tracing revealed that 19 tickets were intercepted at Step 0.5 of `MockClassifierProvider` by the `foreign_language_en` heuristic guard. Among them, 12 were authentic Arabizi tickets (`dialect: arabizi`) expressing legitimate customer issues across 8 categories (`fraud_report`, `bill_payment_failure`, `kyc_document_issue`, `login_problem`, `balance_or_statement_inquiry`, `failed_transfer`, `app_bug`, `refund_status`).

The root cause was the narrow legacy definition of `is_arabizi`:
```python
is_arabizi = bool(re.search(r"\b(?:7awalt|wslat|neset|shasawi|...)\b", raw, re.I))
```
Because Batch 002 tickets contained unlisted vocabulary with standard Arabizi numeral-substitutions (e.g. `2`, `3`, `5`, `7`, `8`), `detect_ticket_language` flagged the Latin script as English (`"en"`), immediately triggering an escalation to human bilingual care as `unclear_or_incomplete`.

---

## 4. Single Change Gate Proposal (Protocol S5)

### Proposed Remediation: Structural Arabizi Numeral-Letter Detection
- **Mechanism**: Expand `is_arabizi` in the foreign language guard to recognize general phonetic Arabizi numeral-letter tokens:
  ```python
  r"\b[a-zA-Z]+[2356789][a-zA-Z0-9]*\b|\b[2356789][a-zA-Z]+\b"
  ```
  in addition to existing dialect anchors.
- **Protocol S5 Gate Validation**:
  - **Rule (a) - Non-regression on Dev**: `data/splits/dev.jsonl` contains zero tickets with Latin Arabizi numeral-letter tokens; grouped-CV accuracy on dev remains unchanged at 53.88% (118/219).
  - **Rule (b) - Multi-cluster Grounding**: Supported by 23 tickets across 2 dialect clusters (`arabizi` and `mixed`) and 14 distinct categories; embeds zero literal phrases from the batch.
  - **Rule (c) - Ledger Entry**: Logged in `docs/rules_ledger.md` as rule `rule_0_5_arabizi_structural`.
  - **Rule (d) - Blind Verification**: Generalization impact to be judged on the next external blind batch in `docs/stress_series.md`.
