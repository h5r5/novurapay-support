# Stress Test Blind Evaluation Summary: batch_009

- **Date**: `2026-10-20T15:51:49.411941+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_009.jsonl`
- **Model**: `rules_dialect_ml_v9` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 68
- **Correct Predictions**: 58
- **Overall Accuracy**: **85.29%**
- **Wilson 95% Confidence Interval**: `[0.7500, 0.9181]` (`[75.00%, 91.81%]`)
- **Average Latency**: 5.20 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 5 | 4 | 80.00% |
| `agent_dispute` | 5 | 4 | 80.00% |
| `app_bug` | 5 | 4 | 80.00% |
| `balance_or_statement_inquiry` | 5 | 3 | 60.00% |
| `bill_payment_failure` | 5 | 4 | 80.00% |
| `card_issue` | 5 | 5 | 100.00% |
| `failed_transfer` | 5 | 5 | 100.00% |
| `fraud_report` | 5 | 4 | 80.00% |
| `general_inquiry` | 5 | 3 | 60.00% |
| `kyc_document_issue` | 5 | 5 | 100.00% |
| `login_problem` | 5 | 5 | 100.00% |
| `refund_status` | 5 | 4 | 80.00% |
| `unclear_or_incomplete` | 3 | 3 | 100.00% |
| `wrong_recipient` | 5 | 5 | 100.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 66 | 57 | 86.36% |
| `True` | 2 | 1 | 50.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 64 | 57 | 89.06% |
| `prompt_injection` | 4 | 1 | 25.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 11 | 8 | 72.73% |
| `baghdadi` | 22 | 19 | 86.36% |
| `basrawi` | 13 | 13 | 100.00% |
| `mixed` | 12 | 8 | 66.67% |
| `mosul` | 10 | 10 | 100.00% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 21 | 20 | 95.24% |
| `normal` | 35 | 29 | 82.86% |
| `short` | 12 | 9 | 75.00% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 62 | 53 | 85.48% |
| `account_blocked` | 1 | 1 | 100.00% |
| `app_bug` | 3 | 2 | 66.67% |
| `kyc_document_issue` | 1 | 1 | 100.00% |
| `refund_status` | 1 | 1 | 100.00% |

