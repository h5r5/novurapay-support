# Stress Test Blind Evaluation Summary: batch_014

- **Date**: `2026-10-26T10:12:29.930959+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_014.jsonl`
- **Model**: `rules_dialect_ml_v10` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 147
- **Correct Predictions**: 122
- **Overall Accuracy**: **82.99%**
- **Wilson 95% Confidence Interval**: `[0.7610, 0.8821]` (`[76.10%, 88.21%]`)
- **Average Latency**: 5.06 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 10 | 10 | 100.00% |
| `agent_dispute` | 10 | 9 | 90.00% |
| `app_bug` | 10 | 8 | 80.00% |
| `balance_or_statement_inquiry` | 10 | 9 | 90.00% |
| `bill_payment_failure` | 11 | 9 | 81.82% |
| `card_issue` | 11 | 7 | 63.64% |
| `failed_transfer` | 11 | 10 | 90.91% |
| `fraud_report` | 11 | 8 | 72.73% |
| `general_inquiry` | 11 | 8 | 72.73% |
| `kyc_document_issue` | 10 | 8 | 80.00% |
| `login_problem` | 11 | 7 | 63.64% |
| `refund_status` | 10 | 9 | 90.00% |
| `unclear_or_incomplete` | 11 | 10 | 90.91% |
| `wrong_recipient` | 10 | 10 | 100.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 142 | 117 | 82.39% |
| `True` | 5 | 5 | 100.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 140 | 118 | 84.29% |
| `prompt_injection` | 7 | 4 | 57.14% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 23 | 18 | 78.26% |
| `baghdadi` | 48 | 40 | 83.33% |
| `basrawi` | 28 | 24 | 85.71% |
| `mixed` | 25 | 21 | 84.00% |
| `mosul` | 23 | 19 | 82.61% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 46 | 37 | 80.43% |
| `normal` | 72 | 63 | 87.50% |
| `short` | 29 | 22 | 75.86% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 135 | 112 | 82.96% |
| `account_blocked` | 1 | 1 | 100.00% |
| `app_bug` | 1 | 1 | 100.00% |
| `balance_or_statement_inquiry` | 1 | 1 | 100.00% |
| `bill_payment_failure` | 1 | 1 | 100.00% |
| `failed_transfer` | 1 | 0 | 0.00% |
| `fraud_report` | 4 | 3 | 75.00% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `login_problem` | 1 | 1 | 100.00% |
| `refund_status` | 1 | 1 | 100.00% |

