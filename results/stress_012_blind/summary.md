# Stress Test Blind Evaluation Summary: batch_012

- **Date**: `2026-10-26T10:03:19.117211+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_012.jsonl`
- **Model**: `rules_dialect_ml_v10` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 200
- **Correct Predictions**: 136
- **Overall Accuracy**: **68.00%**
- **Wilson 95% Confidence Interval**: `[0.6125, 0.7407]` (`[61.25%, 74.07%]`)
- **Average Latency**: 4.74 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 14 | 8 | 57.14% |
| `agent_dispute` | 14 | 14 | 100.00% |
| `app_bug` | 14 | 10 | 71.43% |
| `balance_or_statement_inquiry` | 14 | 10 | 71.43% |
| `bill_payment_failure` | 14 | 8 | 57.14% |
| `card_issue` | 14 | 11 | 78.57% |
| `failed_transfer` | 14 | 7 | 50.00% |
| `fraud_report` | 14 | 8 | 57.14% |
| `general_inquiry` | 14 | 11 | 78.57% |
| `kyc_document_issue` | 14 | 8 | 57.14% |
| `login_problem` | 14 | 10 | 71.43% |
| `refund_status` | 14 | 5 | 35.71% |
| `unclear_or_incomplete` | 18 | 16 | 88.89% |
| `wrong_recipient` | 14 | 10 | 71.43% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 194 | 133 | 68.56% |
| `True` | 6 | 3 | 50.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 190 | 130 | 68.42% |
| `prompt_injection` | 10 | 6 | 60.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 29 | 17 | 58.62% |
| `baghdadi` | 70 | 47 | 67.14% |
| `basrawi` | 41 | 30 | 73.17% |
| `mixed` | 33 | 23 | 69.70% |
| `mosul` | 27 | 19 | 70.37% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 61 | 40 | 65.57% |
| `normal` | 101 | 66 | 65.35% |
| `short` | 38 | 30 | 78.95% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 184 | 128 | 69.57% |
| `account_blocked` | 2 | 2 | 100.00% |
| `app_bug` | 2 | 2 | 100.00% |
| `bill_payment_failure` | 1 | 0 | 0.00% |
| `failed_transfer` | 2 | 1 | 50.00% |
| `fraud_report` | 1 | 1 | 100.00% |
| `general_inquiry` | 1 | 1 | 100.00% |
| `kyc_document_issue` | 1 | 0 | 0.00% |
| `login_problem` | 1 | 0 | 0.00% |
| `refund_status` | 5 | 1 | 20.00% |

