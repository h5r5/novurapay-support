# Stress Test Blind Evaluation Summary: batch_015

- **Date**: `2026-10-26T10:16:18.595353+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_015.jsonl`
- **Model**: `rules_dialect_ml_v10` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 298
- **Correct Predictions**: 258
- **Overall Accuracy**: **86.58%**
- **Wilson 95% Confidence Interval**: `[0.8224, 0.8999]` (`[82.24%, 89.99%]`)
- **Average Latency**: 5.29 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 21 | 20 | 95.24% |
| `agent_dispute` | 21 | 20 | 95.24% |
| `app_bug` | 21 | 17 | 80.95% |
| `balance_or_statement_inquiry` | 21 | 18 | 85.71% |
| `bill_payment_failure` | 22 | 21 | 95.45% |
| `card_issue` | 22 | 18 | 81.82% |
| `failed_transfer` | 22 | 19 | 86.36% |
| `fraud_report` | 22 | 21 | 95.45% |
| `general_inquiry` | 21 | 16 | 76.19% |
| `kyc_document_issue` | 21 | 20 | 95.24% |
| `login_problem` | 22 | 18 | 81.82% |
| `refund_status` | 21 | 15 | 71.43% |
| `unclear_or_incomplete` | 20 | 15 | 75.00% |
| `wrong_recipient` | 21 | 20 | 95.24% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 289 | 252 | 87.20% |
| `True` | 9 | 6 | 66.67% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 283 | 248 | 87.63% |
| `prompt_injection` | 15 | 10 | 66.67% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 39 | 38 | 97.44% |
| `basrawi` | 208 | 174 | 83.65% |
| `mixed` | 51 | 46 | 90.20% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 83 | 71 | 85.54% |
| `normal` | 155 | 133 | 85.81% |
| `short` | 60 | 54 | 90.00% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 274 | 238 | 86.86% |
| `account_blocked` | 2 | 1 | 50.00% |
| `app_bug` | 1 | 1 | 100.00% |
| `balance_or_statement_inquiry` | 2 | 2 | 100.00% |
| `bill_payment_failure` | 1 | 1 | 100.00% |
| `failed_transfer` | 1 | 1 | 100.00% |
| `fraud_report` | 6 | 4 | 66.67% |
| `kyc_document_issue` | 5 | 5 | 100.00% |
| `login_problem` | 1 | 1 | 100.00% |
| `refund_status` | 5 | 4 | 80.00% |

