# Stress Test Blind Evaluation Summary: batch_016

- **Date**: `2026-10-26T10:21:47.498361+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_016.jsonl`
- **Model**: `rules_dialect_ml_v10` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 397
- **Correct Predictions**: 333
- **Overall Accuracy**: **83.88%**
- **Wilson 95% Confidence Interval**: `[0.7994, 0.8717]` (`[79.94%, 87.17%]`)
- **Average Latency**: 5.25 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 29 | 27 | 93.10% |
| `agent_dispute` | 28 | 25 | 89.29% |
| `app_bug` | 29 | 25 | 86.21% |
| `balance_or_statement_inquiry` | 28 | 21 | 75.00% |
| `bill_payment_failure` | 29 | 24 | 82.76% |
| `card_issue` | 28 | 24 | 85.71% |
| `failed_transfer` | 29 | 22 | 75.86% |
| `fraud_report` | 29 | 22 | 75.86% |
| `general_inquiry` | 28 | 21 | 75.00% |
| `kyc_document_issue` | 28 | 22 | 78.57% |
| `login_problem` | 29 | 25 | 86.21% |
| `refund_status` | 29 | 25 | 86.21% |
| `unclear_or_incomplete` | 26 | 26 | 100.00% |
| `wrong_recipient` | 28 | 24 | 85.71% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 385 | 325 | 84.42% |
| `True` | 12 | 8 | 66.67% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 378 | 323 | 85.45% |
| `prompt_injection` | 19 | 10 | 52.63% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 61 | 45 | 73.77% |
| `baghdadi` | 137 | 119 | 86.86% |
| `basrawi` | 79 | 64 | 81.01% |
| `mixed` | 68 | 61 | 89.71% |
| `mosul` | 52 | 44 | 84.62% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 104 | 83 | 79.81% |
| `normal` | 199 | 163 | 81.91% |
| `short` | 94 | 87 | 92.55% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 370 | 312 | 84.32% |
| `app_bug` | 13 | 8 | 61.54% |
| `failed_transfer` | 1 | 1 | 100.00% |
| `fraud_report` | 1 | 1 | 100.00% |
| `general_inquiry` | 2 | 2 | 100.00% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `login_problem` | 3 | 2 | 66.67% |
| `refund_status` | 6 | 6 | 100.00% |

