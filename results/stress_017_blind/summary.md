# Stress Test Blind Evaluation Summary: batch_017

- **Date**: `2026-10-27T19:48:26.495405+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_017.jsonl`
- **Model**: `rules_dialect_ml_v11` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 198
- **Correct Predictions**: 174
- **Overall Accuracy**: **87.88%**
- **Wilson 95% Confidence Interval**: `[0.8260, 0.9172]` (`[82.60%, 91.72%]`)
- **Average Latency**: 4.98 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 14 | 12 | 85.71% |
| `agent_dispute` | 14 | 14 | 100.00% |
| `app_bug` | 14 | 11 | 78.57% |
| `balance_or_statement_inquiry` | 14 | 14 | 100.00% |
| `bill_payment_failure` | 14 | 14 | 100.00% |
| `card_issue` | 14 | 13 | 92.86% |
| `failed_transfer` | 14 | 12 | 85.71% |
| `fraud_report` | 14 | 14 | 100.00% |
| `general_inquiry` | 16 | 13 | 81.25% |
| `kyc_document_issue` | 14 | 13 | 92.86% |
| `login_problem` | 14 | 10 | 71.43% |
| `refund_status` | 14 | 12 | 85.71% |
| `unclear_or_incomplete` | 14 | 11 | 78.57% |
| `wrong_recipient` | 14 | 11 | 78.57% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 191 | 170 | 89.01% |
| `True` | 7 | 4 | 57.14% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 188 | 165 | 87.77% |
| `prompt_injection` | 10 | 9 | 90.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 27 | 25 | 92.59% |
| `mixed` | 34 | 31 | 91.18% |
| `western` | 137 | 118 | 86.13% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 56 | 47 | 83.93% |
| `normal` | 103 | 92 | 89.32% |
| `short` | 39 | 35 | 89.74% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 182 | 163 | 89.56% |
| `account_blocked` | 1 | 1 | 100.00% |
| `app_bug` | 1 | 1 | 100.00% |
| `balance_or_statement_inquiry` | 1 | 0 | 0.00% |
| `bill_payment_failure` | 1 | 1 | 100.00% |
| `failed_transfer` | 1 | 1 | 100.00% |
| `fraud_report` | 5 | 5 | 100.00% |
| `kyc_document_issue` | 2 | 1 | 50.00% |
| `login_problem` | 1 | 0 | 0.00% |
| `refund_status` | 3 | 1 | 33.33% |

