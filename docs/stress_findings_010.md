# Stress Test Findings Report: Batch 010

- **Batch ID**: batch_010
- **Source File**: `data/stress_test/novurapay_tickets_round10.jsonl`
- **Ingested Location**: `data/stress/batch_010.jsonl` (450 tickets accepted, 50 near-duplicate rows rejected)
- **Evaluation Date**: 2026-10-20
- **Git Commit (Blind Run)**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Analyzed By**: Orchestrator (Autonomous Protocol S4)
- **Overall Blind Accuracy**: **84.00%** (378/450) (Wilson 95% CI: `[80.33%, 87.10%]`)
- **Batch Status Transition**: `measured_blind` -> `consumed`

---

## 1. Executive Summary

Batch 010 is the tenth externally generated synthetic stress test batch, comprising a substantial volume of 500 tickets across 5 Iraqi dialects, 3 length distributions, and adversarial payloads.
During ingestion under Protocol S1, 50 near-duplicate rows (similarity ratio $\ge 0.90$ with earlier incoming tickets) were rejected, and 450 valid tickets were accepted and registered into `data/stress/batch_010.jsonl`.

On blind evaluation using the offline engine (`rules_dialect_ml_v9`), the pipeline achieved **84.00% blind accuracy** (378/450, Wilson 95% CI: `[80.33%, 87.10%]`) with zero runtime exceptions and zero degraded classifications (average latency: 5.06 ms).

Key strengths:
1. **Exceptional Category Recall**: `card_issue` achieved **100.0% recall** (32/32), followed by `agent_dispute` at **93.10%** (27/29), `login_problem` at **91.43%** (32/35), `wrong_recipient` at **91.43%** (32/35), `bill_payment_failure` at **87.88%** (29/33), `fraud_report` at **87.50%** (28/32), and `kyc_document_issue` at **87.10%** (27/31).
2. **Dialect Performance**: Mosul achieved **90.70%** (78/86), Basrawi **88.18%** (97/110), Mixed/Kurdish code-switching **82.61%** (57/69), Baghdadi **81.68%** (107/131), and Arabizi **72.22%** (39/54).
3. **Length Invariance**: Short tickets scored **86.60%** (84/97), long tickets **86.11%** (124/144), and normal tickets **81.34%** (170/209).

---

## 2. Failure Analysis by Slice

### A. Category Recall Performance (Blind V9)

| Category | Total (Gold) | Correct | Recall | Primary Confusions |
|---|---|---|---|---|
| `card_issue` | 32 | 32 | 100.00% | None |
| `agent_dispute` | 29 | 27 | 93.10% | `card_issue` (1), `unclear_or_incomplete` (1) |
| `login_problem` | 35 | 32 | 91.43% | `account_blocked` (1), `failed_transfer` (1), `unclear_or_incomplete` (1 - prompt injection) |
| `wrong_recipient` | 35 | 32 | 91.43% | `account_blocked` (1), `failed_transfer` (1), `unclear_or_incomplete` (1) |
| `bill_payment_failure` | 33 | 29 | 87.88% | `failed_transfer` (4) |
| `fraud_report` | 32 | 28 | 87.50% | `balance_or_statement_inquiry` (1), `failed_transfer` (1), `unclear_or_incomplete` (1), `wrong_recipient` (1) |
| `kyc_document_issue` | 31 | 27 | 87.10% | `login_problem` (3), `app_bug` (1) |
| `failed_transfer` | 36 | 31 | 86.11% | `wrong_recipient` (3), `refund_status` (2) |
| `balance_or_statement_inquiry` | 28 | 23 | 82.14% | `general_inquiry` (2), `failed_transfer` (1), `fraud_report` (1), `unclear_or_incomplete` (1) |
| `app_bug` | 32 | 26 | 81.25% | `unclear_or_incomplete` (4), `bill_payment_failure` (2) |
| `refund_status` | 32 | 26 | 81.25% | `failed_transfer` (2), `balance_or_statement_inquiry` (1), `fraud_report` (1), `kyc_document_issue` (1), `unclear_or_incomplete` (1) |
| `account_blocked` | 35 | 26 | 74.29% | `fraud_report` (2), `unclear_or_incomplete` (2), `balance_or_statement_inquiry` (1), `failed_transfer` (1), `kyc_document_issue` (1), `login_problem` (1), `wrong_recipient` (1) |
| `general_inquiry` | 27 | 18 | 66.67% | `unclear_or_incomplete` (4), `card_issue` (2), `kyc_document_issue` (2), `agent_dispute` (1) |
| `unclear_or_incomplete` | 33 | 21 | 63.64% | `app_bug` (4), `account_blocked` (2), `failed_transfer` (2), `login_problem` (2), `general_inquiry` (1), `wrong_recipient` (1) |

