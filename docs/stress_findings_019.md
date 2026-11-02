# Stress Test Findings Report: Batch 019

- **Batch ID**: batch_019
- **Source File**: `data/stress_test/novurapay_tickets_round19.jsonl`
- **Ingested Location**: `data/stress/batch_019.jsonl` (400 tickets accepted, 0 duplicate/invalid rows rejected)
- **Evaluation Date**: 2026-11-02
- **Git Commit (Blind Run)**: `6f1b696817b1f88631c6de630e23d682a3bd8e39`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **58.25%** (233/400) (Wilson 95% CI: `[53.36%, 62.98%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 019 is the nineteenth externally generated synthetic stress test batch, containing 400 tickets spanning 5 Iraqi dialects (`baghdadi`, `basrawi`, `mosul`, `mixed`, `arabizi`), 3 length categories, and adversarial prompt injections.

During ingestion under Protocol S1:
- 400 total rows were processed from `data/stress_test/novurapay_tickets_round19.jsonl`.
- 0 rows were rejected (no schema violations, no taxonomy errors, and 0 exact or near-duplicates found against dev, test, or existing batches).
- 400 valid tickets were accepted and registered into `data/stress/batch_019.jsonl` (SHA-256: `7e90e3794feb94bc871bfe68d76c98e9604f7bca6b182aba429038bde6175edd`).

On blind evaluation using the offline engine (`rules_dialect_ml_v11`), the pipeline achieved **58.25% blind accuracy** (233/400, Wilson 95% CI: `[53.36%, 62.98%]`) with zero runtime errors, zero degraded classifications, and average latency of 4.96 ms.

---

## 2. Slice Breakdown

### A. Category Recall Performance (Blind V11)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `balance_or_statement_inquiry` | 5 | 5 | 100.00% | None |
| `bill_payment_failure` | 10 | 9 | 90.00% | `kyc_document_issue` (1) |
| `fraud_report` | 35 | 28 | 80.00% | `unclear_or_incomplete` (1), `wrong_recipient` (1), `card_issue` (1), `agent_dispute` (1), `kyc_document_issue` (1) |
| `wrong_recipient` | 8 | 6 | 75.00% | `kyc_document_issue` (1), `unclear_or_incomplete` (1) |
| `card_issue` | 15 | 11 | 73.33% | `kyc_document_issue` (2), `unclear_or_incomplete` (1), `fraud_report` (1) |
| `kyc_document_issue` | 85 | 61 | 71.76% | `card_issue` (11), `unclear_or_incomplete` (4), `fraud_report` (2), `wrong_recipient` (2), `app_bug` (1) |
| `agent_dispute` | 10 | 7 | 70.00% | `login_problem` (1), `fraud_report` (1), `kyc_document_issue` (1) |
| `login_problem` | 90 | 51 | 56.67% | `app_bug` (14), `kyc_document_issue` (6), `unclear_or_incomplete` (4), `wrong_recipient` (3), `bill_payment_failure` (3) |
| `failed_transfer` | 12 | 6 | 50.00% | `kyc_document_issue` (4), `login_problem` (2) |
| `account_blocked` | 35 | 15 | 42.86% | `kyc_document_issue` (4), `login_problem` (4), `unclear_or_incomplete` (3), `refund_status` (2), `agent_dispute` (2) |
| `app_bug` | 35 | 14 | 40.00% | `kyc_document_issue` (7), `login_problem` (6), `bill_payment_failure` (2), `unclear_or_incomplete` (2), `card_issue` (2) |
| `refund_status` | 5 | 2 | 40.00% | `kyc_document_issue` (2), `bill_payment_failure` (1) |
| `unclear_or_incomplete` | 25 | 10 | 40.00% | `login_problem` (6), `app_bug` (3), `kyc_document_issue` (3), `general_inquiry` (2), `card_issue` (1) |
| `general_inquiry` | 30 | 8 | 26.67% | `login_problem` (8), `kyc_document_issue` (7), `balance_or_statement_inquiry` (3), `bill_payment_failure` (2), `card_issue` (2) |

### B. Dialect & Tag Slice Performance

- **Dialects**:
  - `mosul`: 37/58 (63.79%)
  - `arabizi`: 27/44 (61.36%)
  - `baghdadi`: 87/151 (57.62%)
  - `basrawi`: 40/71 (56.34%)
  - `mixed`: 42/76 (55.26%)
- **Attacks**:
  - `prompt_injection`: 21/32 (65.62%)
  - `None`: 212/368 (57.61%)
- **Length Buckets**:
  - `long`: 77/117 (65.81%)
  - `normal`: 126/209 (60.29%)
  - `short`: 30/74 (40.54%)
- **Ambiguity**:
  - `False`: 210/355 (59.15%)
  - `True`: 23/45 (51.11%)

---

## 3. Failure Analysis & Root Cause Patterns

Total misclassifications across the batch: 167 tickets out of 400 (41.75%).
Error analysis reveals three dominant structural clusters:

1. **Authentication Crash vs App Bug (`login_problem -> app_bug`, 14 tickets)**:
   - *Observation*: Customers describing authentication blockage where technical application crashes, freezes, screen errors, or OTP entry glitches occur during login/verification.
   - *Root Cause*: Subword and token features for generic crashes (`تطبيق`, `يغلق`, `كود`, `يعلق`) overpowered login intent in the offline ML model.
   - *Affected Clusters*: 14 distinct tickets across 5 dialects (`baghdadi`, `basrawi`, `mosul`, `mixed`, `arabizi`) and 3 length buckets (`short`, `normal`, `long`).

2. **Civil Identification Document vs Payment Card Disambiguation (`kyc_document_issue -> card_issue`, 11 tickets)**:
   - *Observation*: Tickets discussing national identity cards, unified national cards, and residence cards (`البطاقة الوطنية`, `البطاقة الموحدة`, `بطاقة السكن`) being rejected during scanning or verification.
   - *Root Cause*: The presence of the root token "بطاقة" (card) without explicit payment terms triggered ML weighting toward payment card issues rather than document verification.
   - *Affected Clusters*: 11 tickets across 3 dialects (`baghdadi`, `mosul`, `mixed`) and all 3 length categories.

3. **General Inquiries with Authentication/KYC References (`general_inquiry -> login_problem / kyc_document_issue`, 15 tickets)**:
   - *Observation*: Inquiries about requirements, support availability, or operational procedures mentioning account access or documents were pulled into operational defect categories.
   - *Root Cause*: Lack of explicit operational complaint in general questions allowed high-frequency keywords to trigger defect classification.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `data/splits/dev.jsonl`.
- **Proposed Remediation Candidate**:
  - **Target Category**: `kyc_document_issue`
  - **Proposed Rule Pattern**: High-precision deterministic guard recognizing civil identification and residence cards:
    `r"(?:البطاق(?:ة|ه)\s*(?:الوطني(?:ة|ه)|الموحد(?:ة|ه))|بطاق(?:ة|ه)\s*سكن(?:ي(?:ة|ه))?)"`
  - **Supporting Tickets**: 11 tickets (`EXT-19-055`, `EXT-19-101`, `EXT-19-179`, `EXT-19-262`, `EXT-19-324`, `EXT-19-335`, `EXT-19-358`, `EXT-19-375`, `EXT-19-382`, etc.).
  - **Cluster Diversity**: 3 distinct dialect clusters (`baghdadi`, `mosul`, `mixed`) and 3 length categories $\ge 2$.
  - **Literal Phrase Check**: Syntactic generalized regex; zero literal sentences or phrases copied.
  - **Dev CV Impact**: 0 matches in `data/splits/dev.jsonl` (zero regression risk, grouped-CV accuracy remains 100% preserved).
  - **Deployment Status**: Under the operational instruction keeping `src/classify` strictly read-only for this round, this remediation is documented as a validated proposal. No modification was made to `src/classify`, and the offline engine remains at version `v11`.
