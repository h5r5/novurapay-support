# Stress Test Blind Evaluation Summary: batch_002

- **Date**: `2026-10-18T18:18:34.020009+00:00`
- **Git HEAD**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Batch File**: `batch_002.jsonl`
- **Model**: `rules_dialect_ml_v3` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 150
- **Correct Predictions**: 75
- **Overall Accuracy**: **50.00%**
- **Wilson 95% Confidence Interval**: `[0.4210, 0.5790]` (`[42.10%, 57.90%]`)
- **Average Latency**: 3.78 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 11 | 3 | 27.27% |
| `agent_dispute` | 11 | 10 | 90.91% |
| `app_bug` | 10 | 5 | 50.00% |
| `balance_or_statement_inquiry` | 10 | 4 | 40.00% |
| `bill_payment_failure` | 11 | 4 | 36.36% |
| `card_issue` | 11 | 9 | 81.82% |
| `failed_transfer` | 10 | 1 | 10.00% |
| `fraud_report` | 10 | 2 | 20.00% |
| `general_inquiry` | 10 | 2 | 20.00% |
| `kyc_document_issue` | 10 | 6 | 60.00% |
| `login_problem` | 10 | 5 | 50.00% |
| `refund_status` | 10 | 6 | 60.00% |
| `unclear_or_incomplete` | 16 | 14 | 87.50% |
| `wrong_recipient` | 10 | 4 | 40.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 145 | 73 | 50.34% |
| `True` | 5 | 2 | 40.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 142 | 71 | 50.00% |
| `prompt_injection` | 8 | 4 | 50.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 21 | 4 | 19.05% |
| `baghdadi` | 51 | 31 | 60.78% |
| `basrawi` | 28 | 16 | 57.14% |
| `mixed` | 26 | 10 | 38.46% |
| `mosul` | 24 | 14 | 58.33% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 41 | 25 | 60.98% |
| `normal` | 72 | 28 | 38.89% |
| `short` | 37 | 22 | 59.46% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 138 | 70 | 50.72% |
| `account_blocked` | 1 | 1 | 100.00% |
| `agent_dispute` | 1 | 0 | 0.00% |
| `app_bug` | 1 | 1 | 100.00% |
| `balance_or_statement_inquiry` | 2 | 1 | 50.00% |
| `failed_transfer` | 1 | 0 | 0.00% |
| `fraud_report` | 1 | 0 | 0.00% |
| `general_inquiry` | 1 | 1 | 100.00% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `refund_status` | 3 | 0 | 0.00% |

