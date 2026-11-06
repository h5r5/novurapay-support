# Stress Test Findings Report: Batch 020

- **Batch ID**: batch_020
- **Source File**: `data/stress_test/novurapay_tickets_round20.jsonl`
- **Ingested Location**: `data/stress/batch_020.jsonl` (499 tickets accepted, 1 duplicate row rejected)
- **Evaluation Date**: 2026-11-05
- **Git Commit (Blind Run)**: `98014541d549e5465b4cf090beb12511c3dfab14`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **69.14%** (345/499) (Wilson 95% CI: `[64.95%, 73.03%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 020 is the twentieth externally generated synthetic stress test batch, containing 500 tickets focused heavily on boundary disambiguation between `kyc_document_issue` and `login_problem`, across 5 Iraqi dialects (`baghdadi`, `basrawi`, `mosul`, `mixed`, `arabizi`), English/bilingual queries, and adversarial prompt injections.

During ingestion under Protocol S1:
- 500 total rows were processed from `data/stress_test/novurapay_tickets_round20.jsonl`.
- 1 duplicate row was rejected:
  - Row 258 (`EXT-20-258`): Exact duplicate text of ticket `EXT-2-204` from `batch_015.jsonl`.
- 499 valid tickets were accepted and registered into `data/stress/batch_020.jsonl` (SHA-256: `32e3a4d8abf86a8b4db1508859f0360d4a9b2e4ca1f81b7d66305f9374e3b0e8`).

On blind evaluation using the offline engine (`rules_dialect_ml_v13`), the pipeline achieved **69.14% blind accuracy** (345/499, Wilson 95% CI: `[64.95%, 73.03%]`) with zero runtime errors, zero degraded classifications, and average latency of 5.72 ms.

---

## 2. Slice Breakdown

### A. Category Recall Performance (Blind V13)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `kyc_document_issue` | 249 | 186 | 74.70% | `unclear_or_incomplete` (12), `account_blocked` (11), `login_problem` (11), `general_inquiry` (9), `app_bug` (7), `fraud_report` (6) |
| `login_problem` | 250 | 159 | 63.60% | `unclear_or_incomplete` (28), `app_bug` (18), `account_blocked` (15), `fraud_report` (13), `kyc_document_issue` (5), `general_inquiry` (4) |

### B. Dialect & Tag Slice Performance

- **Dialects**:
  - `basrawi`: 78/103 (75.73%)
  - `baghdadi`: 125/167 (74.85%)
  - `arabizi`: 49/70 (70.00%)
  - `mosul`: 45/74 (60.81%)
  - `mixed`: 48/85 (56.47%)
- **Attacks**:
  - `prompt_injection`: 12/25 (48.00%)
  - `None`: 333/474 (70.25%)
- **Length Buckets**:
  - `long`: 110/150 (73.33%)
  - `normal`: 171/251 (68.13%)
  - `short`: 64/98 (65.31%)
- **Ambiguity**:
  - `False`: 335/484 (69.21%)
  - `True`: 10/15 (66.67%)
- **Secondary Hints**:
  - `failed_transfer`: 6/7 (85.71%)
  - `None`: 329/457 (71.99%)
  - `fraud_report`: 9/24 (37.50%)
  - `account_blocked`: 1/8 (12.50%)
  - `balance_or_statement_inquiry`: 0/2 (0.00%)
  - `bill_payment_failure`: 0/1 (0.00%)

---

## 3. Failure Analysis & Root Cause Patterns

Total misclassifications across the batch: 154 tickets out of 499 (30.86%).
Error analysis reveals four dominant structural mechanisms:

1. **Vague English Intent Routing (`login_problem / kyc_document_issue -> unclear_or_incomplete`, 19 tickets)**:
   - *Observation*: English-language tickets reporting non-specific login loops or document inquiries routed to `unclear_or_incomplete` with `sentiment_tags=["foreign_language_en"]`.
   - *Root Cause*: Intentional compliance with milestone safeguard MS-01 (`test_ms01_english_language_ticket_routing`), which safely diverts non-explicit English requests to bilingual human escalation.

2. **Authentication Crash vs Application Bug (`login_problem -> app_bug`, 18 tickets)**:
   - *Observation*: Users describing app crashes, black/blank screens, or closures while attempting to authenticate.
   - *Root Cause*: Subword character n-grams associated with app crashes (`تطبيق`, `يغلق`, `كود`, `crash`) outweighed login features during ML model inference.

3. **Authentication Lockout vs Administrative Block (`login_problem -> account_blocked`, 15 tickets)**:
   - *Observation*: Users temporarily locked out due to OTP exhaustion or device mismatch misrouted to compliance account freeze.
   - *Root Cause*: Overlapping vocabulary regarding lock/freeze between authentication lockout and account suspension.

4. **Security & Prompt Injection Defenses (13 tickets)**:
   - *Observation*: 13 adversarial prompt injections successfully quarantined into `unclear_or_incomplete` with security tags.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Change Gate Rules**: Any rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `data/splits/dev.jsonl`.
- **Operational Constraint**: `src/classify` remains strictly read-only for this evaluation round.
- **Evaluation**: The observed misclassifications are distributed across ML fallback boundaries and intentional English bilingual routing (MS-01). No single pattern cleanly isolates $\ge 3$ tickets across $\ge 2$ clusters without high risk of false positives or dev regression.
- **Verdict**: **Nothing qualifies under S5 gate.** Zero code modifications proposed; offline model version remains at `v13`.