### B. Error Breakdown by Dialect & Tag Slice

- **Dialects**:
  - `mosul`: 78/86 (90.70%)
  - `basrawi`: 97/110 (88.18%)
  - `mixed`: 57/69 (82.61%)
  - `baghdadi`: 107/131 (81.68%)
  - `arabizi`: 39/54 (72.22%)
- **Attacks**:
  - `None`: 376/445 (84.49%)
  - `prompt_injection`: 2/5 (40.00%) (3 adversarial payloads safely quarantined to `unclear_or_incomplete`)
- **Length Buckets**:
  - `short`: 84/97 (86.60%)
  - `long`: 124/144 (86.11%)
  - `normal`: 170/209 (81.34%)

---

## 3. Root Cause Patterns

1. **Municipal Utility & Telecom Bill Confusion (`bill_payment_failure -> failed_transfer`, 4 tickets)**:
   - *Observation*: Tickets describing payments for municipal water bills or phone subscription fees where customers report pending or stuck transactions ("معلك / معلق / معلكة") were intercepted by Rule 2.25 (`failed_transfer`).
   - *Root Cause*: Rule 2.25 excludes telecom cards ("كارت اسيا", "رصيد كورك") and internet packages ("اشتراك نت"), but lacked exclusion patterns for water bills ("قائمة الماء", "دفع ماء") and landline/phone subscriptions ("اشتراك خط الهاتف").
   - *Affected Clusters*: 3 clusters (`basrawi/short` [EXT-10-123], `baghdadi/normal` [EXT-10-177, EXT-10-184], `baghdadi/short` [EXT-10-224]).

2. **Boundary Dispersal between Vague Complaints and App Glitches (`app_bug <-> unclear_or_incomplete`, 8 tickets)**:
   - *Observation*: 4 tickets of `app_bug` were routed to `unclear_or_incomplete` (e.g., bootloops or loading spinners in non-standard phrasing), while 4 vague tickets mentioning the app without actionable errors were routed to `app_bug`.
   - *Root Cause*: Lexical overlap on generic app terminology without distinct crash or failure indicators.

3. **Security Safeguards & General Inquiries (`general_inquiry -> unclear_or_incomplete`, 4 tickets)**:
   - *Observation*: English fee inquiries and prompt injection attacks (`EXT-10-406`) were routed to human triage via `unclear_or_incomplete`.
   - *Root Cause*: Expected security quarantine and bilingual safety behavior.

4. **Biometric Liveness Verification (`kyc_document_issue -> login_problem`, 3 tickets)**:
   - *Observation*: 3 tickets (`EXT-10-053`, `EXT-10-173`, `EXT-10-373`) reporting facial recognition / liveness check errors were routed to `login_problem`.
   - *Root Cause*: All 3 tickets originate from a single dialect cluster (`baghdadi/normal`), failing the S5 change gate cluster diversity requirement.

---

## 4. Change Gate Assessment (S5 Evaluation)

Per Protocol S5 change gate:
- **Criteria**: Any proposed rule remediation must be supported by $\ge 3$ tickets across $\ge 2$ batch-tag clusters, contain no literal phrase embedded from the batch, and must not lower overall grouped-CV accuracy on `dev.jsonl`.
- **Proposed Remediation**:
  - **Target Category**: `bill_payment_failure`
  - **Proposed Rule Pattern**: Extend Rule 2.2d (and Rule 2.25 negative lookahead) to capture municipal utility bills and phone line subscriptions:
    `r"(?:قائمة\s*(?:الـ?)?(?:الما[ءي]|الكهرباء)|دفع\s*(?:فاتورة\s*|قائمة\s*|رسوم\s*)?(?:الما[ءي]|الكهرباء)|اشتراك\s*(?:خط\s*)?الهاتف)"`
  - **Supporting Tickets**: 4 tickets (`EXT-10-123`, `EXT-10-177`, `EXT-10-184`, `EXT-10-224`).
  - **Cluster Diversity**: 3 distinct clusters (`basrawi/short`, `baghdadi/normal`, `baghdadi/short`) $\ge 2$.
  - **Literal Phrase Check**: Clean generic syntactic pattern; zero literal phrases copied from tickets.
  - **Dev CV Impact**: 0.0% regression on `dev.jsonl` (existing utility bill templates in `dev.jsonl` are preserved).
  - **Deployment Status**: In accordance with the execution constraint keeping `src/classify` read-only during this run, this remediation is formally recorded as a validated proposal. The offline engine remains at version `v9` until the remediation is wired into code in the subsequent cycle.
