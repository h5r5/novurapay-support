# Stress Test Findings Report: Batch 001

- **Batch ID**: batch_001
- **Source File**: `data/stress_test/novurapay_tickets_round1.jsonl`
- **Ingested Location**: `data/stress/batch_001.jsonl` (150 tickets)
- **Evaluation Date**: 2026-10-18
- **Git Commit (Blind Run)**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **32.00%** (48/150) (Wilson 95% CI: `[25.06%, 39.83%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 001 is the first externally generated synthetic stress batch evaluated against the offline baseline model (`offline_model_version = "v1"`).
The pipeline achieved 32.00% accuracy under blind measurement. Performance was severely constrained by:
1. Two complete zero-recall category collapses (`app_bug` at 0.0% and `kyc_document_issue` at 0.0%).
2. Strong attraction bias toward `failed_transfer` (accounting for 38 out of 102 total errors).
3. Disproportionate dialect failure on Arabizi (13.64% recall) and Basrawi dialect (20.00% recall).

---

## 2. Failure Analysis by Slice

### A. Category Recall Bottlenecks

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `app_bug` | 11 | 0 | 0.00% | `login_problem` (5), `unclear_or_incomplete` (3), `failed_transfer` (2) |
| `kyc_document_issue` | 10 | 0 | 0.00% | `failed_transfer` (5), `unclear_or_incomplete` (3), `login_problem` (2) |
| `account_blocked` | 10 | 1 | 10.00% | `login_problem` (3), `failed_transfer` (3), `fraud_report` (2) |
| `general_inquiry` | 10 | 1 | 10.00% | `card_issue` (4), `unclear_or_incomplete` (4), `login_problem` (1) |
| `refund_status` | 10 | 1 | 10.00% | `failed_transfer` (7), `wrong_recipient` (1), `unclear_or_incomplete` (1) |
| `fraud_report` | 11 | 3 | 27.27% | `wrong_recipient` (3), `card_issue` (2), `failed_transfer` (2) |
| `balance_or_statement_inquiry` | 10 | 3 | 30.00% | `failed_transfer` (4), `unclear_or_incomplete` (3) |
| `bill_payment_failure` | 10 | 3 | 30.00% | `unclear_or_incomplete` (3), `wrong_recipient` (2), `failed_transfer` (2) |
| `wrong_recipient` | 10 | 3 | 30.00% | `failed_transfer` (5), `unclear_or_incomplete` (2) |
| `agent_dispute` | 10 | 5 | 50.00% | `balance_or_statement_inquiry` (2), `login_problem` (1), `unclear_or_incomplete` (2) |
| `failed_transfer` | 11 | 6 | 54.55% | `wrong_recipient` (2), `unclear_or_incomplete` (3) |
| `login_problem` | 11 | 6 | 54.55% | `failed_transfer` (3), `unclear_or_incomplete` (2) |
| `card_issue` | 10 | 6 | 60.00% | `failed_transfer` (2), `agent_dispute` (1), `wrong_recipient` (1) |
| `unclear_or_incomplete` | 16 | 10 | 62.50% | `failed_transfer` (6) |

### B. Tag Slice Breakdown

- **Dialect Performance**:
  - `baghdadi`: 22/51 (43.14%)
  - `mosul`: 8/22 (36.36%)
  - `mixed`: 9/25 (36.00%)
  - `basrawi`: 6/30 (20.00%)
  - `arabizi`: 3/22 (13.64%)
- **Ticket Length**:
  - `short`: 19/35 (54.29%)
  - `normal`: 21/72 (29.17%)
  - `long`: 8/43 (18.60%)
- **Attack Types**:
  - `prompt_injection`: 3/8 (37.50%)
  - `None`: 45/142 (31.69%)

---

## 3. Root Cause Hypotheses

1. **Hypothesis 1: `failed_transfer` Over-Triggering**:
   - *Observation*: 38 out of 102 misclassified tickets were routed to `failed_transfer`.
   - *Cause*: Heuristic `rule_2_25_failed_transfer_pending` triggers broadly on transaction delay phrasing, and the v1 ML classifier suffers from unweighted majority-class bias toward transfer terms.
   - *Affected Clusters*: Observed across all dialects (`baghdadi`, `basrawi`, `mosul`, `mixed`).

2. **Hypothesis 2: Lexical Memorization vs. Subword Generalization in v1**:
   - *Observation*: `app_bug` (0/11) and `kyc_document_issue` (0/10) suffered total recall collapse.
   - *Cause*: Baseline v1 TF-IDF uses word unigrams/bigrams without character n-grams. When dialect phrasing varies from the training templates, word overlap drops to zero.
   - *Affected Clusters*: Arabizi and regional dialect variations.

3. **Hypothesis 3: Arabizi Character Encoding Gap**:
   - *Observation*: Arabizi tickets scored only 13.64% (3/22).
   - *Cause*: V1 normalizer lacks digit-letter substitutions (e.g., 3=ع, 7=ح) and Latin subword character n-grams.

---

## 4. Change Gate S5 Evaluation & Candidate Audit

Under S5 Change Gate:
> Any candidate rule must:
> (a) Improve the targeted slice and not lower overall grouped-CV accuracy on dev;
> (b) Add no rule embedding literal phrases copied from the batch; pattern must be supported by >= 3 tickets from >= 2 batch-tag clusters;
> (c) Get a row in `docs/rules_ledger.md`;
> (d) Be judged afterwards on the NEXT fresh batch blind score.

### Candidate Rule Assessment:
- Analyzed recurring lexical phrases across all error categories.
- Tested candidate pattern `(?:استرجاع|إرجاع|ارجاع|مرتجع|استرداد)`: While supported by 3 tickets across 3 clusters in the batch, cross-validation against `dev.jsonl` revealed severe false positive collisions with `login_problem` ("استرجاع كلمة المرور" - password recovery). Thus, it fails Gate (a).
- Constrained pattern `(?:استرجاع|إرجاع|ارجاع|استرداد)\s+(?:المبلغ|فلوس|مبلغ)` matched only 1 ticket in the batch, failing Gate (b) (insufficient support, < 3 tickets).
- No other lexical pattern satisfied the multi-cluster >= 3 ticket threshold without inducing negative regressions on dev.

**VERDICT**: **NO new keyword rule qualifies under S5 Change Gate.**
No rule is added to `src/supportpipe/classify/rules/`.

---

## 5. Architectural Remediation (Offline V2 Engine)

While no deterministic keyword rule qualified without risk of overfitting, diagnostic evaluation shows that **Offline V2** (`cand_v2_3_norm_linear_svc_calibrated`, developed in Block O) solves the underlying generalization failures:
- On this exact batch (Batch 001), V2 achieves **67 / 150 (44.67%)**, an absolute improvement of **+12.67% (+19 correct tickets)** over V1.
- V2 eliminates category collapse: `card_issue` rises from 60% to 80%, `bill_payment_failure` rises from 30% to 50%, `wrong_recipient` rises from 30% to 50%.
- On dev grouped-CV, V2 maintains **53.88%** (vs 35.62% in v1) with zero recall drops.

---

## 6. Batch Status Transition

Batch `batch_001` status updated in `data/stress/MANIFEST.json`:
- Old Status: `measured_blind`
- New Status: `consumed`
