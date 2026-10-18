# Stress Test Blind Evaluation Summary: batch_007

- **Date**: `2026-10-18T21:56:05.344727+00:00`
- **Git HEAD**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Batch File**: `batch_007.jsonl`
- **Model**: `rules_dialect_ml_v9` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 150
- **Correct Predictions**: 121
- **Overall Accuracy**: **80.67%**
- **Wilson 95% Confidence Interval**: `[0.7361, 0.8619]` (`[73.61%, 86.19%]`)
- **Average Latency**: 3.81 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 11 | 9 | 81.82% |
| `agent_dispute` | 11 | 10 | 90.91% |
| `app_bug` | 11 | 7 | 63.64% |
| `balance_or_statement_inquiry` | 11 | 9 | 81.82% |
| `bill_payment_failure` | 11 | 9 | 81.82% |
| `card_issue` | 11 | 10 | 90.91% |
| `failed_transfer` | 11 | 9 | 81.82% |
| `fraud_report` | 11 | 9 | 81.82% |
| `general_inquiry` | 10 | 4 | 40.00% |
| `kyc_document_issue` | 10 | 9 | 90.00% |
| `login_problem` | 11 | 8 | 72.73% |
| `refund_status` | 11 | 10 | 90.91% |
| `unclear_or_incomplete` | 9 | 8 | 88.89% |
| `wrong_recipient` | 11 | 10 | 90.91% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 145 | 118 | 81.38% |
| `True` | 5 | 3 | 60.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 148 | 121 | 81.76% |
| `prompt_injection` | 2 | 0 | 0.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 24 | 15 | 62.50% |
| `baghdadi` | 19 | 14 | 73.68% |
| `basrawi` | 32 | 28 | 87.50% |
| `mixed` | 35 | 32 | 91.43% |
| `mosul` | 40 | 32 | 80.00% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 40 | 38 | 95.00% |
| `normal` | 66 | 47 | 71.21% |
| `short` | 44 | 36 | 81.82% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 145 | 118 | 81.38% |
| `failed_transfer` | 1 | 1 | 100.00% |
| `fraud_report` | 1 | 0 | 0.00% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `refund_status` | 2 | 1 | 50.00% |

