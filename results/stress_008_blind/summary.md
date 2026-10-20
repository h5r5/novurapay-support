# Stress Test Blind Evaluation Summary: batch_008

- **Date**: `2026-10-19T22:53:36.585953+00:00`
- **Git HEAD**: `f0ceaaa9e3a9ba84ced4c59fca078c366ca1439b`
- **Batch File**: `batch_008.jsonl`
- **Model**: `rules_dialect_ml_v9` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 198
- **Correct Predictions**: 150
- **Overall Accuracy**: **75.76%**
- **Wilson 95% Confidence Interval**: `[0.6933, 0.8120]` (`[69.33%, 81.20%]`)
- **Average Latency**: 4.15 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 20 | 16 | 80.00% |
| `agent_dispute` | 12 | 9 | 75.00% |
| `app_bug` | 22 | 18 | 81.82% |
| `balance_or_statement_inquiry` | 12 | 11 | 91.67% |
| `bill_payment_failure` | 12 | 11 | 91.67% |
| `card_issue` | 12 | 9 | 75.00% |
| `failed_transfer` | 12 | 11 | 91.67% |
| `fraud_report` | 12 | 6 | 50.00% |
| `general_inquiry` | 14 | 8 | 57.14% |
| `kyc_document_issue` | 12 | 8 | 66.67% |
| `login_problem` | 20 | 14 | 70.00% |
| `refund_status` | 12 | 9 | 75.00% |
| `unclear_or_incomplete` | 14 | 12 | 85.71% |
| `wrong_recipient` | 12 | 8 | 66.67% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 192 | 145 | 75.52% |
| `True` | 6 | 5 | 83.33% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 185 | 144 | 77.84% |
| `prompt_injection` | 13 | 6 | 46.15% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 32 | 26 | 81.25% |
| `baghdadi` | 62 | 41 | 66.13% |
| `basrawi` | 35 | 27 | 77.14% |
| `mixed` | 39 | 33 | 84.62% |
| `mosul` | 30 | 23 | 76.67% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 56 | 45 | 80.36% |
| `normal` | 98 | 70 | 71.43% |
| `short` | 44 | 35 | 79.55% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 182 | 139 | 76.37% |
| `account_blocked` | 3 | 1 | 33.33% |
| `app_bug` | 2 | 2 | 100.00% |
| `card_issue` | 1 | 0 | 0.00% |
| `failed_transfer` | 2 | 2 | 100.00% |
| `fraud_report` | 2 | 1 | 50.00% |
| `kyc_document_issue` | 2 | 2 | 100.00% |
| `refund_status` | 4 | 3 | 75.00% |

