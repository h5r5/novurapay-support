# Stress Test Blind Evaluation Summary: batch_003

- **Date**: `2026-10-18T18:57:14.088843+00:00`
- **Git HEAD**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Batch File**: `batch_003.jsonl`
- **Model**: `rules_dialect_ml_v4` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 150
- **Correct Predictions**: 91
- **Overall Accuracy**: **60.67%**
- **Wilson 95% Confidence Interval**: `[0.5268, 0.6812]` (`[52.68%, 68.12%]`)
- **Average Latency**: 3.53 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 12 | 8 | 66.67% |
| `agent_dispute` | 11 | 8 | 72.73% |
| `app_bug` | 10 | 5 | 50.00% |
| `balance_or_statement_inquiry` | 11 | 6 | 54.55% |
| `bill_payment_failure` | 12 | 6 | 50.00% |
| `card_issue` | 10 | 7 | 70.00% |
| `failed_transfer` | 10 | 5 | 50.00% |
| `fraud_report` | 12 | 7 | 58.33% |
| `general_inquiry` | 11 | 9 | 81.82% |
| `kyc_document_issue` | 10 | 6 | 60.00% |
| `login_problem` | 10 | 3 | 30.00% |
| `refund_status` | 10 | 7 | 70.00% |
| `unclear_or_incomplete` | 11 | 8 | 72.73% |
| `wrong_recipient` | 10 | 6 | 60.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 145 | 89 | 61.38% |
| `True` | 5 | 2 | 40.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 142 | 90 | 63.38% |
| `prompt_injection` | 8 | 1 | 12.50% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 18 | 11 | 61.11% |
| `baghdadi` | 46 | 34 | 73.91% |
| `basrawi` | 38 | 23 | 60.53% |
| `mixed` | 21 | 5 | 23.81% |
| `mosul` | 27 | 18 | 66.67% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 31 | 19 | 61.29% |
| `normal` | 81 | 48 | 59.26% |
| `short` | 38 | 24 | 63.16% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 133 | 84 | 63.16% |
| `agent_dispute` | 2 | 1 | 50.00% |
| `app_bug` | 3 | 0 | 0.00% |
| `card_issue` | 2 | 0 | 0.00% |
| `failed_transfer` | 3 | 1 | 33.33% |
| `fraud_report` | 2 | 2 | 100.00% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `login_problem` | 1 | 1 | 100.00% |
| `refund_status` | 2 | 1 | 50.00% |
| `wrong_recipient` | 1 | 0 | 0.00% |

