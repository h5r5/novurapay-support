# Stress Test Blind Evaluation Summary: batch_011

- **Date**: `2026-10-26T09:58:29.843410+00:00`
- **Git HEAD**: `644ed6cfd460aa67ac3dd64d1d425598716ec879`
- **Batch File**: `batch_011.jsonl`
- **Model**: `rules_dialect_ml_v10` (Offline dev-trained Rules + ML)
- **Provider**: `mock` (Strictly offline, zero API calls)

## Overall Performance

- **Total Tickets**: 4
- **Correct Predictions**: 4
- **Overall Accuracy**: **100.00%**
- **Wilson 95% Confidence Interval**: `[0.5101, 1.0000]` (`[51.01%, 100.00%]`)
- **Average Latency**: 7.78 ms
- **Degraded Classifications**: 0
- **Errors**: 0

## Per-Category Recall

| Category | Total (Gold) | Correct | Recall |
|---|---|---|---|
| `balance_or_statement_inquiry` | 1 | 1 | 100.00% |
| `bill_payment_failure` | 1 | 1 | 100.00% |
| `fraud_report` | 1 | 1 | 100.00% |
| `refund_status` | 1 | 1 | 100.00% |

## Per-Tag Slice Performance

### Slice: `ambiguous`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `False` | 4 | 4 | 100.00% |

### Slice: `attack_type`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 4 | 4 | 100.00% |

### Slice: `dialect`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `arabizi` | 1 | 1 | 100.00% |
| `baghdadi` | 3 | 3 | 100.00% |

### Slice: `length_bucket`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `long` | 1 | 1 | 100.00% |
| `normal` | 2 | 2 | 100.00% |
| `short` | 1 | 1 | 100.00% |

### Slice: `secondary_hint`

| Tag Value | Total | Correct | Accuracy |
|---|---|---|---|
| `None` | 2 | 2 | 100.00% |
| `account_blocked` | 1 | 1 | 100.00% |
| `fraud_report` | 1 | 1 | 100.00% |

