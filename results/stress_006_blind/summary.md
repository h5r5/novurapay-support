# Stress Test Blind Evaluation Summary: batch_006

- **Date**: `2026-10-18T21:05:43.843454+00:00`
- **Git HEAD**: `e4874d2afecf35b4d5ae4d098e27b961040ac6e1`
- **Batch File**: `batch_006.jsonl`
- **Model**: `rules_dialect_ml_v7` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 150
- **Correct Predictions**: 109
- **Overall Accuracy**: **72.67%**
- **Wilson 95% Confidence Interval**: `[0.6504, 0.7917]` (`[65.04%, 79.17%]`)
- **Average Latency**: 2.74 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 10 | 7 | 70.00% |
| `agent_dispute` | 10 | 8 | 80.00% |
| `app_bug` | 15 | 8 | 53.33% |
| `balance_or_statement_inquiry` | 10 | 7 | 70.00% |
| `bill_payment_failure` | 10 | 8 | 80.00% |
| `card_issue` | 10 | 9 | 90.00% |
| `failed_transfer` | 12 | 11 | 91.67% |
| `fraud_report` | 10 | 9 | 90.00% |
| `general_inquiry` | 9 | 5 | 55.56% |
| `kyc_document_issue` | 10 | 8 | 80.00% |
| `login_problem` | 15 | 10 | 66.67% |
| `refund_status` | 10 | 8 | 80.00% |
| `unclear_or_incomplete` | 9 | 8 | 88.89% |
| `wrong_recipient` | 10 | 3 | 30.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 145 | 108 | 74.48% |
| `True` | 5 | 1 | 20.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 147 | 109 | 74.15% |
| `prompt_injection` | 3 | 0 | 0.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 27 | 15 | 55.56% |
| `baghdadi` | 37 | 27 | 72.97% |
| `basrawi` | 35 | 29 | 82.86% |
| `mixed` | 35 | 24 | 68.57% |
| `mosul` | 16 | 14 | 87.50% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 32 | 28 | 87.50% |
| `normal` | 76 | 50 | 65.79% |
| `short` | 42 | 31 | 73.81% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 145 | 108 | 74.48% |
| `failed_transfer` | 1 | 0 | 0.00% |
| `fraud_report` | 1 | 0 | 0.00% |
| `kyc_document_issue` | 2 | 0 | 0.00% |
| `refund_status` | 1 | 1 | 100.00% |

