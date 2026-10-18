# Stress Test Blind Evaluation Summary: batch_004

- **Date**: `2026-10-18T19:47:24.640632+00:00`
- **Git HEAD**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Batch File**: `batch_004.jsonl`
- **Model**: `rules_dialect_ml_v5` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 200
- **Correct Predictions**: 151
- **Overall Accuracy**: **75.50%**
- **Wilson 95% Confidence Interval**: `[0.6910, 0.8094]` (`[69.10%, 80.94%]`)
- **Average Latency**: 4.45 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 16 | 13 | 81.25% |
| `agent_dispute` | 14 | 12 | 85.71% |
| `app_bug` | 13 | 11 | 84.62% |
| `balance_or_statement_inquiry` | 15 | 11 | 73.33% |
| `bill_payment_failure` | 16 | 10 | 62.50% |
| `card_issue` | 14 | 13 | 92.86% |
| `failed_transfer` | 14 | 10 | 71.43% |
| `fraud_report` | 16 | 8 | 50.00% |
| `general_inquiry` | 15 | 9 | 60.00% |
| `kyc_document_issue` | 13 | 11 | 84.62% |
| `login_problem` | 13 | 8 | 61.54% |
| `refund_status` | 13 | 12 | 92.31% |
| `unclear_or_incomplete` | 14 | 13 | 92.86% |
| `wrong_recipient` | 14 | 10 | 71.43% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 193 | 147 | 76.17% |
| `True` | 7 | 4 | 57.14% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 193 | 150 | 77.72% |
| `prompt_injection` | 7 | 1 | 14.29% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 28 | 17 | 60.71% |
| `baghdadi` | 46 | 42 | 91.30% |
| `basrawi` | 79 | 59 | 74.68% |
| `mixed` | 19 | 7 | 36.84% |
| `mosul` | 28 | 26 | 92.86% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 28 | 20 | 71.43% |
| `normal` | 112 | 83 | 74.11% |
| `short` | 60 | 48 | 80.00% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 181 | 141 | 77.90% |
| `account_blocked` | 2 | 1 | 50.00% |
| `agent_dispute` | 2 | 0 | 0.00% |
| `app_bug` | 5 | 3 | 60.00% |
| `failed_transfer` | 3 | 1 | 33.33% |
| `fraud_report` | 1 | 1 | 100.00% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `login_problem` | 2 | 1 | 50.00% |
| `refund_status` | 3 | 2 | 66.67% |

