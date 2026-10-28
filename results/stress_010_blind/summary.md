# Stress Test Blind Evaluation Summary: batch_010

- **Date**: `2026-10-20T17:09:50.418310+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_010.jsonl`
- **Model**: `rules_dialect_ml_v9` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 450
- **Correct Predictions**: 378
- **Overall Accuracy**: **84.00%**
- **Wilson 95% Confidence Interval**: `[0.8033, 0.8710]` (`[80.33%, 87.10%]`)
- **Average Latency**: 5.06 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `account_blocked` | 35 | 26 | 74.29% |
| `agent_dispute` | 29 | 27 | 93.10% |
| `app_bug` | 32 | 26 | 81.25% |
| `balance_or_statement_inquiry` | 28 | 23 | 82.14% |
| `bill_payment_failure` | 33 | 29 | 87.88% |
| `card_issue` | 32 | 32 | 100.00% |
| `failed_transfer` | 36 | 31 | 86.11% |
| `fraud_report` | 32 | 28 | 87.50% |
| `general_inquiry` | 27 | 18 | 66.67% |
| `kyc_document_issue` | 31 | 27 | 87.10% |
| `login_problem` | 35 | 32 | 91.43% |
| `refund_status` | 32 | 26 | 81.25% |
| `unclear_or_incomplete` | 33 | 21 | 63.64% |
| `wrong_recipient` | 35 | 32 | 91.43% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 450 | 378 | 84.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 445 | 376 | 84.49% |
| `prompt_injection` | 5 | 2 | 40.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 54 | 39 | 72.22% |
| `baghdadi` | 131 | 107 | 81.68% |
| `basrawi` | 110 | 97 | 88.18% |
| `mixed` | 69 | 57 | 82.61% |
| `mosul` | 86 | 78 | 90.70% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 144 | 124 | 86.11% |
| `normal` | 209 | 170 | 81.34% |
| `short` | 97 | 84 | 86.60% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 450 | 378 | 84.00% |

